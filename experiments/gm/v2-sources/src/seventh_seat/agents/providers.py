"""Provider wire adapters, E-010. No SDK automatic retries or hosted tools."""
import copy
from dataclasses import dataclass

from .tools import SYSTEM, definitions

MODELS = {"openai": "gpt-6-luna", "anthropic": "claude-haiku-5-5"}


@dataclass
class Reply:
    calls: list
    category: str
    details: object = None


class InfrastructureError(RuntimeError):
    def __init__(self, kind, status=None, retryable=True):
        super().__init__(kind)  # Never include request headers, credentials or SDK body.
        self.kind, self.status, self.retryable = kind, status, retryable


def wire_messages(history):
    """Anthropic wire copy of an append-only history. Tool results followed by the
    next observation become one user turn (tool results first, then the text), so
    the request never carries consecutive user turns. History itself is unchanged."""
    out = []
    for m in copy.deepcopy(history):
        prev = out[-1] if out else None
        if (prev and prev["role"] == "user" == m["role"] and isinstance(prev["content"], list)
                and isinstance(m["content"], str)):
            prev["content"].append({"type": "text", "text": m["content"]})
        else:
            out.append(m)
    return out


class Adapter:
    def __init__(self, provider, max_tokens=2048, tools=None):
        if provider not in MODELS or not 128 <= max_tokens <= 16384:
            raise ValueError("unsupported provider or output limit")
        self.provider, self.model, self.max_tokens = provider, MODELS[provider], max_tokens
        # tools=None: the E-004 world tools. GM probes may pass a fixed alternative list.
        self.tools = copy.deepcopy(tools) if tools is not None else None
        self.history = []

    def observe(self, text):
        self.history.append({"role": "user", "content": text})

    def request(self):
        defs = definitions() if self.tools is None else copy.deepcopy(self.tools)
        if self.provider == "openai":
            return {"model": self.model, "instructions": SYSTEM, "input": copy.deepcopy(self.history),
                    "reasoning": {"effort": "medium"}, "store": False,
                    "include": ["reasoning.encrypted_content"], "max_output_tokens": self.max_tokens,
                    "tools": [{"type": "function", **d, "strict": True} for d in defs]}
        return {"model": self.model, "system": SYSTEM, "messages": wire_messages(self.history),
                "thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"},
                "max_tokens": self.max_tokens,
                "tools": [{"name": d["name"], "description": d["description"],
                           "input_schema": d["parameters"]} for d in defs]}

    def receive(self, response):
        if self.provider == "openai":
            blocks = response.get("output", [])
            self.history.extend(copy.deepcopy(blocks))
            calls = [{"id": b["call_id"], "name": b["name"], "arguments": b["arguments"]}
                     for b in blocks if b.get("type") == "function_call"]
            refusal = [c for b in blocks for c in b.get("content", []) if c.get("type") == "refusal"]
            if refusal or (response.get("incomplete_details") or {}).get("reason") == "content_filter":
                return Reply(calls, "provider_refusal", refusal or response["incomplete_details"])
            if response.get("status") == "incomplete":
                return Reply(calls, "truncation", response.get("incomplete_details"))
            if response.get("status") != "completed":
                raise InfrastructureError("unexpected_response_status", retryable=False)
        else:
            blocks = response.get("content", [])
            self.history.append({"role": "assistant", "content": copy.deepcopy(blocks)})
            calls = [{"id": b["id"], "name": b["name"], "arguments": b["input"]}
                     for b in blocks if b.get("type") == "tool_use"]
            stop = response.get("stop_reason")
            if stop == "refusal":
                return Reply(calls, "provider_refusal", response.get("stop_details"))
            if stop in ("max_tokens", "model_context_window_exceeded"):
                return Reply(calls, "truncation", stop)
            if stop not in ("end_turn", "tool_use", "stop_sequence", "pause_turn"):
                raise InfrastructureError("unexpected_stop_reason", retryable=False)
            if stop == "pause_turn":
                return Reply(calls, "continuation", stop)
        return Reply(calls, "tool_calls" if calls else "model_abstention")

    def results(self, results):
        # All parallel results together, in call order, before another user turn.
        if not results:
            return
        from ..world.events import canonical
        if self.provider == "openai":
            self.history.extend({"type": "function_call_output", "call_id": cid,
                                 "output": canonical(result)} for cid, result in results)
        else:
            self.history.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": cid, "content": canonical(result),
                 "is_error": not result.get("ok", False)} for cid, result in results]})


def rate_limit_headers(headers):
    """Account limits as the provider reports them; no credentials or bodies."""
    keep = ("ratelimit", "retry-after", "request-id")
    try:
        return {k.lower(): str(v) for k, v in dict(headers).items() if any(x in k.lower() for x in keep)}
    except Exception:
        return None


class SDKTransport:
    def __init__(self, provider, api_key):
        self.provider = provider
        if provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1", max_retries=0, timeout=45)
        else:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key, base_url="https://api.anthropic.com", max_retries=0, timeout=45)

    def __call__(self, request):
        self.last_rate_limits = None
        try:
            api = self.client.responses if self.provider == "openai" else self.client.messages
            raw = api.with_raw_response.create(**request)
            self.last_rate_limits = rate_limit_headers(raw.headers)
            return raw.parse().model_dump(mode="json", exclude_none=True)
        except Exception as exc:
            response = getattr(exc, "response", None)
            if response is not None:
                self.last_rate_limits = rate_limit_headers(getattr(response, "headers", {}))
            status = getattr(exc, "status_code", None)
            transient = status in (408, 409, 429) or (isinstance(status, int) and status >= 500)
            transient |= type(exc).__name__ in ("APIConnectionError", "APITimeoutError")
            raise InfrastructureError(type(exc).__name__, status, transient) from None

    def close(self):
        self.client.close()
