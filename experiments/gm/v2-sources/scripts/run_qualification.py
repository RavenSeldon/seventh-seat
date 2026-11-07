#!/usr/bin/env python3
"""Gate GM qualification (E-010): declare, run, score. Not experimental evaluation.

  declare                     hash the spec and every outcome-relevant source, once
  run --provider P            live suite; refuses unless current hashes match the declaration
  run --provider P --replay   cache only; never loads credentials
  score                       recompute scores, spend, latency and the decision from records
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from seventh_seat.agents import qualification as q
from seventh_seat.agents.runtime import Caller
from seventh_seat.agents.storage import Budget, ResponseCache
from seventh_seat.world.events import canonical, sha256_hex

GM = ROOT / "experiments/gm/v2"                         # gm-v1 stays in experiments/gm/
DECLARATION = GM / "DECLARATION.json"
CACHE = ROOT / "runs/cache/gm-v2"
RUNS = ROOT / "runs/scratch/gm-v2"
LEDGER = ROOT / "runs/scratch/wednesday-budget.sqlite"     # the existing ledger, never reset
CAPS = {"total": 4, "preparation": 4, "openai": 2, "anthropic": 2}  # existing immutable caps
HASHED = ["experiments/gm/v2/QUALIFICATION_SPEC.md", "scripts/run_qualification.py",
          "src/seventh_seat/agents/qualification.py", "src/seventh_seat/agents/tools.py",
          "src/seventh_seat/agents/providers.py", "src/seventh_seat/agents/runtime.py",
          "src/seventh_seat/agents/storage.py", "src/seventh_seat/world/engine.py",
          "src/seventh_seat/world/events.py", "src/seventh_seat/world/params.py"]


def current_hashes():
    files = {p: sha256_hex((ROOT / p).read_text(encoding="utf-8")) for p in HASHED}
    material = q.declared_material()
    return {"files": files, "declared_material_sha256": sha256_hex(canonical(material)),
            "requests_sha256": {p: sha256_hex(canonical(v)) for p, v in material["requests"].items()}}


def declare(_):
    q.check_worlds()
    if DECLARATION.exists():
        raise SystemExit("declaration exists; a correction needs a new spec version, never an overwrite")
    record = {"spec_version": q.SPEC_VERSION,
              "declared_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "status": "declared before any gm-v2 qualification call",
              "informed_by": {"note": "revision follows observed gm-v1 failures (D-025)",
                              "gm_v1_declaration_sha256": sha256_hex((ROOT / "experiments/gm/DECLARATION.json").read_text()),
                              "gm_v1_result_sha256": sha256_hex((ROOT / "experiments/gm/qualification_result_live.json").read_text()),
                              "decision_D025_sha256": sha256_hex(next(l for l in (ROOT / "docs/DECISIONS.md").read_text().splitlines()
                                                                      if l.startswith("| D-025 |")))},
              **current_hashes()}
    DECLARATION.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"declared": record["declared_utc"], "material": record["declared_material_sha256"]}, indent=2))


def verify_declaration():
    if not DECLARATION.exists():
        raise SystemExit("no declaration; run declare first")
    d = json.loads(DECLARATION.read_text())
    now = current_hashes()
    bad = [k for k, v in d["files"].items() if now["files"].get(k) != v]
    if bad or d["declared_material_sha256"] != now["declared_material_sha256"]:
        raise SystemExit(f"current sources differ from the declaration: {bad or 'declared material'}")
    return d


def run(args):
    verify_declaration()
    out = RUNS / args.provider / ("replay-" + args.tag if args.replay else args.tag)
    budget = transport = None
    try:
        if not args.replay:
            from check_api_access import read_keys
            from seventh_seat.agents.providers import SDKTransport
            name = "OPENAI_API_KEY" if args.provider == "openai" else "ANTHROPIC_API_KEY"
            key = read_keys(ROOT / ".env.local").get(name) or os.environ.get(name)
            if not key:
                raise SystemExit("provider credential missing")
            budget = Budget(LEDGER, CAPS)
            transport = SDKTransport(args.provider, key)
        caller = Caller(args.provider, ResponseCache(CACHE), budget, transport, replay=args.replay)
        result = q.run_suite(caller, out, None if args.replay else LEDGER)
        print(json.dumps({"provider": args.provider, "status": result["status"], "output": str(out.relative_to(ROOT)),
                          "ledger_rows": len(result["ledger_rows"])}, indent=2))
    finally:
        if transport:
            transport.close()
        if budget:
            budget.close()


def offline_suites():
    """GA wire fixtures and GM scoring fixtures, run on the declared sources."""
    import io
    import unittest
    sys.path.insert(0, str(ROOT))
    os.environ.setdefault("PYTHONPATH", str(ROOT / "src"))
    suite = unittest.defaultTestLoader.loadTestsFromNames(["tests.test_harness", "tests.test_qualification"])
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return {"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
            "passed": result.wasSuccessful()}


def score(args):
    d = verify_declaration()
    cache = ResponseCache(CACHE)
    offline = offline_suites()
    scores = [q.score_run(RUNS / p / args.tag, cache, LEDGER, offline_ga_passed=offline["passed"])
              for p in ("openai", "anthropic") if (RUNS / p / args.tag / "run.json").exists()]
    decision = q.select(scores) if len(scores) == 2 else {"selected": None, "reason": "both configurations not yet run"}
    result = {"data_status": q.DATA_STATUS, "spec_version": q.SPEC_VERSION,
              "declaration_sha256": sha256_hex(DECLARATION.read_text()), "declared_utc": d["declared_utc"],
              "cost_basis": "calculated from provider-reported usage at published standard rates; not invoice",
              "offline_suites": offline,
              "scores": scores, "decision": decision}
    path = GM / f"qualification_result_{args.tag}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({"written": str(path.relative_to(ROOT)), "decision": decision,
                      "passed": {s["provider"]: s["passed"] for s in scores}}, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("declare").set_defaults(fn=declare)
    r = sub.add_parser("run"); r.set_defaults(fn=run)
    r.add_argument("--provider", choices=("openai", "anthropic"), required=True)
    r.add_argument("--tag", default="live")
    r.add_argument("--replay", action="store_true")
    s = sub.add_parser("score"); s.set_defaults(fn=score)
    s.add_argument("--tag", default="live")
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
