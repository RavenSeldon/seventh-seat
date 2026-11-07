"""Hazard-world runner (weekend): calibration and evaluation episodes.

Runs any world, hazard or not, in any of the four cells, with the same
recovery semantics as the pre-sprint ``run_with_recovery`` (E-010), whose
no-hazard guard is deliberately left untouched:

- at most 3 provider attempts per request with fixed backoff (inside
  ``Caller.call``); a refusal gets a no-action transition and the episode
  continues (``agent_turn``); refusal, abstention, invalid-call,
  infrastructure-error and truncation classes are counted per episode;
- one complete episode rerun from the start with the same scenario, cell and
  seed after an infrastructure interruption; a second failure is recorded as
  missing and reported; both attempts and their costs are preserved.

Cache and rerun. The cache namespace includes the attempt number, exactly as
pre-sprint: a rerun never replays attempt 0's entries, so every call of a
rerun is a fresh, recorded, paid call, and the failed attempt's entries and
event log are preserved for audit. A cached replay of a completed attempt
reproduces its log byte-identically (G2).

Budget. The pilot charges stage ``preparation``; evaluation charges stage
``evaluation``. This module never touches caps. Each episode opens its own
budget connection (sqlite transactions serialize concurrent reservations, so
headroom for in-flight requests is reserved exactly as pre-sprint).

Output. One directory per episode containing ``attempt-N.jsonl`` (the
hash-chained event logs) and ``manifest.json`` written last, atomically. A
manifest is the completion marker: an episode with a manifest is terminal
(completed or missing) and is skipped on restart. A directory with attempt
logs but no manifest marks an interrupted run; the remaining allowed attempts
are run and the interrupted attempt is preserved and labelled. A paid call is
never duplicated without a record of it.

Fixed stop. ``run_batch`` refuses to launch new episodes at or after
``stop_at`` (UTC); episodes already in flight run to completion. The
block-level launch policy (decision P-5, using measured wall times) belongs
to the evaluation driver, not here.

Concurrency. Episodes are independent, so bounded concurrency changes wall
time only. Per-episode transports, budgets and engines; the response cache
is file-based and atomic.
"""
from __future__ import annotations

import json
import hashlib
import re
import fcntl
from contextlib import contextmanager
import os
import time
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path

from .providers import MODELS, InfrastructureError
from .runtime import Caller, cost, drive
from .storage import Budget, BudgetStop, ResponseCache
from .tools import SYSTEM, definitions
from ..interventions import build_hooks
from ..world.engine import Engine
from ..world.events import canonical, read_jsonl, sha256_hex, verify_records
from ..world.params import CELLS

PROVIDER = "openai"        # gm-v2 selection; never switched after outcomes (E-010c)
MAX_TOKENS = 4096          # closed GM configuration (D-025 to D-027)
STAGES = ("preparation", "evaluation")


def utcnow():
    return datetime.now(timezone.utc)


def episode_manifest(ep_dir):
    path = Path(ep_dir) / "manifest.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _write_atomic(path, payload):
    tmp = path.with_suffix(".tmp")
    with tmp.open("w") as f:
        f.write(canonical(payload) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _attempt_record(log_path, provider, status, wall_seconds=None, **extra):
    """Summarize one attempt from its event log alone (no hand-computed numbers)."""
    # Flush the event file before publishing a durable completion marker.
    with log_path.open("rb") as log_file:
        os.fsync(log_file.fileno())
    records = read_jsonl(log_path)
    categories = Counter()
    accounted = 0
    for r in records:
        if r["action"] != "model_call":
            continue
        result = r.get("result") or {}
        categories[result.get("category", "unknown")] += 1
        if result.get("usage") is not None:
            accounted += cost(provider, {"usage": result["usage"]})
        elif result.get("reserved_nanodollars") is not None:
            accounted += result["reserved_nanodollars"]   # uncertain: reservation retained
    ok, bad = verify_records(records)
    if not ok:
        raise ValueError(f"event chain broken at record {bad} in {log_path}")
    head = records[-1]["hash"] if records else None
    executed = [r for r in records if r["action"] == "season_executed"]
    rec = {"attempt": int(log_path.stem.split("-")[1]), "status": status,
           "log": log_path.name, "log_head": head,
           "state_sequence_sha256": sha256_hex(canonical(
               [r["state_hash_after"] for r in records])),
           "call_categories": dict(categories),
           "accounted_cost_nanodollars": accounted}
    if executed:
        rec["outcome"] = executed[0]["result"]
    if wall_seconds is not None:
        rec["wall_seconds"] = wall_seconds
    rec.update(extra)
    return rec



@contextmanager
def _lease(directory):
    """Kernel releases the writer lock on process exit, including crashes."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".writer.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("another writer owns this run directory") from None
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def _bind(path, contract):
    if path.exists():
        if json.loads(path.read_text()) != contract:
            raise ValueError("run contract differs; refusing to reuse recorded work")
    else:
        _write_atomic(path, contract)


def _safe_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
        raise ValueError("episode_id must be a safe single path component")


def _verify_identity(records, scenario, condition, episode_id):
    for rec in records:
        if any(rec.get(k) != v for k, v in {
            "episode_id": episode_id, "scenario_id": scenario.scenario_id,
            "condition": condition, "seed": scenario.seed}.items()):
            raise ValueError("event identity differs from requested episode")
    if records:
        starts = [rec for rec in records if rec["action"] == "episode_start"]
        if len(starts) != 1 or canonical(starts[0]["args"]["scenario"]) != canonical(scenario.to_dict()):
            raise ValueError("scenario differs from recorded episode")


def run_episode(ep_dir, scenario, condition, stage, provider, caller_factory,
                max_tokens=MAX_TOKENS, sleep=time.sleep):
    with _lease(ep_dir):
        return _run_episode(ep_dir, scenario, condition, stage, provider,
                            caller_factory, max_tokens, sleep)


def _run_episode(ep_dir, scenario, condition, stage, provider, caller_factory,
                max_tokens=MAX_TOKENS, sleep=time.sleep):
    """Run one episode with E-010 recovery. Returns (manifest, ran_new_work)."""
    if condition not in CELLS:
        raise ValueError(f"unknown cell: {condition}")
    if stage not in STAGES:
        raise ValueError(f"unknown budget stage: {stage}")
    ep_dir = Path(ep_dir)
    ep_dir.mkdir(parents=True, exist_ok=True)
    _safe_id(ep_dir.name)
    if provider != PROVIDER or max_tokens != MAX_TOKENS:
        raise ValueError("evaluation uses the closed gm-v2 configuration")
    source_root = Path(__file__).resolve().parents[1]
    implementation = {str(p.relative_to(source_root)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(source_root.rglob("*.py"))}
    contract = {"implementation_sha256": implementation, "scenario": scenario.to_dict(), "condition": condition, "stage": stage,
                "provider": provider, "max_tokens": max_tokens,
                "system_hash": sha256_hex(SYSTEM),
                "tools_hash": sha256_hex(canonical(definitions(condition)))}
    # JSON round trip normalizes dataclass tuples before equality checks.
    _bind(ep_dir / "contract.json", json.loads(canonical(contract)))
    paths = sorted(ep_dir.glob("attempt-*.jsonl"))
    if [p.name for p in paths] != [f"attempt-{i}.jsonl" for i in range(len(paths))] or len(paths) > 2:
        raise ValueError("noncontiguous or excess attempt logs; inspect before continuing")
    for path in paths:
        _verify_identity(read_jsonl(path), scenario, condition, ep_dir.name)
    existing = episode_manifest(ep_dir)
    if existing is not None:
        for key, value in {"scenario_id": scenario.scenario_id, "condition": condition,
                           "seed": scenario.seed, "stage": stage, "provider": provider}.items():
            if existing.get(key) != value:
                raise ValueError("manifest identity differs from requested episode")
        for attempt in existing["attempts"]:
            actual = _attempt_record(ep_dir / attempt["log"], provider, attempt["status"])
            if actual["log_head"] != attempt["log_head"]:
                raise ValueError("manifest log head mismatch")
        return existing, False                      # terminal; never redone
    episode_id = ep_dir.name
    attempts = [_attempt_record(p, provider, "interrupted", resumed=True)
                for p in paths]
    status = None
    for i, attempt_rec in enumerate(attempts):
        if "outcome" in attempt_rec:
            if i != len(attempts) - 1:
                raise ValueError("an executed attempt must not have a later attempt")
            attempt_rec["status"] = "completed"
            status = "completed"  # crash after execution, before manifest publication
    for attempt in range(len(attempts), 2) if status is None else ():         # one rerun at most (E-010)
        engine = Engine(scenario, condition=condition, episode_id=episode_id,
                        log_path=ep_dir / f"attempt-{attempt}.jsonl", **build_hooks(condition))
        caller = caller_factory()
        started = time.monotonic()
        try:
            drive(engine, caller, max_tokens, episode_attempt=attempt,
                  namespace={"stage": stage})
        except InfrastructureError as exc:
            attempts.append(_attempt_record(
                ep_dir / f"attempt-{attempt}.jsonl", provider, "infrastructure_error",
                wall_seconds=time.monotonic() - started, kind=exc.kind))
            continue
        except BudgetStop as exc:
            attempts.append(_attempt_record(
                ep_dir / f"attempt-{attempt}.jsonl", provider, "budget_stop",
                wall_seconds=time.monotonic() - started, reason=str(exc)))
            status = "budget_stop"
            break
        except Exception as exc:
            attempts.append(_attempt_record(
                ep_dir / f"attempt-{attempt}.jsonl", provider, "infrastructure_error",
                wall_seconds=time.monotonic() - started, kind="harness_" + type(exc).__name__))
            continue
        finally:
            if caller.budget is not None:
                caller.budget.close()
            close = getattr(caller.transport, "close", None)
            if close is not None:
                close()
        attempts.append(_attempt_record(
            ep_dir / f"attempt-{attempt}.jsonl", provider, "completed",
            wall_seconds=time.monotonic() - started))
        status = "completed"
        break
    if status is None:
        status = "missing"                          # second failure: recorded, reported
    manifest = {
        "episode_id": episode_id, "scenario_id": scenario.scenario_id,
        "condition": condition, "seed": scenario.seed, "stratum": scenario.stratum,
        "kappa": scenario.kappa, "stage": stage, "status": status,
        "provider": provider, "model": MODELS[provider],
        "model_configuration": {"reasoning_effort": "medium", "temperature": None,
                                "max_output_tokens": max_tokens},
        "system_hash": sha256_hex(SYSTEM),
        "tools_hash": sha256_hex(canonical(definitions(condition))),
        "attempts": attempts,
        "accounted_cost_nanodollars": sum(a.get("accounted_cost_nanodollars", 0) for a in attempts),
        "cost_note": "Event-recorded accounting only; shared budget ledger is authoritative, including reservations lost before event logging.",
        "updated_utc": utcnow().isoformat(timespec="seconds"),
    }
    if status == "completed":
        manifest["outcome"] = attempts[-1]["outcome"]
    _write_atomic(ep_dir / "manifest.json", manifest)
    return manifest, True


def run_batch(worklist, run_dir, **kwargs):
    with _lease(run_dir):
        return _run_batch(worklist, run_dir, **kwargs)


def _run_batch(worklist, run_dir, *, stage, ledger_path, caps, transport_factory,
              provider=PROVIDER, max_workers=1, stop_at=None, max_tokens=MAX_TOKENS,
              sleep=time.sleep):
    """Run an ordered worklist with bounded concurrency, resume and a fixed stop.

    worklist: [{"episode_id", "scenario", "condition"}, ...]. Writes index.json
    atomically after every episode. Returns the index."""
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")
    worklist = list(worklist)
    ids = [item["episode_id"] for item in worklist]
    for eid in ids:
        _safe_id(eid)
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate episode IDs")
    if stop_at is not None and stop_at.utcoffset() is None:
        raise ValueError("stop_at must be timezone aware")
    if stage not in STAGES or provider != PROVIDER or max_tokens != MAX_TOKENS:
        raise ValueError("invalid stage or closed model configuration")
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    _bind(run_dir / "batch-contract.json", {
        "stage": stage, "provider": provider, "max_tokens": max_tokens,
        "stop_at": stop_at.isoformat() if stop_at else None,
        "ledger": str(Path(ledger_path).resolve()),
        "worklist": [{**item, "scenario": json.loads(canonical(item["scenario"].to_dict()))}
                     for item in worklist]})
    cache = ResponseCache(run_dir / "cache")
    index_path = run_dir / "index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text())
        index["resumed"] = True                 # process restart: skip terminal episodes
    else:
        index = {"stage": stage, "provider": provider, "model": MODELS[provider],
                 "max_tokens": max_tokens, "max_workers": max_workers,
                 "stop_at": stop_at.isoformat(timespec="seconds") if stop_at else None,
                 "ledger": str(ledger_path), "episodes": {}}

    def factory():    # one budget connection and transport per episode thread
        budget = Budget(ledger_path, caps)
        try:
            transport = transport_factory()
        except BaseException:
            budget.close()
            raise
        return Caller(provider, cache, budget, transport, sleep=sleep, stage=stage)

    def record(item, manifest, skipped):
        entry = {"status": manifest["status"], "scenario_id": manifest["scenario_id"],
                 "condition": manifest["condition"], "seed": manifest["seed"],
                 "stratum": manifest["stratum"], "attempts": len(manifest["attempts"]),
                 "accounted_cost_nanodollars": manifest["accounted_cost_nanodollars"],
                 "dir": str(Path("episodes") / item["episode_id"])}
        if skipped:
            entry["skipped"] = "manifest exists; terminal"
        index["episodes"][item["episode_id"]] = entry
        _finish(index, index_path)
        return entry

    def _finish(idx, path):
        counts = Counter(e["status"] for e in idx["episodes"].values())
        idx["totals"] = dict(counts)
        idx["totals"]["accounted_cost_nanodollars"] = sum(
            e.get("accounted_cost_nanodollars", 0) for e in idx["episodes"].values())
        idx["updated_utc"] = utcnow().isoformat(timespec="seconds")
        _write_atomic(path, idx)

    pending = list(worklist)
    futures = {}
    halt = None
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        while pending or futures:
            while pending and len(futures) < max_workers and halt is None:
                item = pending.pop(0)
                ep_dir = run_dir / "episodes" / item["episode_id"]
                if episode_manifest(ep_dir) is not None:
                    record(item, run_episode(ep_dir, item["scenario"], item["condition"],
                                             stage, provider, factory, max_tokens, sleep)[0],
                           skipped=True)
                    continue
                if stop_at is not None and utcnow() >= stop_at:
                    halt = "fixed stop reached"
                    index["episodes"][item["episode_id"]] = {
                        "status": "not_launched", "reason": halt,
                        "scenario_id": item["scenario"].scenario_id,
                        "condition": item["condition"]}
                    continue
                futures[pool.submit(run_episode, ep_dir, item["scenario"], item["condition"],
                                    stage, provider, factory, max_tokens, sleep)] = item
            if not futures:
                break
            done, _ = wait(tuple(futures), return_when=FIRST_COMPLETED)
            for fut in done:
                item = futures.pop(fut)
                manifest, _ = fut.result()
                record(item, manifest, skipped=False)
                if manifest["status"] == "budget_stop":
                    halt = "budget stop"
    for item in pending:                    # halted: remaining work is not launched
        index["episodes"][item["episode_id"]] = {
            "status": "not_launched", "reason": halt,
            "scenario_id": item["scenario"].scenario_id, "condition": item["condition"]}
    if halt:
        index["halted"] = halt
    _finish(index, index_path)
    return index
