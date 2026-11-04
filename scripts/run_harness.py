#!/usr/bin/env python3
"""Bounded no-hazard smoke episode; explicitly not qualification or evaluation."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from check_api_access import read_keys
from seventh_seat.agents.providers import SDKTransport
from seventh_seat.agents.runtime import Caller, run_with_recovery
from seventh_seat.agents.storage import Budget, ResponseCache


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--provider',choices=('openai','anthropic'),required=True)
    p.add_argument('--output',type=Path,required=True,help='new directory; never overwrites an earlier run')
    p.add_argument('--episode-id',default='wednesday-smoke-v1')
    p.add_argument('--replay',action='store_true',help='cache only; never loads credentials or contacts provider')
    p.add_argument('--max-tokens',type=int,default=2048)
    args=p.parse_args()
    if args.output.exists():p.error('output directory already exists')
    if not 128 <= args.max_tokens <= 16384:p.error('max tokens must be 128–16384')
    cache=ResponseCache(ROOT/'runs/cache/wednesday-v1')
    budget=None;transport=None
    try:
        if not args.replay:
            key_name='OPENAI_API_KEY' if args.provider=='openai' else 'ANTHROPIC_API_KEY'
            key=read_keys(ROOT/'.env.local').get(key_name) or os.environ.get(key_name)
            if not key:raise ValueError('provider credential missing; run scripts/check_api_access.py --setup')
            # Shared durable ledger: $4 total, $2 per provider, all charged to prep.
            budget=Budget(ROOT/'runs/scratch/wednesday-budget.sqlite',
                          {'total':4,'preparation':4,'openai':2,'anthropic':2})
            transport=SDKTransport(args.provider,key)
        caller=Caller(args.provider,cache,budget,transport,replay=args.replay)
        summary=run_with_recovery(caller,args.output,args.episode_id,args.max_tokens)
        print(json.dumps({'status':summary['status'],'qualified':False,'output':str(args.output),
                          'budget':budget.summary() if budget else 'cache-only; no API spend'},indent=2))
        return 0 if summary['status']=='completed' else 1
    except Exception as exc:
        # Do not print SDK bodies, credentials, or private provider history.
        print(f'Harness stopped: {type(exc).__name__}. Inspect local run records; no credential values shown.',file=sys.stderr)
        return 1
    finally:
        if transport:transport.close()
        if budget:budget.close()


if __name__=='__main__':raise SystemExit(main())
