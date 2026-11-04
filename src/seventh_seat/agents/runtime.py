"""Bounded provider calls, local response replay and deterministic episode driving."""
import copy
import time
from collections import Counter

from .providers import Adapter, InfrastructureError
from .storage import BudgetStop, CacheMiss
from .tools import dispatch, parse_arguments
from ..world.engine import Engine
from ..world.events import canonical, sha256_hex
from ..world.params import District, Scenario


def reservation(provider, max_tokens):
    # Reserve the FULL advertised context (rounded up), at the highest input/cache
    # and long-context rates. No tokenizer estimate or hidden-reasoning guess.
    # USD nanodollars/token: $1/MTok = 1000. Rates verified 2026-11-03.
    return (1_100_000 * (250 if provider == "openai" else 1000)
            + max_tokens * (750 if provider == "openai" else 2500))


def cost(provider, response):
    u = response["usage"]
    def count(value):
        if type(value) is not int or value < 0:
            raise ValueError("invalid token usage")
        return value
    inp, out = count(u["input_tokens"]), count(u["output_tokens"])
    if provider == "openai":
        details = u.get("input_tokens_details") or {}
        cached = count(details.get("cached_tokens", 0))
        writes = count(details.get("cache_write_tokens", 0))
        if cached + writes > inp:
            raise ValueError("inconsistent input usage")
        long = inp > 272000
        # If provider does not itemize cache writes, conservatively charge all
        # non-read input at the write rate. This is an upper accounting estimate.
        fresh = inp - cached - writes
        if "cache_write_tokens" not in details:
            writes, fresh = fresh, 0
        return (fresh * (200 if long else 100) + writes * (250 if long else 125)
                + cached * (20 if long else 10) + out * (750 if long else 500))
    read = count(u.get("cache_read_input_tokens", 0))
    write = count(u.get("cache_creation_input_tokens", 0))
    long = inp + read + write > 100000
    creation = u.get("cache_creation") or {}
    short_write = count(creation.get("ephemeral_5m_input_tokens", 0))
    if short_write > write:
        raise ValueError("inconsistent cache creation usage")
    return (inp * (500 if long else 100) + read * (50 if long else 10)
            + short_write * (625 if long else 125)
            + (write - short_write) * (1000 if long else 200)
            + out * (2500 if long else 500))


class Caller:
    def __init__(self, provider, cache, budget=None, transport=None, replay=False, sleep=time.sleep):
        self.provider, self.cache, self.budget = provider, cache, budget
        self.transport, self.replay, self.sleep = transport, replay, sleep

    def call(self, request, namespace):
        key = self.cache.key(self.provider, request, namespace)
        payload = self.cache.get(key)
        if payload is not None:
            return key, payload
        if self.replay:
            raise CacheMiss(key)
        if self.budget is None or self.transport is None:
            raise ValueError("live requests require a budget and transport")
        attempts = []
        response = None
        for attempt in range(3):
            reserved = reservation(self.provider, request.get("max_tokens", request.get("max_output_tokens")))
            rid = self.budget.reserve(self.provider, "preparation", reserved)
            ledger = {"reservation_id": rid, "reserved_nanodollars": reserved}
            started = time.monotonic()
            try:
                response = self.transport(copy.deepcopy(request))
            except InfrastructureError as exc:
                detail = {"kind": exc.kind, "status": exc.status, "retryable": exc.retryable}
                self.budget.uncertain(rid, detail)
                attempts.append({"category": "infrastructure_error", "detail": detail,
                                 "latency_seconds": time.monotonic() - started,
                                 "rate_limits": getattr(self.transport, "last_rate_limits", None), **ledger})
                if not exc.retryable or attempt == 2:
                    break
                self.sleep(2)
                continue
            except BaseException:
                self.budget.uncertain(rid, {"kind": "local_interruption"})
                raise
            try:
                charge = cost(self.provider, response)
            except (KeyError, TypeError, ValueError):
                self.budget.uncertain(rid, {"kind": "missing_or_invalid_usage"})
                raise BudgetStop("cannot reconcile provider usage; reservation retained") from None
            self.budget.settle(rid, charge, {"usage": response["usage"], "model": response.get("model"),
                                          "cost_basis": "conservative published-rate estimate"})
            attempts.append({"category": "response", "latency_seconds": time.monotonic() - started,
                             "usage": response["usage"], "cost_nanodollars": charge,
                             "rate_limits": getattr(self.transport, "last_rate_limits", None), **ledger})
            break
        payload = {"request": request, "response": response, "attempts": attempts}
        self.cache.put(key, payload)
        return key, payload


def no_hazard_scenario():
    """Dedicated harness fixture, outside pilot/evaluation seeds. Not GM results.

    Total entitlement 60 <= W=70: even wasteful valid allocations cannot breach.
    Demand 48; six identical feasible district tasks, no trade needed.
    """
    return Scenario("harness-no-hazard-v1", 17, -22, "cheap", 100, 30, 1, 2,
                    tuple(District(f"D{i}", 10, 8, 5, 20) for i in range(1, 7)))


def audit(engine, actor, action, result, request=None, key=None):
    provenance = {}
    if request is not None:
        provenance = {"model": request["model"], "params": {k: v for k, v in request.items()
                      if k not in ("input", "messages", "instructions", "system", "tools")},
                      "prompt_hash": sha256_hex(canonical(request)), "cache_key": key}
    engine._log(actor, action, result=result, **provenance)


def agent_turn(engine, caller, adapter, actor, observation, namespace):
    """One agent's turn in the current phase: at most B model calls."""
    engine._log(actor, "observation", result=observation,
                view_hash=sha256_hex(canonical(observation)))
    adapter.observe(canonical(observation))
    # B calls maximum even if the provider emits no action. A provider
    # refusal, abstention or truncation ends this turn with no action.
    for turn in range(engine.B):
        if engine.attention[actor] >= engine.B:
            break
        request = adapter.request()
        key, payload = caller.call(request, {**namespace, "turn": turn})
        for attempt in payload["attempts"]:
            if attempt["category"] == "infrastructure_error":
                audit(engine, actor, "model_call", attempt, request, key)
        if payload["response"] is None:
            raise InfrastructureError("attempts_exhausted")
        response = payload["response"]
        try:
            reply = adapter.receive(response)
        except (KeyError, TypeError, InfrastructureError):
            audit(engine, actor, "model_call", {"category": "infrastructure_error",
                  "detail": "malformed_provider_response"}, request, key)
            raise InfrastructureError("malformed_provider_response", retryable=False) from None
        results = []
        if reply.category == "tool_calls":
            schema_valid = all(parse_arguments(c["name"], c["arguments"])[1] is None for c in reply.calls)
            category = "valid_action" if schema_valid else "invalid_tool_call"
            for call in reply.calls:
                result = dispatch(engine, actor, call["name"], call["arguments"])
                results.append((call["id"], result))
            if any(not r["ok"] for _, r in results):
                category = "invalid_tool_call"
        else:
            category = "truncation" if reply.category == "continuation" else reply.category
            # Resolve any complete IDs in a truncated/refused response,
            # without executing partially delivered intent.
            results = [(c["id"], {"ok": False, "reason": category + ": no action"}) for c in reply.calls]
        adapter.results(results)
        audit(engine, actor, "model_call", {"category": category, "details": reply.details,
              "tool_results": results, "usage": response.get("usage"),
              "latency_seconds": payload["attempts"][-1]["latency_seconds"],
              "response_model": response.get("model"), "response_id": response.get("id")}, request, key)
        if reply.category != "tool_calls":
            break


def drive(engine, caller, max_tokens=2048, episode_attempt=0):
    adapters = {did: Adapter(caller.provider, max_tokens) for did in engine.ids}
    engine.start()
    while not engine.state["executed"]:
        phase = engine.state["phase"]
        for actor in engine.ids:
            base = {"episode": engine.episode_id, "scenario": engine.sc.to_dict(),
                    "condition": engine.condition, "actor": actor, "phase": phase,
                    "episode_attempt": episode_attempt}
            agent_turn(engine, caller, adapters[actor], actor, engine.view(actor), base)
        engine.end_phase()
    return engine


def run_with_recovery(caller, output, episode_id="harness-smoke", max_tokens=2048,
                      scenario=None, condition="E0S0", data_status="harness-no-hazard-smoke"):
    """Pre-sprint no-hazard only. One same-seed episode rerun after infrastructure failure.

    scenario defaults to the Wednesday smoke fixture; GM passes its declared
    no-hazard worlds. Callers must never pass a calibration or evaluation scenario.
    """
    scenario = scenario or no_hazard_scenario()
    if scenario.total_entitlement > scenario.W:
        raise ValueError("run_with_recovery accepts only no-hazard worlds")
    from pathlib import Path
    root = Path(output)
    root.mkdir(parents=True, exist_ok=False)
    attempts = []
    for attempt in range(2):
        # Attempt-specific cache namespace, same engine ID/seed/order. A fresh
        # matched rerun must not replay an infrastructure failure from attempt 0.
        engine = Engine(scenario, condition=condition, episode_id=episode_id,
                        log_path=root / f"attempt-{attempt}.jsonl")
        try:
            drive(engine, caller, max_tokens, episode_attempt=attempt)
        except InfrastructureError as exc:
            attempts.append({"attempt": attempt, "status": "infrastructure_error", "kind": exc.kind,
                             "log_head": engine.log.head})
        except BudgetStop as exc:
            attempts.append({"attempt": attempt, "status": "budget_stop", "reason": str(exc), "log_head": engine.log.head})
            break
        else:
            attempts.append({"attempt": attempt, "status": "completed", "log_head": engine.log.head,
                             "state_hashes": engine.state_hashes(), "outcome": engine.outcome,
                             "call_categories": dict(Counter(r["result"]["category"] for r in engine.log.records if r["action"] == "model_call"))})
            break
    status = attempts[-1]["status"]
    if status == "infrastructure_error":
        status = "missing"
    summary = {"data_status": data_status, "qualified": False, "scenario_id": scenario.scenario_id,
               "provider": caller.provider, "episode_id": episode_id, "max_tokens": max_tokens,
               "status": status, "attempts": attempts}
    (root / "summary.json").write_text(canonical(summary) + "\n")
    return summary
