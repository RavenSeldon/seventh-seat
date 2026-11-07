'use strict';
(() => {
const $=id=>document.getElementById(id), cells=['E0S0','E0S1','E1S0','E1S1'];
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=x=>x==null?'unavailable':Number(x).toLocaleString('en',{maximumSignificantDigits:4});
const table=(headers,rows,caption='')=>`<table>${caption?`<caption>${esc(caption)}</caption>`:''}<thead><tr>${headers.map(h=>`<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(x=>`<td>${esc(x)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
const options=(el,values)=>{el.replaceChildren(...values.map(([v,label])=>{const o=document.createElement('option');o.value=v;o.textContent=label;return o;}));};
let receipt,summary,snapshots;const cache=new Map();let witnessRequest=0;
async function verified(name){
 if(cache.has(name))return cache.get(name);
 if(!receipt.files[name])throw Error(`File absent from export receipt: ${name}`);
 const response=await fetch('data/'+name,{cache:'no-store'});if(!response.ok)throw Error(`Cannot load ${name}`);
 const bytes=await response.arrayBuffer();const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
 if(hash!==receipt.files[name].sha256)throw Error(`Export digest mismatch: ${name}`);
 const data=JSON.parse(new TextDecoder().decode(bytes));cache.set(name,data);return data;
}
function shortfall(s){return Math.max(0,s.minimum_required_flow-s.downstream_flow);}
function water(s,scale=s.total_inflow){
 const width=340,base=110,x=v=>base+v/scale*width;
 const values=[...s.actors.map(a=>[a,s.withdrawals_by_actor[a]]),['Downstream',s.downstream_flow]];
 const body=values.map(([label,v],i)=>`<text x="0" y="${31+i*36}" fill="#b0b1bb" font-size="13">${esc(label)}</text><rect data-value="${v}" x="${base}" y="${18+i*36}" width="${v/scale*width}" height="18" fill="${i===6?'#d0bce9':'#51dbea'}"/><text x="${x(v)+7}" y="${31+i*36}" fill="#f1f0ed" font-size="13">${num(v)}</text>`).join('');
 return `<svg class="water" viewBox="0 0 510 290" role="img" aria-label="Water allocations for ${esc(s.episode_id)}"><title>Water allocations; bars use a shared zero to ${scale} unit scale</title>${body}<line x1="${x(s.minimum_required_flow)}" x2="${x(s.minimum_required_flow)}" y1="227" y2="259" stroke="#f1f0ed" stroke-width="2"/></svg><p class="muted">Downstream tick: minimum ${num(s.minimum_required_flow)}. Bar scale: 0–${scale} water units.</p><details><summary>Water allocations as a table</summary>${table(['Destination','River water'],values)}</details>`;
}
function reading(s){return `<h3>${esc(s.label)}</h3><div class="numbers"><div><strong>${num(s.downstream_flow)}</strong><span>Downstream flow</span></div><div><strong>${num(s.minimum_required_flow)}</strong><span>Required minimum</span></div><div><strong>${num(shortfall(s))}</strong><span>Shortfall</span></div></div>${water(s)}<p class="muted">Balance: ${num(s.total_inflow)} inflow − ${num(Object.values(s.withdrawals_by_actor).reduce((a,b)=>a+b,0))} withdrawals = ${num(s.downstream_flow)} downstream.</p>`;}
function showEpisode(){
 const s=snapshots.find(x=>x.episode_id===$('episode').value);if(!s)return;
 const percent=s.minimum_required_flow?shortfall(s)/s.minimum_required_flow:0;
 const seats=s.actors.map((a,i)=>{const angle=(i*360/7-90)*Math.PI/180,x=200+128*Math.cos(angle),y=180+128*Math.sin(angle);return `<g><circle cx="${x}" cy="${y}" r="29" fill="#11262b" stroke="#51dbea"/><text x="${x}" y="${y-2}" text-anchor="middle" fill="#f1f0ed" font-size="13">${esc(a)}</text><text x="${x}" y="${y+14}" text-anchor="middle" fill="#b0b1bb" font-size="12">${num(s.withdrawals_by_actor[a])}</text></g>`;}).join('');
 const angle=(6*360/7-90)*Math.PI/180,x=200+128*Math.cos(angle),y=180+128*Math.sin(angle);
 $('ring').innerHTML=`<svg class="ring" viewBox="0 0 400 360" role="img" aria-label="Six district seats and the downstream seat. Shortfall ${shortfall(s)} of minimum ${s.minimum_required_flow}."><title>Final recorded state, not a replay</title><circle cx="200" cy="180" r="128" fill="none" stroke="#383941"/><text x="200" y="175" text-anchor="middle" fill="#51dbea" font-size="19">The shared commons</text><text x="200" y="200" text-anchor="middle" fill="#b0b1bb" font-size="13">${num(s.total_inflow)} water units</text>${seats}<defs><clipPath id="seventh-clip"><circle cx="${x}" cy="${y}" r="29"/></clipPath></defs><circle cx="${x}" cy="${y}" r="29" fill="#101115" stroke="#d0bce9"/><rect x="${x-29}" y="${y+29-58*percent}" width="58" height="${58*percent}" fill="#b5465f" clip-path="url(#seventh-clip)"/><text x="${x}" y="${y+5}" text-anchor="middle" fill="#ffffff" font-size="14">VII</text></svg><p class="muted">District numbers: river withdrawals. Seventh seat fill height: ${num(percent*100)}% of the required minimum unmet. Positions and the ring are metaphor; size does not encode district power.</p>`;
 $('reading').innerHTML=reading(s);$('snapshot').textContent=JSON.stringify(s,null,2);
}
const stages=[['1','No recorded hazard','#6b6e7d'],['2','Evidence','#9d86d4'],['3','Access','#7f9fe6'],['4','Evidence-bearing concern','#51c4d6'],['5','Escalation','#8fd3a6'],['6','Intervention','#e1be83'],['7','Outcome','#ee7f86'],['None','All stages recorded','#e8e4f4']];
function showLadder(){
 const counts=summary.descriptive.witness_ladder_first_failed_stage_by_cell;
 $('ladder-bars').innerHTML=cells.map(c=>{const n=summary.cells[c].evaluable;return `<div class="ladder-row"><span>${c}</span><div class="stack" role="img" aria-label="${esc(c+': '+stages.map(([k,l])=>l+' '+(counts[c][k]||0)).join('; '))}">${stages.map(([k,l,color])=>`<span data-stage="${k}" data-count="${counts[c][k]||0}" style="width:${n?100*(counts[c][k]||0)/n:0}%;background:${color}" title="${esc(l)}: ${counts[c][k]||0}"></span>`).join('')}</div><span>N=${n}</span></div>`;}).join('');
 $('ladder-legend').innerHTML=stages.map(([,label,color])=>`<span><i class="swatch" style="background:${color}"></i>${label}</span>`).join('');
 $('ladder-table').innerHTML=table(['Category',...cells],stages.map(([k,l])=>[l,...cells.map(c=>counts[c][k]||0)]),'All evaluable episodes; exact counts');
 const rows=cells.map(c=>{const v=summary.mean_shortfall_intervals_descriptive[c];return[c,num(v.mean),v.mean==null?'unavailable':`[${num(v.ci95[0])}, ${num(v.ci95[1])}]`,v.n];});
 $('means').innerHTML=table(['Cell','Mean','95% interval','N'],rows);
 $('contrasts').innerHTML=table(['Contrast','Estimate','95% interval','N scenarios'],Object.entries(summary.contrasts.shortfall).map(([k,v])=>[k==='ExS'?'E × S (exploratory)':k,num(v.estimate),v.estimate==null?'unavailable':`[${num(v.ci95[0])}, ${num(v.ci95[1])}]`,v.blocks]),`${summary.interpretation}; complete scenarios only`);
 $('missing').innerHTML=`<p>${summary.missing_episodes.length} missing / unevaluable episodes; ${summary.incomplete_scenarios.length} incomplete scenarios excluded from contrasts.</p><pre>${esc(JSON.stringify({missing_episodes:summary.missing_episodes,incomplete_scenarios:summary.incomplete_scenarios},null,2))}</pre>`;
 $('awc').innerHTML=table(['Cell','Mean AWC at hazard onset'],cells.map(c=>[c,num(summary.descriptive.awc_at_hazard_onset_by_cell[c])]),'Descriptive; episodes without recorded hazard excluded');
}
async function showWitness(){
 const request=++witnessRequest,eid=$('witness-episode').value,actor=$('actor').value;const target=$('witness-content');target.textContent='Verifying witness file…';
 try{
  const data=await verified(`witness/${eid}.json`);if(request!==witnessRequest)return;
  const events=data.events.filter(e=>e.actor_id===actor);
  const rows=events.map(e=>{
   const isView=e.action==='observation'||e.action==='read_ledger';
   return `<details class="record-event"><summary><span class="badge">${esc(e.phase)} · ${esc(e.event_id)}</span><span class="event-name">${esc(e.action.replaceAll("_"," "))}</span></summary><article class="event"><span class="badge">${esc(e.phase)} · event ${e.event_id}</span><h3>${esc(e.action)}</h3>${isView?`<h4>Recorded view</h4><details><summary>Inspect the information returned</summary><pre>${esc(JSON.stringify(e.result,null,2))}</pre></details>`:''}${e.claim_text?`<h4>Agent claim · quotation</h4><blockquote>“${esc(e.claim_text)}”</blockquote>`:''}<h4>${e.action==='observation'?'Observation delivery':'Recorded act'}</h4><p>${e.action==='observation'?'Information supplied to the district; not a submitted action.':(e.authorized?'Authorized':'Not authorized')}${e.reason?` · ${esc(e.reason)}`:''}</p><details><summary>Arguments and result</summary><pre>${esc(JSON.stringify({args:e.args,result:e.result,evidence_refs:e.evidence_refs},null,2))}</pre></details><code class="hash">Event hash ${esc(e.hash)}</code></article></details>`;
  }).join('');
  target.innerHTML=`<h3>${esc(eid)} · ${esc(actor)}</h3><p class="muted">${esc(data.scope)}</p><div class="card"><h3>Evaluator truth · phase end</h3><p>Authorized provisional plans, reconstructed at phase end. This is not necessarily what the district saw or what was finally executed.</p><div class="scroll">${table(['Phase','Projected downstream','Minimum','Source event'],data.phase_end_truth.map(r=>[r.phase,num(r.projected_downstream_flow),num(r.minimum),r.event_id]))}</div><p class="muted">Exact event hashes are retained in the <a href="data/witness/${encodeURIComponent(eid)}.json">source witness file</a>.</p></div>${rows||'<p>No recorded events for this district.</p>'}`;
 }catch(e){if(request===witnessRequest){target.textContent='Witness record unavailable: '+e.message;target.classList.add('error');}}
}
function resetWitness(){witnessRequest++;$('witness-content').textContent='Selection changed. Load this district’s record.';}
function showRivers(){
 if($('left-cell').value===$('right-cell').value)$('right-cell').value=cells.find(c=>c!==$('left-cell').value);
 const scenario=$('scenario').value,entries=summary.episodes.filter(e=>e.scenario_id===scenario),available=snapshots.filter(s=>s.scenario_id===scenario),scale=Math.max(...available.map(s=>s.total_inflow),1);
 $('river-pair').innerHTML=['left-cell','right-cell'].map(id=>{const c=$(id).value,s=available.find(s=>s.provenance.condition===c),entry=entries.find(e=>e.condition===c);return `<div class="card"><p class="eyebrow">Matched rerun · ${c}</p>${s?`<h3>${esc(s.episode_id)}</h3>${water(s,scale)}<p>Downstream ${num(s.downstream_flow)} · minimum ${num(s.minimum_required_flow)} · shortfall ${num(shortfall(s))} water units.</p><code class="hash">Source event ${esc(s.provenance.season_event_hash)}</code>`:`<h3>Missing record</h3><p>${esc(entry?.episode_id||scenario+'-'+c)}: ${esc(entry?.status||'not available')}. No zero or allocation is imputed.</p>`}</div>`;}).join('');
}
async function init(){
 try{
  const r=await fetch('data/EXHIBIT.json',{cache:'no-store'});if(!r.ok)throw Error('No exhibit export');receipt=await r.json();
  [summary,snapshots]=await Promise.all([verified('summary.json'),verified('snapshots.json')]);
  if(!['experimental','scripted-fixture'].includes(receipt.data_status)||summary.data_status!==receipt.data_status||snapshots.some(s=>s.data_status!==receipt.data_status||s.provenance.manifest_sha256!==receipt.manifest_sha256))throw Error('Inconsistent data status or manifest');
  $('status').innerHTML=`<strong>${receipt.data_status==='scripted-fixture'?'SCRIPTED FIXTURE · NOT RESEARCH FINDINGS':'Experimental records · verified export'}</strong>${summary.evaluable_episodes} evaluable episodes · ${summary.complete_scenarios}/${summary.planned_scenarios} complete scenarios · ${summary.missing_episodes.length} missing / unevaluable episodes.`;
  options($('episode'),snapshots.map(s=>[s.episode_id,s.label]));
  if(snapshots.length)showEpisode();else{$('ring').textContent='No evaluable snapshots.';$('reading').textContent='Allocations unavailable.';}
  $('episode').addEventListener('change',showEpisode);showLadder();
  options($('witness-episode'),summary.witness_episodes.map(e=>[e,e]));options($('actor'),['D1','D2','D3','D4','D5','D6'].map(a=>[a,a]));
  $('load-witness').disabled=!summary.witness_episodes.length;
  if(!summary.witness_episodes.length){$('witness-content').textContent='No complete scenario: witness detail unavailable.';$('diorama-link').hidden=true;}
  $('load-witness').addEventListener('click',showWitness);$('witness-episode').addEventListener('change',resetWitness);$('actor').addEventListener('change',resetWitness);
  options($('scenario'),[...new Set(summary.episodes.map(e=>e.scenario_id))].map(s=>[s,s]));for(const id of ['left-cell','right-cell'])options($(id),cells.map(c=>[c,c]));$('right-cell').value='E1S1';
  for(const id of ['scenario','left-cell','right-cell'])$(id).addEventListener('change',showRivers);showRivers();
  const sources=await verified('source-table.json');$('source-table').innerHTML=table(['Mark or description','Source'],sources);
  $('provenance').innerHTML=`<p>Protocol commit <code>${esc(summary.protocol_commit)}</code></p><code class="hash">Exhibit manifest SHA-256 ${esc(summary.manifest_sha256)}</code>`;
  const finding=$('finding');
  if(finding&&summary.data_status==='experimental'){
   const effects=['E','S'].map(k=>summary.contrasts.shortfall[k]);
   const includesZero=effects.every(v=>v.estimate!==null&&v.ci95[0]<=0&&v.ci95[1]>=0);
   finding.innerHTML=`<p class="eyebrow">What the experiment found</p><p><strong>${includesZero?'Both primary effect intervals include zero.':'Read both primary effects with their uncertainty.'}</strong> ${includesZero&&summary.interpretation==='confirmatory'?'Neither directional hypothesis met the preregistered support rule. ':''}These results concern one synthetic world and one model configuration. <a href="#ladder">Inspect the estimates and intervals ↓</a></p>`;
   finding.hidden=false;
  }
  $('content').hidden=false;document.documentElement.dataset.ready='true';
 }catch(e){$('status').textContent='Exhibit unavailable: '+e.message+'. No results are drawn.';$('status').classList.add('error');document.documentElement.dataset.failed='true';}
}
init();
})();
