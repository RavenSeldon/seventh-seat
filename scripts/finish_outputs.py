#!/usr/bin/env python3
"""Wait locally for the collector, then produce private audited report inputs.

No provider calls, publication, submission or scientific parameter changes.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from export_research import export
from report_results import summarize,markdown
from seventh_seat.world.events import canonical


def write(path,data):
    temp=path.with_suffix('.tmp')
    with temp.open('w') as f:
        json.dump(data,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temp,path)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--wait',action='store_true');args=p.parse_args()
    runs=ROOT/'runs';status=runs/'report-output-status.json'
    def state(value,**details):write(status,{'state':value,'pid':os.getpid(),'updated_utc':datetime.now(timezone.utc).isoformat(),**details})
    with (runs/'report-output.lock').open('a') as lease:
        try:fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise SystemExit('Another report finisher is active')
        wake=subprocess.Popen(['/usr/bin/caffeinate','-i','-w',str(os.getpid())])
        try:
            state('waiting_for_verified_collection')
            while True:
                controller=json.loads((runs/'controller-status.json').read_text())
                if controller['state']=='results_ready':break
                if controller['state']=='stopped':
                    state('stopped',reason='collector stopped; manual audit required');return 1
                if not args.wait:raise RuntimeError('collection is not ready')
                if datetime.now(timezone.utc)>datetime(2026,11,8,8,tzinfo=timezone.utc):
                    state('stopped',reason='post-collection wait deadline reached');return 1
                time.sleep(30)
            state('building_report_inputs')
            output=runs/'report-output-2026-11-06';output.mkdir(exist_ok=True)
            curated=output/'curated-records'
            if not curated.exists():export(runs/'evaluation-2026-11-06',curated)
            data=summarize(curated)
            write(output/'report-tables.json',data)
            (output/'report-tables.md').write_text(markdown(data))
            pilot=json.loads((runs/'pilot-2026-11-06/result.json').read_text())
            lock=json.loads((curated/'lock.json').read_text())
            if hashlib.sha256(canonical(pilot).encode()).hexdigest()!=lock['calibration_result_sha256']:
                raise ValueError('calibration summary differs from evaluation lock')
            write(output/'calibration-summary.json',pilot)
            db=sqlite3.connect((runs/'research-budget.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
            try:
                totals=[{'provider':provider,'status':charge_status,'requests':n,'accounted_usd':cost/1e9} for provider,charge_status,n,cost in db.execute('select provider,status,count(*),sum(coalesce(actual,reserved)) from charges group by provider,status')]
            finally:db.close()
            write(output/'private-cost-summary.json',{'basis':'published-rate usage estimates and conservative unresolved reservations; not a provider invoice','totals':totals})
            state('report_inputs_ready',output=str(output),complete_scenarios=data['complete_scenarios'],evaluable_episodes=data['evaluable_episodes'],
                  review_remaining=['manuscript interpretation and final layout','calibration-record release audit','author publication and submission'])
            return 0
        except Exception as exc:
            state('stopped',reason='report input verification failed',exception_type=type(exc).__name__)
            return 1
        finally:
            wake.terminate();wake.wait()

if __name__=='__main__':raise SystemExit(main())
