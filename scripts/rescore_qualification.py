#!/usr/bin/env python3
"""Correction C-1 (D-026): rescore gm-v2 with cost evidence. No model calls.

Reuses the declared gm-v2 scorer for every criterion, verifies the gm-v2
declaration first, and writes a corrected artifact beside (never over) the
original outputs.
"""
import argparse
import datetime
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import run_qualification as rq
from seventh_seat.agents import qualification as q
from seventh_seat.agents import qualification_correction as c
from seventh_seat.agents.storage import ResponseCache
from seventh_seat.world.events import sha256_hex

SOURCES = ["src/seventh_seat/agents/qualification_correction.py", "scripts/rescore_qualification.py",
           "tests/test_qualification_correction.py"]


def offline_correction_tests():
    import io
    import unittest
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.loadTestsFromNames(["tests.test_qualification_correction"])
    r = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return {"tests_run": r.testsRun, "failures": len(r.failures), "errors": len(r.errors), "passed": r.wasSuccessful()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tag", default="replay-live")
    p.add_argument("--historical-tag", default="live", help="live run whose verified costs may be reused")
    args = p.parse_args()
    declaration = rq.verify_declaration()                  # gm-v2 sources unchanged
    cache = ResponseCache(rq.CACHE)
    offline, correction_tests = rq.offline_suites(), offline_correction_tests()
    providers = [x for x in ("openai", "anthropic") if (rq.RUNS / x / args.tag / "run.json").exists()]
    base = {x: q.score_run(rq.RUNS / x / args.tag, cache, rq.LEDGER, offline_ga_passed=offline["passed"])
            for x in providers}
    own = {x: c.run_spend(rq.RUNS / x / args.tag, rq.LEDGER) for x in providers}
    hist = {x: c.historical_spend(rq.RUNS / x / args.tag, rq.RUNS / x / args.historical_tag, cache, rq.LEDGER)
            for x in providers}
    own_scores = [c.with_spend(base[x], own[x]) for x in providers]
    hist_scores = [c.with_spend(base[x], hist[x] if own[x]["evidence"] == c.UNAVAILABLE else own[x]) for x in providers]
    original = rq.GM / f"qualification_result_{args.tag}.json"
    result = {
        "data_status": q.DATA_STATUS, "spec_version": q.SPEC_VERSION, "correction": "C-1", "decision_record": "D-026",
        "rescored_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "gm_v2_declaration_sha256": sha256_hex(rq.DECLARATION.read_text()), "gm_v2_declared_utc": declaration["declared_utc"],
        "correction_sources_sha256": {s: sha256_hex((ROOT / s).read_text()) for s in SOURCES},
        "offline_suites": offline, "correction_tests": correction_tests,
        "supersedes": ({"path": str(original.relative_to(ROOT)), "sha256": sha256_hex(original.read_text()),
                        "field": "decision", "why": "unavailable spend was scored as US$0, producing a false cost tie"}
                       if original.exists() else None),
        "cost_basis": "calculated from provider-reported usage at published standard rates; not invoice",
        "criteria_unchanged_from_declared_scorer": True,
        "scores": [{**s, "spend_this_run": own[s["provider"]]} for s in hist_scores],
        "decision_from_this_run_evidence": c.select(own_scores),
        "decision_with_verified_historical_cost": c.select(hist_scores),
    }
    out = rq.GM / f"qualification_result_{args.tag}.corrected.json"
    if out.exists():
        raise SystemExit("corrected artifact exists; never overwritten")
    out.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({"written": str(out.relative_to(ROOT)),
                      "from_this_run": result["decision_from_this_run_evidence"],
                      "with_verified_history": result["decision_with_verified_historical_cost"],
                      "tests": [offline, correction_tests]}, indent=2))


if __name__ == "__main__":
    main()
