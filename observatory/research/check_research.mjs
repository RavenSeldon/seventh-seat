// Offline fixture acceptance: source values, missingness, lazy witnesses, escaping,
// mobile access, 3D selection and release CSP. Never calls a model or publishes.
import {chromium} from '../diorama/node_modules/playwright/index.mjs';
import fs from 'node:fs';import path from 'node:path';import http from 'node:http';
const arg=k=>{const i=process.argv.indexOf(k);return i>=0?process.argv[i+1]:null;};
const root=path.resolve(arg('--release')??'');if(!arg('--release'))throw Error('--release required');
const shots=arg('--shots');if(shots)fs.mkdirSync(shots,{recursive:true});
const release=JSON.parse(fs.readFileSync(path.join(root,'RELEASE.json'),'utf8'));
const summary=JSON.parse(fs.readFileSync(path.join(root,'data/summary.json'),'utf8'));
const snaps=JSON.parse(fs.readFileSync(path.join(root,'data/snapshots.json'),'utf8'));
const experimental=process.argv.includes('--experimental');
if(release.data_status!==(experimental?'experimental':'scripted-fixture'))throw Error('Release status does not match explicit check mode');
const format=x=>x==null?'unavailable':Number(x).toLocaleString('en',{maximumSignificantDigits:4});
const types={'.html':'text/html','.js':'text/javascript','.json':'application/json','.txt':'text/plain'};
const server=http.createServer((req,res)=>{
 const name=decodeURIComponent(new URL(req.url,'http://local').pathname),file=path.resolve(root,'.'+(name.endsWith('/')?name+'index.html':name));
 if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||fs.statSync(file).isDirectory()){res.writeHead(404);res.end();return;}
 res.writeHead(200,{'content-type':types[path.extname(file)]??'application/octet-stream','content-security-policy':release.content_security_policy,'x-content-type-options':'nosniff'});fs.createReadStream(file).pipe(res);
});await new Promise(r=>server.listen(0,'127.0.0.1',r));
const origin=`http://127.0.0.1:${server.address().port}`;let failures=0,passed=0;const errors=[],external=[];
function check(ok,msg){console.log(`${ok?'ok':'FAIL'} ${msg}`);ok?passed++:failures++;}
const browser=await chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-webgl']});
async function open(viewport={width:1440,height:1000}){
 const ctx=await browser.newContext({viewport,reducedMotion:'reduce'}),page=await ctx.newPage();
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(/Content Security Policy|Refused to/i.test(m.text()))errors.push(m.text());});
 await page.route('**/*',route=>{const url=new URL(route.request().url());if(url.origin!==origin){external.push(url.href);return route.abort();}return route.continue();});
 return{ctx,page};
}
try{
 const{ctx,page}=await open();const requests=[];page.on('request',r=>requests.push(r.url()));
 await page.goto(origin);await page.waitForFunction(()=>document.documentElement.dataset.ready==='true');
 check((await page.locator('#status').innerText()).includes(experimental?'Experimental records · verified export':'SCRIPTED FIXTURE · NOT RESEARCH FINDINGS'),'data status is explicit');
 check(await page.locator('main section').count()===5,'four exhibits and source section present');
 check(!requests.some(x=>x.includes('/witness/')),'witness details are not loaded on entry');
 check(!requests.some(x=>x.includes('/vendor/')),'3D library is not loaded on entry');
 for(const s of snaps){
  await page.selectOption('#episode',s.episode_id);
  const source=JSON.parse(await page.locator('#snapshot').textContent());check(JSON.stringify(source)===JSON.stringify(s),`${s.episode_id}: exact snapshot shown`);
  const bars=await page.locator('#reading rect[data-value]').evaluateAll(nodes=>nodes.map(n=>({value:Number(n.dataset.value),width:Number(n.getAttribute('width'))})));
  const expected=[...s.actors.map(a=>s.withdrawals_by_actor[a]),s.downstream_flow];
  check(bars.length===7&&bars.every((b,i)=>b.value===expected[i]&&Math.abs(b.width-expected[i]/s.total_inflow*340)<1e-7),`${s.episode_id}: drawn water widths agree with record`);
 }
 for(const [i,cell]of ['E0S0','E0S1','E1S0','E1S1'].entries()){
  const counts=await page.locator('.ladder-row').nth(i).locator('[data-stage]').evaluateAll(nodes=>Object.fromEntries(nodes.map(n=>[n.dataset.stage,Number(n.dataset.count)])));
  check(Object.entries(summary.descriptive.witness_ladder_first_failed_stage_by_cell[cell]).every(([k,v])=>counts[k]===v)&&Object.values(counts).reduce((a,b)=>a+b,0)===summary.cells[cell].evaluable,`${cell}: ladder counts and N agree`);
 }
 const meansText=await page.locator('#means').innerText();
 check(Object.values(summary.mean_shortfall_intervals_descriptive).every(v=>meansText.includes(v.mean==null?'unavailable':`[${format(v.ci95[0])}, ${format(v.ci95[1])}]`)),'mean shortfall intervals retained');
 check((await page.locator('#contrasts').innerText()).includes('95% interval'),'effect intervals accompany estimates');
 const incomplete=summary.incomplete_scenarios[0];
 if(incomplete){
  await page.selectOption('#scenario',incomplete.scenario_id);await page.selectOption('#left-cell',['E0S0','E0S1','E1S0','E1S1'].find(c=>c!==incomplete.missing_cells[0]));await page.selectOption('#right-cell',incomplete.missing_cells[0]);
  const missing=page.locator('#river-pair .card').nth(1);check((await missing.innerText()).includes('Missing record')&&await missing.locator('svg').count()===0,'missing cell never drawn as zero');
 }else check(summary.missing_episodes.length===0,'no missing episodes omitted from comparison');
 await page.selectOption('#left-cell',await page.locator('#right-cell').inputValue());check(await page.locator('#left-cell').inputValue()!==await page.locator('#right-cell').inputValue(),'matched comparison uses distinct cells');
 const witnessId=summary.witness_episodes[0];
 if(witnessId){
  const witness=JSON.parse(fs.readFileSync(path.join(root,`data/witness/${witnessId}.json`),'utf8'));
  await page.selectOption('#witness-episode',witnessId);await page.selectOption('#actor','D1');await page.click('#load-witness');
  await page.waitForFunction(()=>document.querySelector('#witness-content').textContent.includes('Evaluator truth · phase end'));
  const claims=witness.events.filter(e=>e.actor_id==='D1'&&e.claim_text);
  check(await page.locator('#witness-content blockquote').count()===claims.length,'only selected actor claims displayed as quotations');
  if(!experimental){
   check((await page.locator('#witness-content blockquote').innerText()).includes('<img src=x onerror=alert(1)>'),'agent claim displayed literally as quotation');
   check(await page.locator('#witness-content img').count()===0,'agent HTML cannot become page markup');
   check((await page.locator('#witness-content').innerText()).includes('Observation delivery'),'recorded view distinguished from submitted act');
  }
  check((await page.locator('#witness-content').innerText()).includes('Evaluator truth · phase end'),'phase-end truth scope explicit');
  await page.selectOption('#actor','D2');check((await page.locator('#witness-content').innerText()).includes('Selection changed'),'selection clears stale witness detail');
  await page.click('#load-witness');await page.waitForFunction(()=>document.querySelector('#witness-content').textContent.includes('· D2'));
  check(await page.locator('#witness-content blockquote').count()===witness.events.filter(e=>e.actor_id==='D2'&&e.claim_text).length,'different actor shows only its own claims');
 }
 check((await page.locator('#source-table').innerText()).includes('Seventh seat fill height'),'source table maps seventh-seat mark');
 if(shots){
  await page.selectOption('#episode',snaps[0].episode_id);
  console.log('Screenshot document height: '+await page.evaluate(()=>document.documentElement.scrollHeight));
  // Real witness transcripts can exceed Chromium's full-page bitmap limit.
  // Capture readable viewports, retaining the loaded witness for review.
  await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(shots,'desktop.png')});
  for(const id of ['seven','ladder','witness','rivers','sources']){
   await page.locator('#'+id).scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(shots,'desktop-'+id+'.png')});
  }
 }
 await page.goto(origin+'/seven/');await page.waitForFunction(()=>!!window.__diorama);
 check(await page.locator('#fixture-seg button').count()===4,'diorama includes all four preselected matched cells');
 for(const s of snaps.filter(s=>summary.witness_episodes.includes(s.episode_id))){
  const index=await page.evaluate(eid=>window.__diorama.snapshots.findIndex(s=>s.episode_id===eid),s.episode_id);
  await page.click('#fixture-'+index);check((await page.evaluate(()=>window.__diorama.current())).episode_id===s.episode_id,`${s.episode_id}: 3D source switches honestly`);
 }
 check((await page.locator('body').innerText()).includes('Return to the four exhibits'),'diorama returns to research hub');
 await ctx.close();
 const mobile=await open({width:390,height:844});await mobile.page.goto(origin);await mobile.page.waitForFunction(()=>document.documentElement.dataset.ready==='true');
 check(await mobile.page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'phone has no page-level sideways scrolling');
 check(await mobile.page.locator('select,button').evaluateAll(ns=>ns.every(n=>n.getBoundingClientRect().height>=44)),'phone controls meet 44px touch targets');
 await mobile.page.keyboard.press('Tab');check(await mobile.page.locator('.skip').evaluate(e=>e===document.activeElement),'keyboard skip link reachable first');
 if(shots){await mobile.page.screenshot({path:path.join(shots,'phone-top.png')});for(const id of ['seven','ladder','witness','rivers','sources'])await mobile.page.locator('#'+id).screenshot({path:path.join(shots,'phone-'+id+'.png')});}await mobile.ctx.close();
 const broken=await open();await broken.page.route('**/data/summary.json',route=>route.fulfill({contentType:'application/json',body:'{}'}));await broken.page.goto(origin);await broken.page.waitForFunction(()=>document.documentElement.dataset.failed==='true');
 check(await broken.page.locator('#content').isHidden(),'digest mismatch prevents any results being drawn');await broken.ctx.close();
 check(external.length===0,'zero third-party requests');check(errors.length===0,'no browser errors or CSP violations');
 console.log(JSON.stringify({passed,failures,external,errors},null,2));
}finally{await browser.close();await new Promise(r=>server.close(r));}
if(failures)process.exitCode=1;
