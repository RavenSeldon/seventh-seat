"""Declared calibration, lock preparation and blocked evaluation orchestration.

All source/configuration declarations are immutable. This module cannot create
Git tags, publish a result, change a cap or tune a model after seeing outcomes.
"""
from __future__ import annotations

import hashlib
import json
import random
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from .agents.evalrunner import (run_batch, _write_atomic, _bind, _lease,
                                utcnow, MAX_TOKENS, PROVIDER)
from .agents.providers import MODELS
from .agents.storage import Budget, NANO
from .agents.tools import SYSTEM, definitions
from .analysis.contrasts import DEFAULT_BOOTSTRAP_SEED
from .analysis.run import load_episode
from .world.events import canonical, sha256_hex
from .world.params import CELLS, KAPPA_STEPS
from .world.scenario import generate, assign_strata

ROOT = Path(__file__).resolve().parents[2]
CAPS = {"total": 66, "preparation": 20, "openai": 33, "anthropic": 33}
STOP_AT = datetime(2026, 11, 8, 6, tzinfo=timezone.utc)
ORDER_SEED = "seventh-seat/cell-order/v1"
PILOT_SEEDS = list(range(1000, 1008))
EVAL_SEEDS = list(range(2000, 2024))  # 24 scenarios, exactly balanced strata


def source_hashes():
    files = sorted((ROOT / "src/seventh_seat").rglob("*.py"))
    files += [ROOT / "docs/03_PREREGISTRATION.md", ROOT / "docs/ERRATA.md"]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def initialize_budget(path, historical):
    """Carry the actual historical charges forward, preserving their IDs.

    Never imports dry-run/synthetic ledgers. Caller names the original live
    ledger explicitly. Original ledger is read-only and remains unchanged.
    """
    path, historical = Path(path).resolve(), Path(historical).resolve()
    if not historical.is_file() or path.resolve() == historical.resolve():
        raise ValueError("a distinct existing historical ledger is required")
    old = sqlite3.connect(historical.as_uri() + "?mode=ro", uri=True)
    try:
        rows = old.execute("SELECT id,provider,stage,reserved,actual,status,detail FROM charges ORDER BY id").fetchall()
    finally:
        old.close()
    if not rows or any(r[5] != "settled" for r in rows):
        raise ValueError("historical live ledger must contain settled charges only")
    receipt = {"source": str(historical.resolve()), "charges": len(rows),
               "charges_sha256": sha256_hex(canonical(rows)),
               "historical_nanodollars": sum(r[4] for r in rows), "caps_usd": CAPS}
    receipt_path = path.with_suffix(".import.json")
    if receipt_path.exists() and json.loads(receipt_path.read_text()) != receipt:
        raise ValueError("historical ledger changed after import; reconcile before calls")
    budget = Budget(path, CAPS)
    try:
        with budget.transaction():
            for row in rows:
                existing = budget.db.execute("SELECT id,provider,stage,reserved,actual,status,detail FROM charges WHERE id=?", (row[0],)).fetchone()
                if existing is not None and existing != row:
                    raise ValueError("historical charge ID conflict")
                budget.db.execute("INSERT OR IGNORE INTO charges VALUES (?,?,?,?,?,?,?)", row)
        receipt = {"source": str(historical.resolve()), "charges": len(rows),
                   "charges_sha256": sha256_hex(canonical(rows)),
                   "historical_nanodollars": sum(r[4] for r in rows), "caps_usd": CAPS}
        _bind(path.with_suffix(".import.json"), receipt)
        return budget.summary()
    finally:
        budget.close()


def declare_pilot(root, *, data_status="experimental"):
    if data_status not in ("experimental", "scripted-fixture"):
        raise ValueError("unknown data status")
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    mapping = assign_strata(PILOT_SEEDS)
    declaration = {"kind": "calibration", "data_status": data_status,
        "provider": PROVIDER, "model": MODELS[PROVIDER], "max_tokens": MAX_TOKENS,
        "reasoning_effort": "medium", "temperature": None, "caps_usd": CAPS,
        "seeds": PILOT_SEEDS, "strata": {str(k): v for k, v in mapping.items()},
        "kappa_levels": list(KAPPA_STEPS), "initial_kappa": 14,
        "maximum_adjustments": 3, "source_hashes": source_hashes(),
        "system_hash": sha256_hex(SYSTEM),
        "tools_hashes": {c: sha256_hex(canonical(definitions(c))) for c in CELLS},
        "stop_at": STOP_AT.isoformat()}
    _bind(root / "declaration.json", declaration)
    return declaration


def calibration_step(history):
    """Pure E-014 decision from complete eight-episode batches only."""
    if not history:
        return {"status": "continue", "next_kappa": 14}
    batch = history[-1]
    if batch["evaluable"] != 8:
        return {"status": "incomplete", "reason": "eight evaluable pilot episodes required"}
    kappa, breaches = batch["kappa"], batch["breaches"]
    if type(breaches) is not int or not 0 <= breaches <= 8:
        raise ValueError("invalid breach count")
    if 3 <= breaches <= 6:
        return {"status": "accepted", "kappa": kappa, "confirmatory": True}
    direction = 1 if breaches < 3 else -1
    idx = KAPPA_STEPS.index(kappa) + direction
    why = None
    if len(history) >= 4:
        why = "maximum_adjustments"
    elif not 0 <= idx < len(KAPPA_STEPS):
        why = "endpoint"
    elif KAPPA_STEPS[idx] in [b["kappa"] for b in history]:
        why = "would_revisit"
    if why:
        return {"status": "outside_target", "reason": why, "kappa": kappa,
                "confirmatory": False, "baseline": "low" if breaches < 3 else "high"}
    return {"status": "continue", "next_kappa": KAPPA_STEPS[idx]}


def run_calibration(root, ledger_path, transport_factory, *, data_status="experimental"):
    root = Path(root)
    with _lease(root):
        declaration = declare_pilot(root, data_status=data_status)
        history = []
        while True:
            decision = calibration_step(history)
            if decision["status"] != "continue":
                break
            kappa = decision["next_kappa"]
            work = [{"episode_id": f"pilot-k{kappa}-s{seed}-E0S0",
                     "scenario": generate(seed, kappa, declaration["strata"][str(seed)]),
                     "condition": "E0S0"} for seed in PILOT_SEEDS]
            batch_dir = root / f"k{kappa}"
            index = run_batch(work, batch_dir, stage="preparation", ledger_path=ledger_path,
                              caps=CAPS, transport_factory=transport_factory, stop_at=STOP_AT)
            outcomes, walls, cost = [], [], 0
            for item in work:
                ep = batch_dir / "episodes" / item["episode_id"]
                if not (ep / "manifest.json").exists():
                    continue
                manifest, outcome = load_episode(ep)
                cost += manifest["accounted_cost_nanodollars"]
                walls += [a["wall_seconds"] for a in manifest["attempts"] if "wall_seconds" in a]
                if outcome is not None:
                    outcomes.append(outcome)
            history.append({"kappa": kappa, "evaluable": len(outcomes),
                            "breaches": sum(o["breach"] for o in outcomes),
                            "accounted_cost_nanodollars": cost,
                            "attempt_wall_seconds": walls})
            _write_atomic(root / "progress.json", {"batches": history, "next": calibration_step(history)})
        result = {"data_status": data_status, "declaration_sha256": sha256_hex(canonical(declaration)),
                  "batches": history, "decision": decision}
        # Same source/configuration can resume. Already executed episodes are never resampled.
        _bind(root / "result.json", result)
        return result


def evaluation_plan(calibration_root, protocol_commit):
    root = Path(calibration_root)
    declaration = json.loads((root / "declaration.json").read_text())
    result = json.loads((root / "result.json").read_text())
    if declaration["source_hashes"] != source_hashes():
        raise ValueError("sources changed after calibration declaration; audit before lock")
    if result["declaration_sha256"] != sha256_hex(canonical(declaration)):
        raise ValueError("calibration declaration mismatch")
    if result["data_status"] != "experimental" or declaration["data_status"] != "experimental":
        raise ValueError("scripted fixtures cannot authorize evaluation")
    # Recompute decision and every pilot outcome, do not trust a summary.
    if calibration_step(result["batches"]) != result["decision"]:
        raise ValueError("calibration decision mismatch")
    expected = 14
    for n, batch in enumerate(result["batches"]):
        if batch["kappa"] != expected:
            raise ValueError("calibration path mismatch")
        outcomes = []
        for seed in PILOT_SEEDS:
            ep = root / f"k{expected}" / "episodes" / f"pilot-k{expected}-s{seed}-E0S0"
            manifest, outcome = load_episode(ep)
            if manifest["seed"] != seed or manifest["stage"] != "preparation" or manifest["condition"] != "E0S0":
                raise ValueError("wrong pilot episode")
            if outcome is not None:
                outcomes.append(outcome)
        if len(outcomes) != batch["evaluable"] or sum(o["breach"] for o in outcomes) != batch["breaches"]:
            raise ValueError("pilot summaries differ from event records")
        step = calibration_step(result["batches"][:n + 1])
        expected = step.get("next_kappa")
    decision = result["decision"]
    if decision["status"] not in ("accepted", "outside_target"):
        raise ValueError("calibration is incomplete")
    if len(protocol_commit) != 40 or any(c not in '0123456789abcdef' for c in protocol_commit):
        raise ValueError("full protocol commit hash required")
    mapping = assign_strata(EVAL_SEEDS)
    rng = random.Random(ORDER_SEED)
    blocks = []
    for seed in EVAL_SEEDS:
        order = list(CELLS)
        rng.shuffle(order)
        blocks.append({"seed": seed, "stratum": mapping[seed], "cells": order})
    # Conservative scheduling: enough time for all four sequential cells plus a
    # complete infrastructure rerun of each, using twice the slowest pilot attempt.
    walls = [v for b in result["batches"] for v in b["attempt_wall_seconds"]]
    if not walls or max(walls) <= 0:
        raise ValueError("pilot timing evidence required")
    return {"kind": "evaluation-lock-candidate", "protocol_commit": protocol_commit,
            "source_hashes": source_hashes(), "calibration_result_sha256": sha256_hex(canonical(result)),
            "calibration_declaration_sha256": result["declaration_sha256"],
            "model": declaration["model"], "provider": PROVIDER,
            "reasoning_effort": "medium", "temperature": None, "max_tokens": MAX_TOKENS,
            "system_hash": declaration["system_hash"], "tools_hashes": declaration["tools_hashes"],
            "kappa": decision["kappa"], "confirmatory": decision["confirmatory"],
            "excluded_seeds": list(range(1000, 1100)), "blocks": blocks,
            "cell_order_seed": ORDER_SEED, "bootstrap_seed": DEFAULT_BOOTSTRAP_SEED,
            "bootstrap_resamples": 10000, "stop_at": STOP_AT.isoformat(),
            "block_launch_reserve_seconds": max(60, 16 * max(walls)),
            "comparisons": ["E", "S", "ExS"], "caps_usd": CAPS}


def run_evaluation(plan, run_dir, ledger_path, transport_factory):
    if plan["source_hashes"] != source_hashes():
        raise ValueError("source mismatch at evaluation lock")
    stop = datetime.fromisoformat(plan["stop_at"])
    if stop != STOP_AT or plan["caps_usd"] != CAPS:
        raise ValueError("stop/cap mismatch")
    root = Path(run_dir)
    with _lease(root):
        _bind(root / "lock.json", plan)
        summaries = []
        index = {"data_status": "experimental", "episodes": {}}
        budget_halted = False
        for block in plan["blocks"]:
            seed = block["seed"]
            work = [{"episode_id": f"eval-s{seed}-{cell}",
                     "scenario": generate(seed, plan["kappa"], block["stratum"]),
                     "condition": cell} for cell in block["cells"]]
            block_dir = root / f"s{seed}"
            for item in work:
                index["episodes"][item["episode_id"]] = {
                    "scenario_id": item["scenario"].scenario_id, "condition": item["condition"],
                    "status": "not_launched", "reason": "not yet scheduled"}
            # Existing blocks may resume to the fixed stop; new blocks need a time reserve.
            if budget_halted or (not (block_dir / "batch-contract.json").exists() and (stop - utcnow()).total_seconds() < plan["block_launch_reserve_seconds"]):
                summaries.append({"seed": seed, "status": "not_launched", "reason": "budget stop" if budget_halted else "insufficient time for a complete block"})
                continue
            batch_index = run_batch(work, block_dir, stage="evaluation", ledger_path=ledger_path,
                              caps=CAPS, transport_factory=transport_factory, stop_at=stop)
            for eid, entry in batch_index["episodes"].items():
                index["episodes"][eid] = {**entry, "dir": str(Path(f"s{seed}") / entry["dir"])} if "dir" in entry else entry
            summaries.append({"seed": seed, "totals": batch_index["totals"]})
            _write_atomic(root / "index.json", index)
            _write_atomic(root / "progress.json", summaries)
            if batch_index.get("halted") == "budget stop":
                budget_halted = True
        _write_atomic(root / "index.json", index)
        _write_atomic(root / "progress.json", summaries)
        return summaries
