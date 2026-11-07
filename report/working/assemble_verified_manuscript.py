"""Fill the report from verified computed tables; keeps the original draft intact."""
import argparse,json
from copy import deepcopy
from pathlib import Path

BASE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--tables',type=Path,required=True);p.add_argument('--pilot',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--layout-fixture',action='store_true')
a=p.parse_args();d=json.loads(a.tables.read_text());pilot=json.loads(a.pilot.read_text())
if not a.layout_fixture and (d['data_status']!='experimental' or pilot['data_status']!='experimental'):raise ValueError('experimental verified inputs required')
if d['complete_scenarios']<1:raise ValueError('no complete evaluation blocks; write a failure report, not an effect report')
m=json.loads((BASE/'manuscript.json').read_text());sections=dict(m['sections'])
qualification_detail=sections['3 Methods'][5]
sections['3 Methods'][5]='The selected configuration is GPT-6 Luna through the Responses API, with medium reasoning effort, no temperature setting and at most 4096 output tokens. Pre-experiment competence qualification selected the lower-cost candidate after both passed the disclosed gm-v2 tasks. Qualification does not prove optimal behaviour; Appendix B records the earlier failures and corrections.'
f=lambda n:f'{n:.2f}'
pct=lambda n:f'{100*n:.1f}%'
interval=lambda c:f"{c['estimate']:+.3g} [{c['ci95'][0]:+.3g}, {c['ci95'][1]:+.3g}]"
e=d['contrasts']['shortfall']['E'];s=d['contrasts']['shortfall']['S'];x=d['contrasts']['shortfall']['ExS']
confirm=d['interpretation']=='confirmatory'
cal='; '.join(f"kappa {b['kappa']}: {b['breaches']}/{b['evaluable']} breaches" for b in pilot['batches'])
reading=f"H1 was {d['hypotheses']['H1']}; H2 was {d['hypotheses']['H2']}." if confirm else 'Calibration did not meet its acceptance target, so all factorial results are descriptive and neither directional hypothesis is assessed confirmatorily.'
conclusion=(reading+' These measurements concern complete policy regimes with one qualified model configuration in a deliberately constructed synthetic world. They do not establish protection in deployed systems or adequate representation of real communities.')
m['abstract']=(f"We examine whether verified evidence and direct escalation help six language-model district agents protect an unrepresented downstream community in a synthetic watershed. A scenario-blocked factorial compares a basic register with verified aggregate projections, and peer-mediated reporting with direct access to a fixed scripted supervisor. Downstream harm is designed into the incentives, although it is unnecessary for meeting legitimate demand. A predeclared eight-scenario pilot selected demand pressure {d['calibrated_kappa']}; evaluation yielded {d['evaluable_episodes']} evaluable episodes and {d['complete_scenarios']} complete four-cell scenarios. The primary outcome is downstream shortfall reconstructed from engine records. The evidence contrast was {interval(e)} water units, and the reporting-route contrast was {interval(s)}; brackets give scenario-bootstrap 95% intervals. {reading} The exploratory interaction was {interval(x)}. Failed or omitted cells remain accounted for, refusal episodes remain included, and pilot observations are excluded. Process measures are descriptive and do not establish internal understanding. The findings characterize these institutional regimes in a deliberately limited world; they do not establish deployed safety or adequate representation of real communities.")
assert 150<=len(m['abstract'].split())<=250,len(m['abstract'].split())
for i,text in enumerate(sections['3 Methods']):
 text=text.replace('The final realized sample and calibrated setting remain pending.',f"Calibration retained kappa {d['calibrated_kappa']}; {d['complete_scenarios']} scenarios ultimately formed complete evaluation blocks.")
 sections['3 Methods'][i]=text
rows=[['Cell','N','Mean shortfall','Breach','Demand fulfilled']]
for cell,row in d['cells'].items():
 v=row['mean'];rows.append([cell,row['complete_block_episodes'],f(v['shortfall']),pct(v['breach']),pct(v['U'])])
effects=[['Contrast','Shortfall estimate [95% interval]'],['Evidence E',interval(e)],['Reporting route S',interval(s)],['Interaction E x S',interval(x)]]
sections['4 Results']=[f"Calibration followed the declared path: {cal}. The stopping decision was {pilot['decision']['status']}. Evaluation produced {d['evaluable_episodes']} evaluable episodes from {4*d['planned_scenarios']} planned episodes, with {d['complete_scenarios']} complete scenario blocks used in contrasts. {len(d['incomplete_scenarios'])} incomplete blocks and {len(d['missing_episodes'])} missing or unlaunched episodes are retained in the accounting.",
 {'table':rows,'widths':[1400,700,2500,2100,2660],'caption':'Table 1. Cell means use only complete scenario blocks. Shortfall is in water units; demand fulfilled is the fraction of legitimate demand met.'},
 {'table':effects,'widths':[3300,6060],'caption':f"Table 2. Within-scenario regime contrasts, averaged across {d['complete_scenarios']} complete blocks, with 10000 scenario-bootstrap percentile 95% intervals. Negative values indicate less shortfall. The interaction is exploratory; decisions use unrounded intervals."},
 reading,
 f"Zero shortfall occurred in {pct(d['zero_inflation']['share_of_zero_shortfall_overall'])} of all evaluable episodes. Provider refusals appeared in {d['refusals']['with_provider_refusal']} of {d['refusals']['episodes']} evaluable episodes; these episodes remain included. The preregistered refusal limitation flag was {'triggered' if d['refusals']['flagged'] else 'not triggered'}.",
 'Secondary contrasts, route-specific report counts, phase latencies, all-attempt call and invalid-action rates, and missingness are provided in Appendix B and the recomputable table bundle. The witness ladder and AWC remain descriptive; no pattern in those measures is interpreted as a causal mediation result.']
sections['5 Discussion and Limitations'][-1]=sections['5 Discussion and Limitations'][-1].replace('The empirical interpretation and any future-work priorities will be written after the outcomes are available.', 'The trade-disabled diagnostic H4 was not collected. A useful extension would validate the opportunity measure for replan rounds and test whether these regime contrasts transfer to other configurations and environments.')
sections['6 Conclusion']=[conclusion]
sections['LLM Usage Statement']=['Claude, Kimi, ChatGPT and Codex assisted planning, review, implementation, testing and drafting; the assistance log records their contributions. Inherited Friday work was preserved and reviewed. Automated tests and record-based checks supply specific verification evidence, not independent replication by assistants. Benjamin Amuwo is responsible for the final interpretation, review and submission.']
sections['Code and Data']=['The reviewed code checkpoint is '+d['protocol_commit']+'. Publication links and the author-approved licence must be inserted before submission. The curated local record bundle reproduces every reported statistic using scripts/report_results.py; it excludes provider caches, credentials and private budget databases. The tagged evaluation lock and freeze record identify the unchanged protocol and the disclosed administrative placement of freeze metadata.']
appendix=[f"The scientific source checkpoint is {d['protocol_commit']}. The tagged lock records exact seed/stratum assignments, randomized cell orders, prompt/tool/source hashes, model configuration, bootstrap seed and fixed stopping time. Calibration trace: {cal}. Pilot observations are excluded from the factorial.",
 'Status accounting: '+', '.join(f'{key} {value}' for key,value in sorted(d['episode_status_counts'].items()))+'.',
 'Missing or unlaunched episode IDs: '+(', '.join(d['missing_episodes']) if d['missing_episodes'] else 'none')+'.',
 'The administrative freeze record is stored separately from the pilot-hashed ERRATA file; no scientific design text was changed. AWC retains the explicitly disclosed conservative operationalization. The original records and all reported statistics remain independently recomputable.']
secondary=[['Outcome','E [95% interval]','S [95% interval]']]
for key in ('breach','U','unmet_min_need','alt_cost'):
 secondary.append([{'breach':'Breach fraction','U':'Demand fulfilled','unmet_min_need':'Unmet minimum need','alt_cost':'Alternative cost'}[key],interval(d['contrasts'][key]['E']),interval(d['contrasts'][key]['S'])])
appendix.append(qualification_detail)
appendix.append({'table':secondary,'widths':[2600,3380,3380],'caption':'Secondary contrasts. Breach and demand effects are fractions; unmet need is in water units and alternative cost in credits. Full exploratory interactions and process records are in report-tables.json.'})
for cell,row in d['cells'].items():
 appendix.append(f"{cell}: {row['evaluable']} evaluable episodes; no-commit rate {pct(row['all_evaluable_no_commit_rate']) if row['all_evaluable_no_commit_rate'] is not None else 'unavailable'}; {row['all_attempts_invalid_actions']} invalid of {row['all_attempts_action_count']} attempted world actions across all attempts. Call categories: "+', '.join(f'{k} {v}' for k,v in sorted(row['all_attempts_call_counts'].items()))+'.')
sections['Appendix B Reproducibility']=appendix
m['sections']=[[heading,sections[heading]] for heading,_ in m['sections']]
if a.layout_fixture:
 m['title']='SCRIPTED LAYOUT TEST'
 m['subtitle']='Not an experimental result or a submission'
 m['abstract']='SCRIPTED LAYOUT FIXTURE ONLY. '+m['abstract']
a.output.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'output':str(a.output),'abstract_words':len(m['abstract'].split()),'status':'computed manuscript awaiting author and layout review'}))
