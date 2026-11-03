"""Append-only, hash-chained event record (02 §8). No wall-clock fields, so a
replay reproduces identical hashes (gate G2)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

GENESIS = "0" * 64
SCHEMA_FIELDS = (
    "episode_id", "scenario_id", "condition", "seed",
    "event_id", "phase", "step",
    "actor_id", "display_name",
    "action", "args", "authorized", "reason",
    "view_hash", "claim_text", "evidence_refs",
    "state_hash_before", "state_hash_after",
    "attention_spent", "attention_left",
    "model", "params", "prompt_hash", "cache_key",
    "result", "prev_hash", "hash",
)


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def record_hash(rec: dict) -> str:
    return sha256_hex(canonical({k: v for k, v in rec.items() if k != "hash"}))


class EventLog:
    def __init__(self, path: str | Path | None = None):
        self.records: list[dict] = []
        self.path = Path(path) if path else None
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("", encoding="utf-8")

    def append(self, **fields) -> dict:
        unknown = set(fields) - set(SCHEMA_FIELDS)
        if unknown:
            raise ValueError(f"unknown event fields: {sorted(unknown)}")
        rec = {k: fields.get(k) for k in SCHEMA_FIELDS if k not in ("event_id", "prev_hash", "hash")}
        rec["event_id"] = f"E{len(self.records):06d}"
        rec["prev_hash"] = self.records[-1]["hash"] if self.records else GENESIS
        rec["hash"] = record_hash(rec)
        self.records.append(rec)
        if self.path:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(canonical(rec) + "\n")
        return rec

    @property
    def head(self) -> str:
        return self.records[-1]["hash"] if self.records else GENESIS


def verify_records(records: list[dict]) -> tuple[bool, int | None]:
    """Returns (ok, index of first bad record)."""
    prev = GENESIS
    for i, rec in enumerate(records):
        if rec.get("prev_hash") != prev or record_hash(rec) != rec.get("hash"):
            return False, i
        prev = rec["hash"]
    return True, None


def read_jsonl(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]
