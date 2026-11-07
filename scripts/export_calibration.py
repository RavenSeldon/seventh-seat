#!/usr/bin/env python3
"""Curate all declared pilot records locally and re-verify the locked decision."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from seventh_seat.agents.evalrunner import _lease
from seventh_seat.experiment import evaluation_plan,PILOT_SEEDS
from seventh_seat.world.events import canonical


def export(pilot,lock,output):
    pilot,output=Path(pilot).resolve(),Path(output).resolve()
    if output.exists() or output==pilot or pilot in output.parents:
        raise ValueError('a new destination outside the pilot is required')
    with _lease(pilot):
        if evaluation_plan(pilot,lock['protocol_commit'])!=lock:
            raise ValueError('pilot does not reproduce the frozen evaluation lock')
        result=json.loads((pilot/'result.json').read_text())
        manifests={f"k{b['kappa']}/episodes/pilot-k{b['kappa']}-s{seed}-E0S0/manifest.json"
                   for b in result['batches'] for seed in PILOT_SEEDS}
        if {str(p.relative_to(pilot)) for p in pilot.glob('k*/episodes/*/manifest.json')}!=manifests:
            raise ValueError('pilot has records outside its declared calibration trace')
        names=['declaration.json','result.json']
        for name in sorted(manifests):
            names.append(name);m=json.loads((pilot/name).read_text())
            names.extend(str(Path(name).parent/a['log']) for a in m['attempts'])
        pattern=re.compile(rb'(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{25,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
        for name in names:
            path=pilot/name
            if not path.is_file() or path.is_symlink() or pilot not in path.resolve().parents:
                raise ValueError('pilot export input must be an ordinary in-root file')
            if any(p.is_symlink() for p in path.parents if p!=pilot):
                raise ValueError('symlinked pilot paths require an audit')
            if pattern.search(path.read_bytes()):
                raise ValueError('credential-shaped material requires an audit')
        output.mkdir(parents=True)
        try:
            for name in names:
                target=output/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(pilot/name,target)
            if evaluation_plan(output,lock['protocol_commit'])!=lock:
                raise ValueError('exported pilot does not reproduce the frozen decision')
            (output/'evaluation-lock.json').write_text(canonical(lock)+'\n')
            receipt={'status':'local-export-not-published','kind':'calibration-records',
                     'protocol_commit':lock['protocol_commit'],'episodes':len(manifests),
                     'settings':[b['kappa'] for b in result['batches']],
                     'decision':result['decision'],'additional_paid_calls':0,
                     'files':{name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in names+['evaluation-lock.json']},
                     'excluded_material':['provider cache','credentials','budget databases','raw SDK reasoning state']}
            (output/'EXPORT.json').write_text(json.dumps(receipt,indent=2)+'\n')
            return receipt
        except BaseException:
            (output/'EXPORT_FAILED.txt').write_text('Incomplete calibration export. Do not publish.\n')
            raise

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pilot',type=Path,required=True);p.add_argument('--lock',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();receipt=export(a.pilot,json.loads(a.lock.read_text()),a.output)
    print(json.dumps({k:v for k,v in receipt.items() if k!='files'},indent=2))
