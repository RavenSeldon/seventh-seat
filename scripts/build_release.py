"""Build the static release of the observatory into dist/seventh-seat/ and enforce DEPLOY.md.

    python3 scripts/build_release.py [--three-dir observatory/diorama/node_modules/three] [--out dist]

The source page imports three.js from a pinned CDN URL. The release copies the four three.js files
it uses next to the page and rewrites the importmap to them, so the deployed site makes no
third-party requests. It also writes RELEASE.json (commit, file hashes, raw and gzip sizes) and a
Content-Security-Policy that fits the page, with hashes for its inline scripts.

Fails (exit 1) if any guardrail is broken: release over 15 MB, first load over 1.5 MB, a file type
outside the allowed list, or any remaining reference to a third-party script or stylesheet.
Standard library only.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "observatory" / "diorama"
THREE_FILES = [
    "build/three.module.min.js",
    "examples/jsm/controls/OrbitControls.js",
    "examples/jsm/renderers/CSS2DRenderer.js",
    "examples/jsm/environments/RoomEnvironment.js",
]
ALLOWED = {".html", ".js", ".json", ".txt", ".svg", ".webp", ".png", ".ico", ".webmanifest", ".css", ".mp3", ".m4a", ".aac", ".ogg"}
RELEASE_LIMIT = 15 * 1024 * 1024
FIRST_LOAD_LIMIT = int(1.5 * 1024 * 1024)
IMPORTMAP = re.compile(r'(<script type="importmap">)(.*?)(</script>)', re.S)
INLINE_SCRIPT = re.compile(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", re.S)


def fail(msg: str) -> None:
    print(f"FAIL {msg}")
    sys.exit(1)


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def csp_for(html: str) -> str:
    hashes = []
    for m in INLINE_SCRIPT.finditer(html):
        if "application/json" in m["attrs"] or "src=" in m["attrs"]:
            continue   # data blocks are not executed; external scripts are covered by 'self'
        digest = base64.b64encode(hashlib.sha256(m["body"].encode("utf-8")).digest()).decode()
        hashes.append(f"'sha256-{digest}'")
    return "; ".join([
        "default-src 'none'",
        "script-src 'self' " + " ".join(hashes),
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: blob:",
        "connect-src 'self'",
        "media-src 'self'",
        "frame-src 'self'",
        "manifest-src 'self'",
        "base-uri 'none'",
        "form-action 'none'",
        "frame-ancestors 'self'",
    ])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--three-dir", default=str(SRC / "node_modules" / "three"))
    ap.add_argument("--out", default=str(ROOT / "dist"))
    a = ap.parse_args()

    three = Path(a.three_dir)
    html = (SRC / "index.html").read_text(encoding="utf-8")
    m = re.search(r"https://cdn\.jsdelivr\.net/npm/three@([\d.]+)/", html)
    if not m:
        fail("index.html has no pinned three.js importmap to rewrite")
    pinned = m[1]
    if not (three / "package.json").exists():
        fail(f"no three.js at {three}; run `make diorama-setup` (npm ci in observatory/diorama)")
    version = json.loads((three / "package.json").read_text())["version"]
    if version != pinned:
        fail(f"local three.js is {version}, the page pins {pinned}")

    out = Path(a.out) / "seventh-seat"
    if out.exists():
        shutil.rmtree(out)
    vendor = out / "vendor" / f"three-{pinned}"
    for rel in THREE_FILES:
        (vendor / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(three / rel, vendor / rel)
    shutil.copyfile(three / "LICENSE", vendor / "LICENSE.txt")
    shutil.copytree(SRC / "fixtures", out / "fixtures")

    base = f"./vendor/three-{pinned}/"
    importmap = json.dumps({"imports": {"three": base + "build/three.module.min.js", "three/addons/": base + "examples/jsm/"}}, indent=1)
    html = IMPORTMAP.sub(lambda mm: f"{mm[1]}\n{importmap}\n{mm[3]}", html, count=1)
    if "cdn.jsdelivr.net" in html or re.search(r'<(script|link)[^>]+(src|href)="https?://', html):
        fail("index.html still references a third-party script or stylesheet")
    (out / "index.html").write_text(html, encoding="utf-8")

    files, total = {}, 0
    for f in sorted(p for p in out.rglob("*") if p.is_file()):
        if f.suffix not in ALLOWED:
            fail(f"{f.relative_to(out)}: file type {f.suffix or '(none)'} is not allowed (DEPLOY.md)")
        data = f.read_bytes()
        total += len(data)
        files[str(f.relative_to(out))] = {"bytes": len(data), "gzip": len(gzip.compress(data, 9)), "sha256": hashlib.sha256(data).hexdigest()}
    first = files["index.html"]
    on_enter = sum(files[str(Path("vendor", f"three-{pinned}", r))]["gzip"] for r in THREE_FILES)

    if total > RELEASE_LIMIT:
        fail(f"release is {total:,} bytes, over the 15 MB limit")
    if first["bytes"] > FIRST_LOAD_LIMIT:
        fail(f"first load is {first['bytes']:,} bytes, over the 1.5 MB limit")

    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain"))
    release = {
        "commit": commit or None,
        "working_tree_clean": not dirty if commit else None,
        "three": pinned,
        "total_bytes": total,
        "first_load": {"bytes": first["bytes"], "gzip": first["gzip"]},
        "on_enter_gzip": on_enter,
        "content_security_policy": csp_for(html),
        "files": files,
    }
    (out / "RELEASE.json").write_text(json.dumps(release, indent=1) + "\n", encoding="utf-8")

    print(f"built {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}  ({len(files) + 1} files)")
    print(f"  first load   {first['bytes']:>9,} B raw  {first['gzip']:>9,} B gzip   (limit 1.5 MB)")
    print(f"  on entering  {on_enter:>9,} B gzip   (three.js, loaded only when asked)")
    print(f"  release      {total:>9,} B raw                      (limit 15 MB)")
    if dirty:
        print("  note: built from a working tree with uncommitted changes; commit before deploying")


if __name__ == "__main__":
    main()
