#!/usr/bin/env python3
"""End-to-end scripted dry run: offline, no credentials, no provider calls, real ledger untouched.

Writes private artifacts to a new directory and, with --record, a shareable summary
(hashes, checks and scripted-fixture outcomes only) to experiments/.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from seventh_seat import rehearsal


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True, help="new directory; never overwritten")
    p.add_argument("--record", type=Path, help="write the shareable summary here (never overwrites)")
    a = p.parse_args()
    ledger = ROOT / "runs/scratch/wednesday-budget.sqlite"
    before = hashlib.sha256(ledger.read_bytes()).hexdigest() if ledger.exists() else None
    result = rehearsal.run(a.output)
    after = hashlib.sha256(ledger.read_bytes()).hexdigest() if ledger.exists() else None
    result["checks"]["real_ledger_untouched"] = before == after
    result["passed"] = all(result["checks"].values())
    if a.record:
        if a.record.exists():
            raise SystemExit("record exists; never overwritten")
        src = ["src/seventh_seat/rehearsal.py", "scripts/dry_run.py"]
        result["sources_sha256"] = {s: hashlib.sha256((ROOT / s).read_bytes()).hexdigest() for s in src}
        a.record.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({"passed": result["passed"], "failed": [k for k, v in result["checks"].items() if not v],
                      "output": str(a.output)}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
