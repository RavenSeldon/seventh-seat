#!/usr/bin/env python3
"""Recompute manuscript tables from a curated, locally audited research export."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from seventh_seat.analysis.run import analyze_run,OUTCOME_CONTRASTS
from seventh_seat.world.events import canonical,read_jsonl
from seventh_seat.world.params import CELLS


def summarize(run):
    run=Path(run)
    receipt=json.loads((run/'EXPORT.json').read_text())
    for name,digest in receipt['files'].items():
        if hashlib.sha256((run/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('export receipt mismatch')
    result=analyze_run(run)
    lock=json.loads((run/'lock.json').read_text())
    for name,digest in result['provenance']['analysis_sources_sha256'].items():
        if lock['source_hashes'].get(name)!=digest:
            raise ValueError('analysis source differs from the evaluation lock')
    complete=set(result['blocks']['complete'])
    rows={}
    for cell in CELLS:
        entries=[e for e in result['episodes'].values() if e['condition']==cell]
        evaluable=[e for e in entries if e['evaluable']]
        outcomes=[e['outcome'] for e in evaluable if e['scenario_id'] in complete]
        def mean(key):return sum(o[key] for o in outcomes)/len(outcomes) if outcomes else None
        reports={key:dict(sum((Counter(e['outcome']['reports'][key]) for e in evaluable),Counter())) for key in ('appropriate','false')}
        calls=result['call_outcome_counts_by_cell_all_attempts'][cell]
        call_total=sum(calls.values())
        actions=[]
        for m in run.glob('s*/episodes/*/manifest.json'):
            manifest=json.loads(m.read_text())
            if manifest['condition']==cell:
                for a in manifest['attempts']:
                    actions.extend(r for r in read_jsonl(m.parent/a['log']) if r['actor_id'].startswith('D') and r['action'] in ('post','read_ledger','offer','accept','plan','commit','record_concern','submit_report','endorse'))
        invalid=sum(not r.get('authorized',False) or (isinstance(r.get('result'),dict) and r['result'].get('ok') is False) for r in actions)
        rows[cell]={'planned':len(entries),'evaluable':len(evaluable),'complete_block_episodes':len(outcomes),
                    'mean':{key:mean(key) for key in OUTCOME_CONTRASTS},
                    'shortfall_values_complete_blocks':sorted(o['shortfall'] for o in outcomes),
                    'all_evaluable_no_commit_rate':sum(e['outcome']['no_commit_count'] for e in evaluable)/(6*len(evaluable)) if evaluable else None,
                    'all_attempts_action_count':len(actions),'all_attempts_invalid_actions':invalid,
                    'all_attempts_invalid_action_rate':invalid/len(actions) if actions else None,
                    'all_attempts_call_counts':calls,'all_attempts_call_rates':{k:v/call_total for k,v in calls.items()} if call_total else {},
                    'all_evaluable_reports':reports,
                    'all_evaluable_latency_values':{key:[e['outcome']['latencies'][key] for e in evaluable] for key in ('hazard_onset','first_evidence_bearing_concern','first_report_reaching_supervisor','hold','correction')}}
    hypotheses={}
    for name,effect in [('H1','E'),('H2','S')]:
        c=result['contrasts']['shortfall'][effect]
        hypotheses[name]='not assessed confirmatorily' if not lock['confirmatory'] else ('unavailable' if c['estimate'] is None else ('supported under the preregistered interval rule' if c['ci95'][1]<0 else 'not supported under the preregistered interval rule'))
    return {'data_status':result['data_status'],'interpretation':result['interpretation'],
            'protocol_commit':lock['protocol_commit'],'calibrated_kappa':lock.get('kappa'),
            'planned_scenarios':len(lock['blocks']),'complete_scenarios':len(complete),
            'evaluable_episodes':result['episodes_evaluable'],
            'missing_episodes':result['episodes_unevaluable'],
            'incomplete_scenarios':result['blocks']['incomplete_dropped_from_contrasts'],
            'episode_status_counts':dict(Counter(e['status'] for e in result['episodes'].values())),
            'cells':rows,'contrasts':result['contrasts'],'hypotheses':hypotheses,
            'zero_inflation':result['zero_inflation'],'descriptive':result['descriptive'],
            'refusals':result['refusals'],'bootstrap':result['bootstrap'],
            'provenance':result['provenance'],
            'notes':['Cell means and contrasts use complete scenario blocks. Other summaries explicitly retain all evaluable episodes or all attempts.',
                     'H3 interaction and stratum summaries are exploratory. H4 trade-disabled diagnostic was not collected.',
                     'AWC is the disclosed conservative proxy; it does not fully represent extra replan opportunities.',
                     'No provider invoice or private budget database is part of this export.']}


def markdown(data):
    def f(v):return 'unavailable' if v is None else f'{v:.4f}'
    lines=['# Computed research tables','',f"Interpretation: {data['interpretation']}.",
           f"Complete scenarios: {data['complete_scenarios']} of {data['planned_scenarios']}; evaluable episodes: {data['evaluable_episodes']}.",'',
           '| Cell | Complete blocks | Shortfall | Breach fraction | Demand fulfilled | Unmet need | Alternative cost |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for cell,row in data['cells'].items():
        lines.append('| '+' | '.join([cell,str(row['complete_block_episodes'])]+[f(row['mean'][k]) for k in OUTCOME_CONTRASTS])+' |')
    lines.extend(['','| Outcome | Contrast | Estimate | 95% interval |','|---|---|---:|---|'])
    for outcome,contrasts in data['contrasts'].items():
        for name,c in contrasts.items():lines.append(f"| {outcome} | {name} | {f(c['estimate'])} | [{f(c['ci95'][0])}, {f(c['ci95'][1])}] |")
    lines.extend(['']+[f'{k}: {v}.' for k,v in data['hypotheses'].items()]+['']+data['notes'])
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();data=summarize(a.run);a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'report-tables.json').write_text(canonical(data)+'\n');(a.out/'report-tables.md').write_text(markdown(data))
    print(json.dumps({'output':str(a.out),'complete_scenarios':data['complete_scenarios'],'evaluable_episodes':data['evaluable_episodes']}))
