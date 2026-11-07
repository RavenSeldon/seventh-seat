#!/usr/bin/env bash
# Deploy the reviewed four-exhibit research release to https://benamuwo.me/seventh-seat/.
# Run by the author, from the Mac. Never run by an assistant.
#
#   scripts/deploy_research.sh --verify-only                      # check the release locally, no network
#   SEVENTH_SEAT_HOST=user@droplet scripts/deploy_research.sh --dry-run
#   SEVENTH_SEAT_HOST=user@droplet scripts/deploy_research.sh
#
# Deploys the reviewed build itself (221 browser checks, desktop and phone review; the same
# static exhibit carried in the public research release), not a rebuild: a rebuild would need
# its own review. Before uploading, every file is checked against the build's RELEASE.json
# receipt and nothing outside the receipt may be present.
#
# Server layout (DEPLOY.md): /srv/seventh-seat/releases/<stamp>/seventh-seat/, served through
# the blog blueprint from /srv/seventh-seat/current/seventh-seat. The blueprint must already be
# live (deploy/blog/apply_to_blog.py, then commit, push, pull, reload), else the page is a 404.
set -euo pipefail

MODE="${1:-}"
RELEASE="${SEVENTH_SEAT_RELEASE:-runs/report-output-2026-11-06/exhibit-review}"
BASE="${SEVENTH_SEAT_BASE:-/srv/seventh-seat}"
SITE="${SEVENTH_SEAT_SITE:-https://benamuwo.me}"
KEEP="${SEVENTH_SEAT_KEEP:-3}"

cd "$(dirname "$0")/.."
[[ -f "$RELEASE/RELEASE.json" ]] || { echo "no $RELEASE/RELEASE.json"; exit 1; }

python3 - "$RELEASE" <<'PY'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
rel = json.loads((root / "RELEASE.json").read_text())
if rel.get("data_status") != "experimental":
    sys.exit("refusing: release is not marked experimental (a fixture is never deployed as research)")
listed = set(rel["files"])
present = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()} - {"RELEASE.json"}
if present != listed:
    sys.exit(f"refusing: files differ from the receipt; extra {sorted(present - listed)}, missing {sorted(listed - present)}")
for name, d in rel["files"].items():
    b = (root / name).read_bytes()
    if hashlib.sha256(b).hexdigest() != d["sha256"] or len(b) != d["bytes"]:
        sys.exit(f"refusing: {name} does not match the receipt")
if not rel.get("content_security_policy"):
    sys.exit("refusing: no content_security_policy in RELEASE.json")
print(f"verified {len(listed)} files against RELEASE.json (built from {rel['commit'][:7]}, {rel['total_bytes']} bytes)")
PY
[[ "$MODE" == "--verify-only" ]] && exit 0

HOST="${SEVENTH_SEAT_HOST:?set SEVENTH_SEAT_HOST, e.g. user@droplet}"
DRY=""; [[ "$MODE" == "--dry-run" ]] && DRY="echo [dry-run]"
SHORT="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["commit"][:7])' "$RELEASE/RELEASE.json")"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)-research-$SHORT"
DEST="$BASE/releases/$STAMP"
echo "deploying $STAMP to $HOST:$DEST"

$DRY ssh "$HOST" "mkdir -p '$DEST'"
$DRY rsync -az --delete --chmod=D755,F644 "$RELEASE/" "$HOST:$DEST/seventh-seat/"
# atomic switch: build the new link beside the old one, then rename over it
$DRY ssh "$HOST" "ln -sfn 'releases/$STAMP' '$BASE/current.new' && mv -T '$BASE/current.new' '$BASE/current'"
# keep the newest $KEEP releases
$DRY ssh "$HOST" "cd '$BASE/releases' && ls -1 | sort | head -n -$KEEP | xargs -r rm -rf --"

[[ -n "$DRY" ]] && exit 0
fail=0
for path in /seventh-seat/ /seventh-seat/seven/ /seventh-seat/RELEASE.json /seventh-seat/data/summary.json / /schrodingers_civ/ /first-notice/; do
  code="$(curl -s -o /dev/null -w '%{http_code}' "$SITE$path")"
  echo "  $code  $path"; [[ "$code" == 200 ]] || fail=1
done
want="$(shasum -a 256 "$RELEASE/RELEASE.json" | cut -d' ' -f1)"
got="$(curl -s "$SITE/seventh-seat/RELEASE.json" | shasum -a 256 | cut -d' ' -f1)"
[[ "$want" == "$got" ]] && echo "  live RELEASE.json matches the reviewed build" || { echo "  live RELEASE.json differs"; fail=1; }
csp="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["content_security_policy"])' "$RELEASE/RELEASE.json")"
curl -sI "$SITE/seventh-seat/" | tr -d '\r' | grep -qiF "content-security-policy: $csp" \
  && echo "  live page carries the release's own CSP" || { echo "  live page does not carry the release CSP (is the blog patch live?)"; fail=1; }
if [[ $fail == 1 ]]; then
  echo "checks failed. Roll back: ssh $HOST \"ln -sfn releases/<previous> $BASE/current.new && mv -T $BASE/current.new $BASE/current\""
  exit 1
fi
echo "live: $SITE/seventh-seat/"
