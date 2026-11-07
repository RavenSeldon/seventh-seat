#!/usr/bin/env python3
"""Cross-check reported outcomes against executed district allocations, offline.

The frozen analyzer reconstructs allocations from authorized acts. This audit
uses the separately logged final allocation rows and direct arithmetic, then
checks every cell mean and point contrast. It does not replace the frozen
bootstrap or revise the preregistered analysis.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from report_results import summarize
from seventh_seat.analysis.run import analyze_run
from seventh_seat.world.events import read_jsonl,canonical


def audit(run):
    run=Path(run);tables=summarize(run);analysis=analyze_run(run)
    calculated={};checks=0
    def equal(a,b,context):
        nonlocal checks
        if not math.isclose(float(a),float(b),abs_tol=1e-12,rel_tol=1e-12):
            raise ValueError('final-allocation cross-check failed: '+context)
        checks+=1
    for p in sorted(run.glob('s*/episodes/*/manifest.json')):
        manifest=json.loads(p.read_text())
        if manifest['status']!='completed':continue
        attempt=next(a for a in manifest['attempts'] if a['status']=='completed')
        records=read_jsonl(p.parent/attempt['log'])
        scenario=next(r['args']['scenario'] for r in records if r['action']=='episode_start')
        final=next(r['result'] for r in records if r['action']=='season_executed')
        districts={d['id']:d for d in scenario['districts']};rows=final['by_district']
        if set(rows)!=set(districts):raise ValueError('final district set mismatch')
        withdrawal=sum(row['river'] for row in rows.values());flow=scenario['F']-withdrawal
        shortfall=max(0,scenario['M']-flow)
        demand_met=sum(min(districts[a]['demand'],row['river']+row['alt']) for a,row in rows.items())
        unmet=sum(max(0,districts[a]['min_need']-row['river']-row['alt']) for a,row in rows.items())
        alt=sum(row['alt'] for row in rows.values());no_commit=sum(row['source']!='commit' for row in rows.values())
        values={'shortfall':shortfall,'breach':int(shortfall>0),
                'U':Fraction(demand_met,sum(d['demand'] for d in districts.values())),
                'unmet_min_need':unmet,'alt_cost':scenario['c_a']*alt}
        outcome=analysis['episodes'][manifest['episode_id']]['outcome']
        for name,v in values.items():equal(v,outcome[name],manifest['episode_id']+'/'+name)
        for name,v in {'total_withdrawal':withdrawal,'downstream_flow':flow,'demand_met':demand_met,'unmet_min_need':unmet,'alt_units':alt,'no_commit_count':no_commit}.items():equal(v,final[name],manifest['episode_id']+'/engine/'+name)
        equal(no_commit,outcome['no_commit_count'],manifest['episode_id']+'/no_commit')
        calculated.setdefault(manifest['scenario_id'],{})[manifest['condition']]=values
    complete=analysis['blocks']['complete'];cells=['E0S0','E0S1','E1S0','E1S1']
    def mean(xs):return sum(xs,Fraction())/len(xs)
    if complete:
        for name in ('shortfall','breach','U','unmet_min_need','alt_cost'):
            for cell in cells:
                equal(mean([Fraction(calculated[sid][cell][name]) for sid in complete]),tables['cells'][cell]['mean'][name],cell+'/mean/'+name)
            effects={'E':[],'S':[],'ExS':[]}
            for sid in complete:
                a,b,c,d=[Fraction(calculated[sid][cell][name]) for cell in cells]
                effects['E'].append((c+d-a-b)/2)
                effects['S'].append((b+d-a-c)/2)
                effects['ExS'].append(d-c-b+a)
            for key,values in effects.items():equal(mean(values),tables['contrasts'][name][key]['estimate'],key+'/contrast/'+name)
    return {'status':'passed','data_status':json.loads((run/'index.json').read_text())['data_status'],
            'allocation_rows_episodes_checked':sum(len(v) for v in calculated.values()),
            'complete_blocks':len(complete),'numeric_cross_checks':checks,
            'source_export_receipt_sha256':hashlib.sha256((run/'EXPORT.json').read_bytes()).hexdigest(),
            'report_tables_sha256':hashlib.sha256(canonical(tables).encode()).hexdigest(),
            'scope':'Independent arithmetic from logged executed district rows versus act-reconstructed outcomes; all cell means and point contrasts. Frozen bootstrap retained, not redefined.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=audit(a.run);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
