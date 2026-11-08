/* Optional soundtrack and inline diorama. Rushii / SchroCiv Tale mechanics, adapted for static research pages. */
(() => {
'use strict';
const script=document.currentScript,base=new URL('.',script.src);
// An embedded diorama uses the parent's uninterrupted soundtrack.
if(window.self!==window.top)return;
const root=document.createElement('div');root.className='soundtrack';
root.innerHTML='<button class="music-toggle" type="button" aria-label="Play background music" aria-pressed="false" disabled title="Background music"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6 5.6 18.4"/><circle cx="12" cy="12" r="2.2"/></svg><span>Music</span></button><details class="music-options"><summary aria-label="Music settings">Settings</summary><div class="music-panel"><p class="music-status" role="status">Loading soundtrack list…</p><label>Volume <input class="music-volume" aria-label="Music volume" type="range" min="0" max="1" step="0.05" value="0.4"></label><button class="music-next" type="button" disabled>Next track</button><p class="music-note">Optional soundtrack, not experimental evidence. Audio downloads only after you press play.</p></div></details>';
document.body.append(root);
const toggle=root.querySelector('.music-toggle'),status=root.querySelector('.music-status'),next=root.querySelector('.music-next'),volume=root.querySelector('input');
const el=document.createElement('audio');el.preload='none';el.hidden=true;el.volume=.4;document.body.append(el);
let tracks=[],index=0,timer=null,want=false,token=0,restore=0,lastSaved=0;
const key='seventh-seat-soundtrack-v1';
let prior={};try{prior=JSON.parse(sessionStorage.getItem(key))||{};}catch{}
if(Number.isFinite(prior.volume)){el.volume=Math.max(0,Math.min(1,prior.volume));volume.value=el.volume;}
function save(){if(!tracks.length)return;try{sessionStorage.setItem(key,JSON.stringify({file:tracks[index],time:el.currentTime,volume:el.volume}));}catch{}}
function reflect(){const playing=want&&!el.paused&&!el.ended;toggle.setAttribute('aria-pressed',String(playing));toggle.setAttribute('aria-label',playing?'Pause background music':'Play background music');root.classList.toggle('is-playing',playing);}
function label(){return tracks[index].replace(/\.[^.]+$/,'').replace(/_/g,' ');}
function load(){el.src=new URL('audio/'+tracks[index],base).href;}
async function play(){const attempt=++token;want=true;clearTimeout(timer);if(!el.getAttribute('src'))load();status.textContent='Loading · '+label();try{await el.play();if(attempt!==token){if(!want)el.pause();return;}status.textContent='Playing · '+label();reflect();}catch{if(attempt!==token)return;want=false;reflect();status.textContent='Playback could not start. Press play to retry, or try the next track.';}}
function pause(){++token;want=false;clearTimeout(timer);el.pause();save();reflect();status.textContent='Paused · '+label();}
function advance(){if(!tracks.length)return;const resume=want;pause();index=(index+1)%tracks.length;restore=0;load();save();status.textContent='Ready · '+label();if(resume)play();}
toggle.addEventListener('click',()=>{if(want)pause();else play();});next.addEventListener('click',advance);
volume.addEventListener('input',()=>{el.volume=Number(volume.value);save();});
el.addEventListener('loadedmetadata',()=>{if(restore>0&&restore<el.duration)el.currentTime=restore;restore=0;});
el.addEventListener('playing',()=>{if(!want){el.pause();return;}status.textContent='Playing · '+label();reflect();});
el.addEventListener('pause',reflect);
el.addEventListener('error',()=>{++token;want=false;clearTimeout(timer);reflect();status.textContent='This track could not load. Try the next track.';});
el.addEventListener('timeupdate',()=>{if(Date.now()-lastSaved>4000){save();lastSaved=Date.now();}});
el.addEventListener('ended',()=>{const resume=want,wrapped=index===tracks.length-1;index=(index+1)%tracks.length;restore=0;load();save();reflect();if(resume){status.textContent=wrapped?'A short pause before the playlist repeats…':'Loading next track…';timer=setTimeout(()=>{if(want)play();},wrapped?3000:0);}});
addEventListener('pagehide',()=>{save();clearTimeout(timer);});
fetch(new URL('audio/playlist.json',base)).then(r=>{if(!r.ok)throw Error();return r.json();}).then(list=>{
 if(!Array.isArray(list)||list.some(n=>typeof n!=='string'||! /^[A-Za-z0-9][A-Za-z0-9._-]*\.(mp3|m4a|aac|ogg)$/i.test(n)))throw Error();
 tracks=list;if(!tracks.length){root.remove();el.remove();return;}
 const previous=tracks.indexOf(prior.file);if(previous>=0){index=previous;restore=Number.isFinite(prior.time)?Math.max(0,prior.time):0;}
 toggle.disabled=false;next.disabled=tracks.length<2;status.textContent='Ready · '+label();
}).catch(()=>{status.textContent='Soundtrack unavailable. The research remains fully usable.';});
const entrance=document.getElementById('diorama-link');
if(entrance){
 const panel=document.createElement('div');panel.id='inline-diorama';panel.className='inline-diorama';panel.hidden=true;
 const bar=document.createElement('div');bar.className='inline-diorama-tools';
 const close=document.createElement('button');close.type='button';close.textContent='Close diorama';
 const full=document.createElement('a');full.href=entrance.href;full.textContent='Open standalone view ↗';full.target='_blank';full.rel='noopener noreferrer';
 bar.append(close,full);panel.append(bar);entrance.after(panel);entrance.setAttribute('aria-expanded','false');entrance.setAttribute('aria-controls',panel.id);
 entrance.addEventListener('click',event=>{if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();if(panel.querySelector('iframe')){close.focus();return;}
 const frame=document.createElement('iframe');frame.src=entrance.href;frame.title='Seventh Seat interactive diorama: four matched experimental cells';frame.allowFullscreen=true;panel.append(frame);panel.hidden=false;entrance.setAttribute('aria-expanded','true');close.focus();});
 close.addEventListener('click',()=>{panel.querySelector('iframe')?.remove();panel.hidden=true;entrance.setAttribute('aria-expanded','false');entrance.focus();});
}
})();
