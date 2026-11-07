#!/usr/bin/env python3
"""Calibration and locked evaluation. No live call without an explicit --live flag."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from check_api_access import read_keys
from seventh_seat.experiment import (CAPS, declare_pilot, initialize_budget,
    run_calibration, evaluation_plan, run_evaluation, source_hashes)
from seventh_seat.agents.providers import SDKTransport
from seventh_seat.agents.evalrunner import _bind


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('declare-pilot', 'pilot', 'prepare-lock', 'evaluate'))
    parser.add_argument('--pilot', type=Path, default=ROOT/'runs/pilot-2026-11-06')
    parser.add_argument('--evaluation', type=Path, default=ROOT/'runs/evaluation-2026-11-06')
    parser.add_argument('--ledger', type=Path, default=ROOT/'runs/research-budget.sqlite')
    parser.add_argument('--historical-ledger', type=Path, default=ROOT/'runs/scratch/wednesday-budget.sqlite')
    parser.add_argument('--lock', type=Path, default=ROOT/'experiments/evaluation-lock.json')
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args(argv)
    if args.action == 'declare-pilot':
        result = declare_pilot(args.pilot)
    elif args.action == 'prepare-lock':
        commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
        result = evaluation_plan(args.pilot, commit)
        args.lock.parent.mkdir(parents=True, exist_ok=True)
        _bind(args.lock, result)
    else:
        if not args.live:
            parser.error('paid calls require --live')
        # Hashes and tags are checked BEFORE loading keys, opening SDKs or charging.
        if args.action == 'pilot':
            declare_pilot(args.pilot)
        else:
            plan = json.loads(args.lock.read_text())
            tag = subprocess.check_output(['git','rev-parse','prereg-frozen^{commit}'], cwd=ROOT, text=True).strip()
            head = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
            if tag != head:
                raise ValueError('prereg-frozen must identify the current reviewed HEAD')
            if source_hashes() != plan['source_hashes']:
                raise ValueError('source hashes differ from lock')
            # Sources must match the tagged tree too; an uncommitted working tree
            # cannot smuggle a different instrument under a valid tag.
            for name in plan['source_hashes']:
                import hashlib
                data = subprocess.check_output(['git','show',f'{tag}:{name}'], cwd=ROOT)
                if hashlib.sha256(data).hexdigest() != plan['source_hashes'][name]:
                    raise ValueError('tagged source differs from lock')
            check = evaluation_plan(args.pilot, plan['protocol_commit'])
            if check != plan:
                raise ValueError('lock no longer matches verified pilot')
            gates = json.loads((ROOT/'experiments/research-gates.json').read_text())
            required = ['G0','G1','G2','G3','G3b','G4','G5','G6','G7','G8','G9','G10','G11','GM']
            if any(gates.get(g) != 'pass' for g in required):
                raise ValueError('required research gates remain open')
            if gates.get('source_hashes') != source_hashes():
                raise ValueError('research gates do not bind these sources')
        summary = initialize_budget(args.ledger, args.historical_ledger)
        print(json.dumps({'budget_before': summary, 'caps_usd': CAPS}), flush=True)
        key = read_keys(ROOT/'.env.local').get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
        if not key:
            raise ValueError('OpenAI credential missing')
        factory = lambda: SDKTransport('openai', key)
        if args.action == 'pilot':
            result = run_calibration(args.pilot, args.ledger, factory)
        else:
            result = run_evaluation(plan, args.evaluation, args.ledger, factory)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        # Provider bodies/credentials are never printed.
        print(f'Experiment stopped: {type(exc).__name__}. Inspect local records; no credentials printed.', file=sys.stderr)
        raise SystemExit(1)
