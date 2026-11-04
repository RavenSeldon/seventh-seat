"""Correction C-1 (D-026) to Gate GM scoring: cost evidence, never an implied US$0.

The declared gm-v2 scorer (`qualification.score_run`, `qualification.select`) is
reused unchanged for every criterion. This module replaces only how spend is
evidenced and when cost-based selection may run:

* a run's spend is available only from ledger rows it recorded and the ledger holds;
* a run that recorded no ledger rows (a cache-only replay) incurred no additional
  charge, but its qualification spend is unavailable unless verified historically;
* historical spend is accepted only if the live run's rows are present and settled,
  the replay used exactly the live run's cache entries, and the cached charges for
  those entries equal the ledger;
* cost-based selection is withheld whenever a passing configuration lacks evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import qualification as q

UNAVAILABLE = "unavailable"


def cache_keys(run_dir):
    """Every cache entry a run's records reference (rules records and engine logs)."""
    run_dir, keys = Path(run_dir), set()
    for f in run_dir.rglob("*.json"):
        if f.name not in ("run.json", "summary.json"):
            key = json.loads(f.read_text()).get("cache_key")
            if key:
                keys.add(key)
    for f in run_dir.rglob("*.jsonl"):
        for line in f.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                if rec.get("action") == "model_call" and rec.get("cache_key"):
                    keys.add(rec["cache_key"])
    return keys


def run_spend(run_dir, ledger_path):
    """Spend evidenced by the run's own ledger rows."""
    rows = json.loads((Path(run_dir) / "run.json").read_text())["ledger_rows"]
    if not rows:
        return {"evidence": UNAVAILABLE, "reason": "run recorded no ledger rows (cache-only replay)",
                "this_run_additional_nanodollars": 0, "measured_nanodollars": None, "upper_nanodollars": None}
    if ledger_path is None:
        return {"evidence": UNAVAILABLE, "reason": "ledger not supplied",
                "this_run_additional_nanodollars": None, "measured_nanodollars": None, "upper_nanodollars": None}
    held = q.ledger_rows(ledger_path, json.loads((Path(run_dir) / "run.json").read_text())["provider"])
    missing = [r for r in rows if r not in held]
    if missing:
        return {"evidence": UNAVAILABLE, "reason": f"{len(missing)} recorded ledger rows absent from the ledger",
                "this_run_additional_nanodollars": None, "measured_nanodollars": None, "upper_nanodollars": None}
    mine = [held[r] for r in rows]
    measured = sum(r["actual"] or 0 for r in mine)
    upper = sum(r["actual"] if r["actual"] is not None else r["reserved"] for r in mine)
    return {"evidence": "ledger", "basis": f"{len(rows)} ledger rows recorded by this run",
            "measured_nanodollars": measured, "upper_nanodollars": upper,
            "unresolved": sum(r["actual"] is None for r in mine), "this_run_additional_nanodollars": upper}


def historical_spend(replay_dir, live_dir, cache, ledger_path):
    """Original qualification spend for a replay, accepted only after verification."""
    live = run_spend(live_dir, ledger_path)
    if live["evidence"] != "ledger":
        return {"evidence": UNAVAILABLE, "reason": "live run spend unavailable: " + live["reason"]}
    if live["unresolved"]:
        return {"evidence": UNAVAILABLE, "reason": "live run has unresolved reservations"}
    rk, lk = cache_keys(replay_dir), cache_keys(live_dir)
    if rk != lk:
        return {"evidence": UNAVAILABLE, "reason": "replay and live runs reference different cache entries"}
    cached = 0
    for key in lk:
        payload = cache.get(key)
        if payload is None:
            return {"evidence": UNAVAILABLE, "reason": "cache entry missing"}
        cached += sum(a.get("cost_nanodollars", 0) for a in payload["attempts"])
    if cached != live["measured_nanodollars"]:
        return {"evidence": UNAVAILABLE, "reason": "cached charges do not equal the live ledger rows"}
    return {"evidence": "historical-verified",
            "basis": (f"live run {Path(live_dir).name}: {live['basis']}; all settled; replay used the same "
                      f"{len(lk)} cache entries; cached charges equal the ledger"),
            "measured_nanodollars": live["measured_nanodollars"], "upper_nanodollars": live["upper_nanodollars"]}


def select(scores):
    """q.select, guarded: no cost-based selection without cost evidence."""
    passing = [s for s in scores if s["passed"]]
    if len(passing) > 1:
        lacking = sorted(s["provider"] for s in passing if s["spend"].get("evidence") == UNAVAILABLE)
        if lacking:
            return {"selected": None, "reason": "cost evidence unavailable for " + ", ".join(lacking)
                    + "; cost-based selection withheld"}
    return q.select(scores)


def with_spend(score, spend):
    return {**score, "spend": dict(spend)}
