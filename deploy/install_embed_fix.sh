#!/usr/bin/env bash
# Install only the reviewed static presentation. No blog pull or service restart.
# Previous release is retained; a failed health check restores its symlink.
set -euo pipefail
BASE="${SEVENTH_SEAT_BASE:-/srv/seventh-seat}"
SITE="${SEVENTH_SEAT_SITE:-https://benamuwo.me}"
ARCHIVE_URL='https://github.com/RavenSeldon/seventh-seat/releases/download/embed-fix-2026-11-07/seventh-seat-embed-fix.zip'
ARCHIVE_SHA='974064dc1471b89d585394b019dc1afff4ad44ad21b9952d9e6ba35006668c68'
[[ -d "$BASE/current/seventh-seat" && -L "$BASE/current" ]] || { echo 'STOP: existing static release/symlink required'; exit 1; }
mkdir "$BASE/.embed-install.lock" || { echo 'STOP: another reading installer may be running'; exit 1; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"; rmdir "$BASE/.embed-install.lock"' EXIT
if [[ -n "${SEVENTH_SEAT_ZIP_FILE:-}" ]]; then cp "$SEVENTH_SEAT_ZIP_FILE" "$TMP/site.zip"
else curl --fail --show-error --silent --location --retry 2 "$ARCHIVE_URL" -o "$TMP/site.zip"; fi
python3 - "$TMP/site.zip" "$ARCHIVE_SHA" "$BASE" "$SITE" <<'PY'
import hashlib, json, os, sys, tempfile, urllib.request, zipfile
from pathlib import Path, PurePosixPath
archive, expected, base, site = sys.argv[1:]; base=Path(base)
if hashlib.sha256(Path(archive).read_bytes()).hexdigest()!=expected:sys.exit('STOP: archive digest mismatch; live release unchanged')
with zipfile.ZipFile(archive) as z:
    infos=z.infolist();names=[i.filename for i in infos]
    if len(names)!=len(set(names)) or sum(i.file_size for i in infos)>20*1024*1024:sys.exit('STOP: duplicate or oversized archive')
    files={}
    for info in infos:
        name=info.filename;p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or '\\' in name:sys.exit('STOP: unsafe archive path')
        if name in {'LICENSE.txt','LICENSE-DATA.txt','LICENSING.txt'}:continue
        if not name.startswith('seventh-seat/') or info.is_dir():sys.exit('STOP: unexpected archive member')
        files[name[len('seventh-seat/'):]]=z.read(info)
rel=json.loads(files['RELEASE.json'])
if rel['data_status']!='experimental' or not rel['working_tree_clean']:sys.exit('STOP: unreviewed release status')
if set(files)-{'RELEASE.json'}!=set(rel['files']):sys.exit('STOP: file set differs from receipt')
for name,entry in rel['files'].items():
    if hashlib.sha256(files[name]).hexdigest()!=entry['sha256'] or len(files[name])!=entry['bytes']:sys.exit('STOP: file digest mismatch: '+name)
if sum(map(len,files.values()))!=rel['total_bytes']:sys.exit('STOP: release size differs from receipt')
# Refuse accidental replacement with different scientific data or diorama bytes.
current=base/'current';previous=os.readlink(current);old=json.loads((current/'seventh-seat/RELEASE.json').read_text())
for name,entry in old['files'].items():
    if name.startswith(('data/','seven/')) and rel['files'].get(name,{}).get('sha256')!=entry['sha256']:sys.exit('STOP: scientific data or diorama differs: '+name)
release=Path(tempfile.mkdtemp(prefix='embed-20261107-',dir=base/'releases'))
release.chmod(0o755);dest=release/'seventh-seat'
for name,data in files.items():
    p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);p.chmod(0o644)
for p in [dest,*[p for p in dest.rglob('*') if p.is_dir()]]:p.chmod(0o755)
# All bytes verified before the only live mutation.
new=base/'current.embed-new'
if os.path.lexists(new):sys.exit('STOP: a pending release switch exists; live release unchanged')
os.symlink(str(release.relative_to(base)),new);os.replace(new,current)
try:
    if not os.environ.get('SEVENTH_SEAT_SKIP_HTTP_CHECKS'):
        for name,expected_bytes in files.items():
            req=urllib.request.Request(site.rstrip('/')+'/seventh-seat/'+name,headers={'Cache-Control':'no-cache'})
            with urllib.request.urlopen(req,timeout=25) as response:
                if response.status!=200 or hashlib.sha256(response.read()).digest()!=hashlib.sha256(expected_bytes).digest():raise ValueError('live bytes differ: '+name)
                if name.endswith('.html') and response.headers.get('Content-Security-Policy')!=rel['content_security_policy']:raise ValueError('live CSP differs: '+name)
        for route in ('/seventh-seat/','/seventh-seat/paper/','/seventh-seat/seven/'):
            with urllib.request.urlopen(site.rstrip('/')+route,timeout=25) as response:
                if response.status!=200:raise ValueError('route unavailable: '+route)
except Exception:
    os.symlink(previous,new);os.replace(new,current)
    print('ROLLED BACK: live verification failed; previous release restored',file=sys.stderr)
    raise
print('INSTALLED: '+str(release))
print('Previous release retained: '+previous)
print('HTTP checks skipped (local test only)' if os.environ.get('SEVENTH_SEAT_SKIP_HTTP_CHECKS') else 'VERIFIED: all live file hashes, HTML policies and publication routes')
PY
