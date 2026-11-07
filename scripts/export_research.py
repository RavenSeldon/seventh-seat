#!/usr/bin/env python3
"""Create an audited local research export. Never publishes or copies provider caches."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from seventh_seat.analysis.run import analyze_run
from seventh_seat.experiment import source_hashes
from seventh_seat.agents.evalrunner import _lease
from seventh_seat.world.events import canonical


def export(run, output):
    run, output=Path(run).resolve(),Path(output).resolve()
    if output.exists() or output==run or run in output.parents:
        raise ValueError('export needs a new directory outside the run')
    with _lease(run):
        lock=json.loads((run/'lock.json').read_text())
        if lock['source_hashes']!=source_hashes():
            raise ValueError('current implementation differs from the evaluation lock')
        expected={f"eval-s{block['seed']}-{cell}" for block in lock['blocks'] for cell in block['cells']}
        index=json.loads((run/'index.json').read_text())
        if set(index['episodes']) != expected:
            raise ValueError('the run index does not account for every locked episode')
        result=analyze_run(run)
        if set(result['episodes']) != expected:
            raise ValueError('recorded episodes differ from the locked worklist')
        if result['interrupted_without_manifest']:
            raise ValueError('interrupted episodes require an audit before release')
        # An allowlist prevents environment files, SDK histories and databases
        # from entering this export. Copy bytes intact so chains stay verifiable.
        names=['lock.json','index.json']
        for m in sorted(run.glob('s*/episodes/*/manifest.json')):
            manifest=json.loads(m.read_text())
            names.append(str(m.relative_to(run)))
            for attempt in manifest['attempts']:
                names.append(str((m.parent/attempt['log']).relative_to(run)))
        pattern=re.compile(rb'(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{25,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
        for name in names:
            candidate = run/name
            if not candidate.is_file() or candidate.is_symlink() or run not in candidate.resolve().parents:
                raise ValueError('export inputs must be ordinary files inside the run')
            if any(parent.is_symlink() for parent in candidate.parents if parent != run):
                raise ValueError('symlinked export paths require manual review')
            if pattern.search((run/name).read_bytes()):
                raise ValueError('credential-shaped content requires manual review')
        output.mkdir(parents=True)
        try:
            for name in names:
                target=output/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(run/name,target)
            exported=analyze_run(output)
            for key in ('episodes','blocks','contrasts','zero_inflation','descriptive','refusals'):
                if exported[key]!=result[key]:
                    raise ValueError('export does not reproduce original analysis')
            (output/'analysis').mkdir()
            (output/'analysis/results.json').write_text(canonical(exported)+'\n')
            receipt={'status':'local-export-not-published','source_protocol_commit':lock['protocol_commit'],
                     'files':{name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in names},
                     'evaluation_episodes':result['episodes_evaluable'],
                     'complete_blocks':len(result['blocks']['complete']),
                     'excluded_material':['provider cache','credentials','budget databases','raw SDK reasoning state'],
                     'reproduction':'PYTHONPATH=src python3 -m seventh_seat.analysis.run --run PATH_TO_EXPORT'}
            (output/'EXPORT.json').write_text(json.dumps(receipt,indent=2)+'\n')
            return receipt
        except BaseException:
            (output/'EXPORT_FAILED.txt').write_text('Incomplete export. Do not release. Inspect source integrity and rerun to a new directory.\n')
            raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(export(a.run,a.output),indent=2))
