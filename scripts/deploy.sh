#!/usr/bin/env bash
# Upload a built release to the droplet and switch to it atomically. TEMPLATE: not yet run against
# the server; do a --dry-run first and compare with First Notice's deploy script.
#
#   make release && make release-check        # build and verify first
#   SEVENTH_SEAT_HOST=user@droplet scripts/deploy.sh [--dry-run]
#
# Layout on the server (DEPLOY.md):
#   /srv/seventh-seat/releases/<stamp>/seventh-seat/   one directory per release
#   /srv/seventh-seat/current -> releases/<stamp>      the blueprint serves current/seventh-seat/
set -euo pipefail

HOST="${SEVENTH_SEAT_HOST:?set SEVENTH_SEAT_HOST, e.g. user@droplet}"
BASE="${SEVENTH_SEAT_BASE:-/srv/seventh-seat}"
SITE="${SEVENTH_SEAT_SITE:-https://benamuwo.me}"
KEEP="${SEVENTH_SEAT_KEEP:-3}"
DRY=""; [[ "${1:-}" == "--dry-run" ]] && DRY="echo [dry-run]"

cd "$(dirname "$0")/.."
DIST="dist/seventh-seat"
[[ -f "$DIST/RELEASE.json" ]] || { echo "no $DIST/RELEASE.json; run make release"; exit 1; }
if [[ -n "$(git status --porcelain)" ]]; then echo "working tree has uncommitted changes; commit, then rebuild"; exit 1; fi
grep -q "\"commit\": \"$(git rev-parse HEAD)\"" "$DIST/RELEASE.json" || { echo "release was built from another commit; rebuild"; exit 1; }

STAMP="$(date -u +%Y%m%dT%H%M%SZ)-$(git rev-parse --short HEAD)"
DEST="$BASE/releases/$STAMP"
echo "deploying $STAMP to $HOST:$DEST"

$DRY ssh "$HOST" "mkdir -p '$DEST'"
$DRY rsync -az --delete --chmod=D755,F644 "$DIST/" "$HOST:$DEST/seventh-seat/"
# atomic switch: build the new link beside the old one, then rename over it
$DRY ssh "$HOST" "ln -sfn 'releases/$STAMP' '$BASE/current.new' && mv -T '$BASE/current.new' '$BASE/current'"
# keep the newest $KEEP releases
$DRY ssh "$HOST" "cd '$BASE/releases' && ls -1 | sort | head -n -$KEEP | xargs -r rm -rf --"

[[ -n "$DRY" ]] && exit 0
fail=0
for path in /seventh-seat/ /seventh-seat/RELEASE.json / /schrodingers_civ/ /first-notice/; do
  code="$(curl -s -o /dev/null -w '%{http_code}' "$SITE$path")"
  echo "  $code  $path"; [[ "$code" == 200 ]] || fail=1
done
curl -s "$SITE/seventh-seat/RELEASE.json" | grep -q "\"commit\": \"$(git rev-parse HEAD)\"" \
  && echo "  live release matches this commit" || { echo "  live RELEASE.json does not match this commit"; fail=1; }
if [[ $fail == 1 ]]; then
  echo "checks failed. Roll back: ssh $HOST \"ln -sfn releases/<previous> $BASE/current.new && mv -T $BASE/current.new $BASE/current\""
  exit 1
fi
