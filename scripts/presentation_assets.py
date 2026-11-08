"""Seal metadata, optional soundtrack, and shared static presentation assets."""
from pathlib import Path
import json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
TRACK=re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*\.(mp3|m4a|aac|ogg)$',re.I)
def copy_assets(output):
    source=ROOT/'observatory/research';output=Path(output)
    shutil.copytree(source/'icons',output/'icons')
    for name in ('experience.js','experience.css'):shutil.copyfile(source/name,output/name)
    target=output/'audio';target.mkdir();tracks=[]
    for p in sorted((source/'audio').iterdir(),key=lambda p:p.name.lower()):
        if p.name.startswith('.') or p.suffix.lower() not in ('.mp3','.m4a','.aac','.ogg'):continue
        if p.is_symlink() or not p.is_file() or not TRACK.fullmatch(p.name):raise ValueError('Unsupported soundtrack filename: '+p.name)
        shutil.copyfile(p,target/p.name);tracks.append(p.name)
    (target/'playlist.json').write_text(json.dumps(tracks,indent=2)+'\n')
    manifest={'id':'/seventh-seat/','name':'The Seventh Seat','short_name':'Seventh Seat','start_url':'/seventh-seat/','scope':'/seventh-seat/','display':'browser','background_color':'#101115','theme_color':'#101115','icons':[{'src':f'icons/icon-{s}.png','sizes':f'{s}x{s}','type':'image/png','purpose':'any'} for s in (192,512)]}
    (output/'site.webmanifest').write_text(json.dumps(manifest,indent=2)+'\n')
def decorate(html,path):
    sub=path!='index.html';prefix='../' if sub else './'
    suffix={'index.html':'','paper/index.html':'paper/','seven/index.html':'seven/'}[path]
    title={'index.html':'The Seventh Seat — Research observatory','paper/index.html':'The Seventh Seat — The paper','seven/index.html':'The Seventh Seat — Interactive diorama'}[path]
    desc='A synthetic watershed experiment on evidence, reporting and an absent downstream community. Explore the records, results and limitations.'
    head=f'''\n<link rel="canonical" href="https://benamuwo.me/seventh-seat/{suffix}">
<link rel="icon" type="image/svg+xml" href="{prefix}icons/seal.svg">
<link rel="icon" type="image/png" sizes="32x32" href="{prefix}icons/icon-32.png">
<link rel="icon" sizes="16x16 32x32 48x48" href="{prefix}icons/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="{prefix}icons/icon-180.png">
<link rel="manifest" href="{prefix}site.webmanifest">
<meta name="theme-color" content="#101115">
<meta property="og:type" content="{'article' if sub else 'website'}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://benamuwo.me/seventh-seat/{suffix}">
<meta property="og:image" content="https://benamuwo.me/seventh-seat/icons/seventh-seat-share.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="The Seventh Seat, with a multicoloured geometric seal">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://benamuwo.me/seventh-seat/icons/seventh-seat-share.png">
<link rel="stylesheet" href="{prefix}experience.css">
<script defer src="{prefix}experience.js"></script>
'''
    return html.replace('</head>',head+'</head>',1)
