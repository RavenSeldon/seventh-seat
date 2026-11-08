#!/usr/bin/env python3
"""Build the four-exhibit static release from verified local exhibit data. No deploy."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from seventh_seat.observatory.snapshot import validate,embed,prune_posters
from seventh_seat.world.events import canonical,sha256_hex
from build_release import THREE_FILES,IMPORTMAP,csp_for,git,RELEASE_LIMIT,FIRST_LOAD_LIMIT,ALLOWED


from presentation_assets import copy_assets,decorate

PRESENTATION_LIMIT=20*1024*1024

def build(data,output,three):
    data,output,three=Path(data).resolve(),Path(output).resolve(),Path(three)
    if output.exists() or output==data or data in output.parents:
        raise ValueError('release needs a new destination outside its source')
    receipt=json.loads((data/'EXHIBIT.json').read_text())
    if receipt.get('status')!='local-exhibit-data-not-published':raise ValueError('unrecognized exhibit receipt')
    allowed={'manifest.json','summary.json','snapshots.json','source-table.json'}
    for name,details in receipt['files'].items():
        if name not in allowed and not re.fullmatch(r'witness/eval-s[0-9]+-E[01]S[01]\.json',name):raise ValueError('unexpected exhibit file')
        p=data/name
        if not p.is_file() or p.is_symlink() or data not in p.resolve().parents:raise ValueError('unsafe exhibit path')
        if any(parent.is_symlink() for parent in p.parents if parent!=data):raise ValueError('symlinked exhibit path')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=details['sha256'] or p.stat().st_size!=details['bytes']:raise ValueError('exhibit receipt mismatch')
    if not allowed<=set(receipt['files']):raise ValueError('incomplete exhibit export')
    manifest=json.loads((data/'manifest.json').read_text());summary=json.loads((data/'summary.json').read_text());snaps=json.loads((data/'snapshots.json').read_text())
    mh=hashlib.sha256((data/'manifest.json').read_bytes()).hexdigest()
    if mh!=receipt['manifest_sha256'] or mh!=summary['manifest_sha256']:raise ValueError('manifest mismatch')
    if receipt['data_status'] not in ('scripted-fixture','experimental') or any(x['data_status']!=receipt['data_status'] for x in (manifest,summary)):raise ValueError('data status mismatch')
    for s in snaps:
        validate(s)
        if s['data_status']!=receipt['data_status'] or s['provenance']['manifest_sha256']!=mh:raise ValueError('snapshot provenance mismatch')
        if sha256_hex(canonical({k:v for k,v in s.items() if k!='provenance'}))!=manifest['episodes'][s['episode_id']]['snapshot_core_sha256']:raise ValueError('snapshot core mismatch')
    if len(snaps)!=receipt['snapshots'] or len(snaps)!=summary['evaluable_episodes']:raise ValueError('snapshot count mismatch')
    expected_witness={f'witness/{eid}.json' for eid in summary['witness_episodes']}
    if {n for n in receipt['files'] if n.startswith('witness/')}!=expected_witness:raise ValueError('witness set mismatch')
    selected=[s for s in snaps if s['episode_id'] in summary['witness_episodes']]
    if len(selected) not in (0,4):raise ValueError('witness selection must include all four matched cells')
    output.mkdir(parents=True)
    for name in [*receipt['files'],'EXHIBIT.json']:
        target=output/'data'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(data/name,target)
    for name in ('index.html','app.js'):shutil.copyfile(ROOT/'observatory/research'/name,output/name)
    copy_assets(output)
    htmls=[]
    paper=ROOT/'observatory/research/paper/index.html'
    if paper.is_file():
        (output/'paper').mkdir();shutil.copyfile(paper,output/'paper/index.html')
    if selected:
        html=(ROOT/'observatory/diorama/index.html').read_text();html=prune_posters(embed(html,selected),selected)
        pinned=re.search(r'https://cdn\.jsdelivr\.net/npm/three@([\d.]+)/',html)[1]
        if json.loads((three/'package.json').read_text())['version']!=pinned:raise ValueError('three.js pin mismatch')
        seven=output/'seven';seven.mkdir()
        for rel in [*THREE_FILES,'LICENSE']:
            dest=seven/'vendor'/f'three-{pinned}'/('LICENSE.txt' if rel=='LICENSE' else rel);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(three/rel,dest)
        base=f'./vendor/three-{pinned}/'
        imports=json.dumps({'imports':{'three':base+'build/three.module.min.js','three/addons/':base+'examples/jsm/'}})
        html=IMPORTMAP.sub(lambda m:f'{m[1]}{imports}{m[3]}',html,count=1)
        html=html.replace('<body>','<body><a href="../index.html#seven" style="display:block;padding:12px 24px;color:#ddbf78;background:#0c1318">← Return to the four exhibits</a>',1)
        if 'cdn.jsdelivr.net' in html:raise ValueError('external diorama request remains')
        (seven/'index.html').write_text(html)
    for path in ('index.html','paper/index.html','seven/index.html'):
        p=output/path
        if p.is_file():
            html=decorate(p.read_text(),path);p.write_text(html);htmls.append(html)
    files={}
    for p in sorted(output.rglob('*')):
        if not p.is_file():continue
        if p.suffix not in ALLOWED:raise ValueError('unsupported release type')
        blob=p.read_bytes();files[str(p.relative_to(output))]={'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob),'gzip':len(gzip.compress(blob,9))}
    first_names=['index.html','app.js','data/EXHIBIT.json','data/summary.json','data/snapshots.json','data/source-table.json','experience.js','experience.css','audio/playlist.json','icons/seal.svg','icons/icon-32.png']
    first=sum(files[n]['bytes'] for n in first_names)
    if selected:first=max(first,files['seven/index.html']['bytes'])
    total=sum(f['bytes'] for f in files.values())
    has_audio=any(Path(n).suffix.lower() in ('.mp3','.m4a','.aac','.ogg') for n in files)
    limit=PRESENTATION_LIMIT if has_audio else RELEASE_LIMIT
    if total>limit or first>FIRST_LOAD_LIMIT:raise ValueError('release exceeds hosting limits')
    release={'kind':'four-exhibit-local-release','data_status':receipt['data_status'],'commit':git('rev-parse','HEAD') or None,
             'working_tree_clean':not bool(git('status','--porcelain')),'total_bytes':total,'first_load':{'bytes':first,'files':first_names},
             'content_security_policy':csp_for('\n'.join(htmls)), 'files':files,
             'publication_status':'not-deployed','exhibit_manifest_sha256':mh}
    encoded=json.dumps(release,indent=2)+'\n'
    # RELEASE.json is part of the transfer/disk budget too, even though it cannot hash itself.
    release['total_bytes_excluding_self']=total
    for _ in range(4):
        encoded=json.dumps(release,indent=2)+'\n';release['total_bytes']=total+len(encoded.encode())
    encoded=json.dumps(release,indent=2)+'\n'
    if release['total_bytes']>limit:raise ValueError('release including manifest exceeds hosting limit')
    (output/'RELEASE.json').write_text(encoded)
    return release

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--three-dir',type=Path,default=ROOT/'observatory/diorama/node_modules/three')
    a=p.parse_args();r=build(a.data,a.output,a.three_dir);print(json.dumps({k:v for k,v in r.items() if k!='files'},indent=2))
