#!/usr/bin/env python3
"""Build compact exhibit data from a finished, verified evaluation export.

This does not publish, sample new episodes or alter the frozen analysis.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from report_results import summarize
from seventh_seat.analysis.run import analyze_run
from seventh_seat.analysis.episodes import load_scenario,phase_end_projections
from seventh_seat.analysis.contrasts import _percentile
from seventh_seat.observatory.snapshot import validate,CONTRACT
from seventh_seat.world.events import canonical,read_jsonl,sha256_hex
from seventh_seat.world.params import CELLS


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mean_interval(values,seed,resamples):
    if not values:return {'mean':None,'ci95':[None,None],'n':0}
    rng=random.Random(seed);n=len(values)
    draws=sorted(sum(values[rng.randrange(n)] for _ in range(n))/n for _ in range(resamples))
    return {'mean':sum(values)/n,'ci95':[_percentile(draws,2.5),_percentile(draws,97.5)],'n':n}


def export(run,output,*,fixture=False):
    run,output=Path(run).resolve(),Path(output).resolve()
    if output.exists() or output==run or run in output.parents:
        raise ValueError('exhibit export requires a new directory outside the source')
    expected_status='scripted-fixture' if fixture else 'experimental'
    index=json.loads((run/'index.json').read_text())
    if index.get('data_status')!=expected_status:
        raise ValueError('source status and requested exhibit status differ')
    tables=summarize(run)  # verifies every receipt digest and frozen analysis sources
    result=analyze_run(run)
    lock=json.loads((run/'lock.json').read_text())
    expected={f"eval-s{b['seed']}-{cell}" for b in lock['blocks'] for cell in b['cells']}
    if set(result['episodes'])!=expected or result['interrupted_without_manifest']:
        raise ValueError('unfinished or undeclared evaluation work remains')
    complete=set(result['blocks']['complete'])
    selected=next((b['seed'] for b in lock['blocks'] if any(e['scenario_id'] in complete and e.get('seed')==b['seed'] for e in result['episodes'].values())),None)
    snapshots=[];witness={};provenance={}
    for path in sorted(run.glob('s*/episodes/*/manifest.json')):
        m=json.loads(path.read_text())
        if m['status']!='completed':continue
        attempt=next(a for a in m['attempts'] if a['status']=='completed')
        log=path.parent/attempt['log'];records=read_jsonl(log);sc=load_scenario(records)
        executed=next(r for r in records if r['action']=='season_executed')
        truth=executed['result'];eid=m['episode_id']
        snap={'contract':CONTRACT,'episode_id':eid,'scenario_id':m['scenario_id'],
              'tick':executed['step'],'actors':[d['id'] for d in sc['districts']],
              'total_inflow':sc['F'],'withdrawals_by_actor':truth['withdrawals'],
              'downstream_flow':truth['downstream_flow'],'minimum_required_flow':sc['M'],
              'event_refs':[executed['event_id']]+[r['event_id'] for r in records if r['action']=='accept' and r['authorized']],
              'data_status':expected_status,'label':f"Seed {m['seed']} · {m['condition']}",
              'description':'Recorded final state. Not an event replay. Matched cells are separate model runs, not counterfactuals.'}
        provenance[eid]={'episode_manifest':str(path.relative_to(run)),'episode_manifest_sha256':digest(path),
                         'log':str(log.relative_to(run)),'log_sha256':digest(log),'log_head':attempt['log_head'],
                         'season_event_id':executed['event_id'],'season_event_hash':executed['hash'],
                         'snapshot_core_sha256':sha256_hex(canonical(snap)),'condition':m['condition']}
        snapshots.append(snap)
        if m['seed']==selected:
            rows=[{k:r.get(k) for k in ('event_id','phase','step','actor_id','action','args','authorized','reason','result','claim_text','evidence_refs','hash')}
                  for r in records if r['actor_id'] in snap['actors'] and r['action']!='model_call']
            projections=phase_end_projections(records,sc)
            witness[eid]={'episode_id':eid,'data_status':expected_status,'actors':snap['actors'],'events':rows,
                          'phase_end_truth':[{'phase':r['phase'],'event_id':r['event_id'],'event_hash':r['hash'],
                                              'projected_downstream_flow':projections[r['phase']],'minimum':sc['M']}
                                             for r in records if r['action']=='phase_end'],
                          'scope':'Observations and world actions for the first complete scenario in the locked worklist. Provider calls/state are omitted. Phase-end projections are reconstructed from authorized provisional plans; they are not final allocations.'}
    manifest={'contract':'seventh-seat/exhibit-export/v1','data_status':expected_status,
              'protocol_commit':lock['protocol_commit'],'source_export_receipt_sha256':digest(run/'EXPORT.json'),
              'source_lock_sha256':digest(run/'lock.json'),'episodes':provenance,
              'selection':'All evaluable final snapshots; witness detail uses the first complete scenario in locked order, never selected by outcome.'}
    mh=sha256_hex(canonical(manifest)+'\n')
    for snap in snapshots:
        p=provenance[snap['episode_id']]
        snap['provenance']={'manifest_sha256':mh,'log_head':p['log_head'],'season_event_hash':p['season_event_hash'],'condition':p['condition']}
        validate(snap)
    means={cell:mean_interval(tables['cells'][cell]['shortfall_values_complete_blocks'],lock['bootstrap_seed'],lock['bootstrap_resamples']) for cell in CELLS}
    summary={'data_status':expected_status,'interpretation':tables['interpretation'] if not fixture else 'scripted fixture; not research findings',
             'protocol_commit':lock['protocol_commit'],'manifest_sha256':mh,
             'planned_scenarios':len(lock['blocks']),'complete_scenarios':len(complete),
             'evaluable_episodes':tables['evaluable_episodes'],'missing_episodes':tables['missing_episodes'],
             'incomplete_scenarios':tables['incomplete_scenarios'],'cells':tables['cells'],
             'contrasts':tables['contrasts'],'descriptive':tables['descriptive'],
             'mean_shortfall_intervals_descriptive':means,'witness_seed':selected,'witness_episodes':sorted(witness),
             'episodes':[{k:v for k,v in e.items() if k in ('episode_id','scenario_id','condition','seed','stratum','status','evaluable')} for e in result['episodes'].values()],
             'notes':['Effects and means use complete scenario blocks; ladder counts use all evaluable episodes.',
                      'Mean intervals are descriptive scenario-bootstrap summaries, not additional hypothesis tests.',
                      'Reading evidence does not demonstrate understanding. The ladder and AWC do not identify causes.',
                      'AWC uses the disclosed conservative phase-end proxy and does not fully capture extra replan opportunities.',
                      'All snapshots are final recorded states. Matched reruns are not counterfactuals.']}
    source_table=[['Seat ring and positions','Metaphor only; simultaneous shared commons, no ordering or power encoded'],
                  ['Seventh seat fill height','max(0, minimum_required_flow - downstream_flow) / minimum_required_flow; zero when minimum is zero'],
                  ['Allocation bars','Exact final withdrawals and downstream flow; common zero-to-inflow linear scale within each pair'],
                  ['Final water values','season_executed.result and episode_start.args.scenario; event hashes in manifest.json'],
                  ['Effect estimates and intervals','Frozen analysis contrasts; 10000 complete-scenario bootstrap resamples'],
                  ['Mean shortfall and interval','Same complete-block shortfall values; descriptive mean bootstrap, locked seed/resample count'],
                  ['Ladder','Frozen descriptive first_failed_stage counts over all evaluable episodes; no-hazard episodes labelled separately'],
                  ['Agent view','Recorded observation.result and read_ledger.result; no claim of internal understanding'],
                  ['Agent claim','claim_text, displayed explicitly as a quotation'],
                  ['Agent action','Recorded action, args, authorized, reason and result'],
                  ['Phase-end truth','Frozen phase_end_projections recomputed from authorized plan/commit records; not executed allocations'],
                  ['Witness selection','First complete scenario in the locked worklist, all four cells'],
                  ['Missing data','Every planned but unevaluable episode retained; never drawn as zero']]
    output.mkdir(parents=True)
    def write(name,data):
        p=output/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(canonical(data)+'\n')
    write('manifest.json',manifest);write('summary.json',summary);write('snapshots.json',snapshots);write('source-table.json',source_table)
    for eid,data in witness.items():write(f'witness/{eid}.json',data)
    # Re-open every snapshot and verify its source-bound core and accounting.
    for snap in json.loads((output/'snapshots.json').read_text()):
        validate(snap)
        assert snap['provenance']['manifest_sha256']==mh
        assert sha256_hex(canonical({k:v for k,v in snap.items() if k!='provenance'}))==provenance[snap['episode_id']]['snapshot_core_sha256']
    files={str(p.relative_to(output)):{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(output.rglob('*')) if p.is_file()}
    receipt={'status':'local-exhibit-data-not-published','data_status':expected_status,'manifest_sha256':mh,
             'snapshots':len(snapshots),'witness_episodes':len(witness),'files':files,'total_bytes':sum(f['bytes'] for f in files.values())}
    write('EXHIBIT.json',receipt)
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--scripted-fixture',action='store_true')
    a=p.parse_args();r=export(a.run,a.output,fixture=a.scripted_fixture);print(json.dumps({k:v for k,v in r.items() if k!='files'},indent=2))
