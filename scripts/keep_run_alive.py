#!/usr/bin/env python3
"""One local supervisor: pilot -> wait for reviewed lock -> evaluation -> analysis.

No cloud service, polling model calls, new seeds or automatic model selection.
A terminal pilot failure stops here. Process-level restarts only resume the
runner's existing attempt budget. The controller never commits or creates tags.
"""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT/'runs'
PYTHON = str(ROOT/'.venv/bin/python')
STOP = datetime(2026, 11, 8, 6, tzinfo=timezone.utc)
STATUS = RUNS/'controller-status.json'


def status(state, **detail):
    payload = {'state': state, 'updated_utc': datetime.now(timezone.utc).isoformat(),
               'pid': os.getpid(), **detail}
    temp = STATUS.with_suffix('.tmp')
    with temp.open('w') as f:
        json.dump(payload, f, indent=2)
        f.flush(); os.fsync(f.fileno())
    os.replace(temp, STATUS)


def held(path):
    if not path.exists():
        return False
    with path.open('a') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(f, fcntl.LOCK_UN)
    return False


def run(argv, name):
    with (RUNS/f'{name}.log').open('ab', buffering=0) as out:
        result = subprocess.run([PYTHON, *argv], cwd=ROOT, stdin=subprocess.DEVNULL,
                                stdout=out, stderr=subprocess.STDOUT)
    return result.returncode


def main():
    RUNS.mkdir(exist_ok=True)
    with (RUNS/'controller.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('Another controller is already running')
        wake = subprocess.Popen(['/usr/bin/caffeinate','-i','-w',str(os.getpid())])
        try:
            pilot = RUNS/'pilot-2026-11-06'
            result = pilot/'result.json'
            status('pilot_running', budget_caps_usd={'total':66,'preparation':20,'openai':33,'anthropic':33})
            # Adopt the already-running, authorized pilot without duplicating it.
            while held(pilot/'.writer.lock'):
                time.sleep(20)
            if not result.exists():
                status('resuming_interrupted_pilot')
                if run(['scripts/run_experiment.py','pilot','--live'], 'pilot-resume'):
                    status('stopped', reason='pilot process failed; inspect private logs')
                    return 1
            if not result.exists() or json.loads(result.read_text())['decision']['status'] not in ('accepted','outside_target'):
                status('stopped', reason='calibration incomplete; no evaluation permitted')
                return 1
            status('awaiting_evaluation_lock', pilot_result=str(result),
                   requirement='reviewed prereg-frozen tag, evaluation-lock.json and passing bound research gates')
            while datetime.now(timezone.utc) < STOP:
                lockfile = ROOT/'experiments/evaluation-lock.json'
                gatefile = ROOT/'experiments/research-gates.json'
                tag = subprocess.run(['git','rev-parse','--verify','prereg-frozen'], cwd=ROOT,
                                     stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode == 0
                if lockfile.exists() and gatefile.exists() and tag:
                    break
                time.sleep(30)
            else:
                status('stopped', reason='fixed collection deadline reached before evaluation lock')
                return 1
            status('evaluation_running')
            if run(['scripts/run_experiment.py','evaluate','--live'], 'evaluation-worker'):
                status('stopped', reason='evaluation failed or lock/gates rejected; no automatic resampling')
                return 1
            status('analyzing')
            env = dict(os.environ, PYTHONPATH=str(ROOT/'src'))
            with (RUNS/'analysis-worker.log').open('ab',buffering=0) as out:
                rc = subprocess.run([PYTHON,'-m','seventh_seat.analysis.run','--run',str(RUNS/'evaluation-2026-11-06')],
                                    cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT).returncode
            if rc:
                status('stopped',reason='analysis integrity check failed')
                return 1
            status('results_ready', results=str(RUNS/'evaluation-2026-11-06/analysis/results.json'),
                   note='Private computed results; manuscript, release audit and author submission remain.')
            return 0
        finally:
            wake.terminate()
            wake.wait()


if __name__ == '__main__':
    raise SystemExit(main())
