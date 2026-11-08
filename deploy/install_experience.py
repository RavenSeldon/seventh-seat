#!/usr/bin/env python3
"""Install the pinned seal/music release; retain and restore both previous components."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import time
import urllib.request
import zipfile

ARCHIVE_URL = 'https://github.com/RavenSeldon/seventh-seat/releases/download/experience-2026-11-07/seventh-seat-experience.zip'
ARCHIVE_SHA = 'e694b03a0c6f86428d92ca4cd1f75f8afc2ac691c1dcf73b6afc4d0a32da8786'
VIEWS_URL = 'https://raw.githubusercontent.com/RavenSeldon/seventh-seat/03df2854c6cc3def5aabec11b2177567da32c25e/deploy/blog/seventh_seat/views.py'
OLD_VIEWS_SHA = 'db46c753c613203d35d61518c35cb5013f325941cdb4ef274921492e7d7b9fc6'
NEW_VIEWS_SHA = 'e01c4842639bace55a462fa2b61064567b6105d1818454fd9eda2b57529e6875'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'Cache-Control':'no-cache'}), timeout=45) as response:
        return response.read(22 * 1024 * 1024)

def atomic_write(path, data):
    stat = path.stat()
    fd, name = tempfile.mkstemp(prefix='.seventh-seat-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(data); out.flush(); os.fsync(out.fileno())
        os.chmod(name, stat.st_mode & 0o777)
        if os.geteuid() == 0: os.chown(name, stat.st_uid, stat.st_gid)
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)

def switch(base, target):
    new = base / 'current.experience-new'
    if os.path.lexists(new): raise RuntimeError('Pending release switch exists')
    os.symlink(target, new)
    os.replace(new, base / 'current')

def install(archive, views, base, live_views, reload_blog, verify):
    if digest(archive.read_bytes()) != ARCHIVE_SHA: raise ValueError('Archive digest mismatch')
    if digest(views) != NEW_VIEWS_SHA: raise ValueError('Serving-file digest mismatch')
    previous_views = live_views.read_bytes()
    if digest(previous_views) not in (OLD_VIEWS_SHA, NEW_VIEWS_SHA):
        raise ValueError('Server serving file differs from reviewed versions; nothing changed')
    current = base / 'current'
    if not current.is_symlink(): raise ValueError('Existing release symlink required')
    previous = os.readlink(current)
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        if len({i.filename for i in infos}) != len(infos) or sum(i.file_size for i in infos) > 20*1024*1024:
            raise ValueError('Duplicate or oversized archive')
        files = {}
        for info in infos:
            p = PurePosixPath(info.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in info.filename or info.is_dir():
                raise ValueError('Unsafe archive path')
            if info.filename in ('LICENSE.txt', 'LICENSE-DATA.txt', 'LICENSING.txt'): continue
            if not info.filename.startswith('seventh-seat/'): raise ValueError('Unexpected archive member')
            files[info.filename[len('seventh-seat/'):]] = z.read(info)
    rel = json.loads(files['RELEASE.json'])
    if rel['data_status'] != 'experimental' or not rel['working_tree_clean']:
        raise ValueError('Unreviewed release status')
    if set(files) - {'RELEASE.json'} != set(rel['files']): raise ValueError('Receipt file set mismatch')
    for name, entry in rel['files'].items():
        if digest(files[name]) != entry['sha256'] or len(files[name]) != entry['bytes']:
            raise ValueError('Receipt mismatch: ' + name)
    if sum(map(len, files.values())) != rel['total_bytes']: raise ValueError('Receipt size mismatch')
    old = json.loads((current / 'seventh-seat/RELEASE.json').read_text())
    for name, entry in old['files'].items():
        if name.startswith(('data/', 'seven/vendor/')) and rel['files'].get(name, {}).get('sha256') != entry['sha256']:
            raise ValueError('Scientific data or vendored engine differs: ' + name)
    release = Path(tempfile.mkdtemp(prefix='experience-20261107-', dir=base/'releases'))
    release.chmod(0o755)
    dest = release / 'seventh-seat'
    for name, data in files.items():
        path = dest / name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data); path.chmod(0o644)
    for path in (dest, *[p for p in dest.rglob('*') if p.is_dir()]): path.chmod(0o755)
    (release / 'previous-views.py').write_bytes(previous_views)
    (release / 'previous-release.txt').write_text(previous + '\n')
    # Verified before mutations. Only one route file and one static symlink change.
    try:
        atomic_write(live_views, views)
        reload_blog()
        switch(base, str(release.relative_to(base)))
        verify(files, rel)
    except BaseException:
        switch(base, previous)
        atomic_write(live_views, previous_views)
        reload_blog()
        print('ROLLED BACK: previous site and serving file restored.')
        raise
    print('VERIFIED: seal, soundtrack, diorama and publication routes installed.')
    print('Previous release and serving file retained in ' + str(release))
    return release

def check_http(files, rel):
    base = 'https://benamuwo.me/seventh-seat/'
    for name, data in files.items():
        with urllib.request.urlopen(urllib.request.Request(base+name, headers={'Cache-Control':'no-cache'}), timeout=30) as response:
            if response.status != 200 or digest(response.read()) != digest(data): raise ValueError('Live mismatch: ' + name)
            if name.endswith('.html') and response.headers.get('Content-Security-Policy') != rel['content_security_policy']:
                raise ValueError('Live content policy mismatch')
    track = next(name for name in files if name.endswith('.m4a'))
    with urllib.request.urlopen(urllib.request.Request(base+track, headers={'Range':'bytes=0-31'}), timeout=30) as response:
        if response.status != 206 or response.read() != files[track][:32] or response.headers.get_content_type() != 'audio/mp4':
            raise ValueError('Audio range serving failed')
    for route in ('/seventh-seat/', '/seventh-seat/paper/', '/seventh-seat/seven/', '/first-notice/', '/schrodingers_civ/', '/'):
        with urllib.request.urlopen('https://benamuwo.me'+route, timeout=30) as response:
            if response.status != 200: raise ValueError('Publication route unavailable')

def main():
    if os.geteuid() != 0: raise SystemExit('Run in the server root console (or with sudo).')
    base = Path('/srv/seventh-seat')
    work = subprocess.check_output(['systemctl','show','blog.service','--property=WorkingDirectory','--value'], text=True).strip()
    command = subprocess.check_output(['systemctl','show','blog.service','--property=ExecStart','--value'], text=True)
    if not work.startswith('/') or 'gunicorn' not in command: raise SystemExit('STOP: expected blog.service not found; nothing changed')
    live_views = Path(work) / 'app/routes/seventh_seat/views.py'
    if not live_views.is_file() or live_views.is_symlink(): raise SystemExit('STOP: expected serving file not found; nothing changed')
    lock = base / '.experience-install.lock'
    lock.mkdir()  # Do not overlap another invocation.
    try:
        views = fetch(VIEWS_URL)
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / 'site.zip'; archive.write_bytes(fetch(ARCHIVE_URL))
            def reload_blog():
                subprocess.run(['systemctl','kill','--kill-who=main','--signal=HUP','blog.service'], check=True)
                time.sleep(2)
                subprocess.run(['systemctl','is-active','--quiet','blog.service'], check=True)
            install(archive, views, base, live_views, reload_blog, check_http)
    finally:
        lock.rmdir()

if __name__ == '__main__':
    main()
