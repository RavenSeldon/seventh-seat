#!/usr/bin/env bash
# One-shot install of /seventh-seat/ on the droplet. Paste into the DigitalOcean web console as root:
#   curl -fsSL https://raw.githubusercontent.com/RavenSeldon/seventh-seat/main/deploy/droplet_install.sh | bash
# It (1) pulls the blog (which must already carry the seventh_seat blueprint) and restarts it,
# (2) downloads the public research release, checks its SHA-256, checks every exhibit file against
# its RELEASE.json receipt, installs it as a new release and switches to it atomically, (3) checks
# the live site. It stops at the first problem and changes nothing it has not verified.
set -euo pipefail

ZIP_URL="https://github.com/RavenSeldon/seventh-seat/releases/download/research-2026-11-07/seventh-seat-research-2026-11-07.zip"
ZIP_SHA="a1887b626dc57d1e475e268fe6c16d00e8739f49e3a1e3e19eea3930e221f04a"
BASE="${SEVENTH_SEAT_BASE:-/srv/seventh-seat}"
SITE="${SEVENTH_SEAT_SITE:-https://benamuwo.me}"
say() { printf '\n== %s\n' "$*"; }
die() { printf '\nSTOPPED: %s\n' "$*"; exit 1; }

if [[ -z "${SKIP_BLOG:-}" ]]; then
  say "1/3 Updating the blog"
  VIEWS="$(find / -path '*/WebDev/Blog/app/routes/first_notice/views.py' -not -path '*/.venv/*' -not -path '/proc/*' 2>/dev/null | head -1)"
  [[ -n "$VIEWS" ]] || die "could not find the blog checkout on this droplet"
  APP="${VIEWS%/app/routes/first_notice/views.py}"; REPO="${APP%/WebDev/Blog}"
  OWNER="$(stat -c %U "$REPO")"; echo "blog: $REPO (owner $OWNER)"
  if [[ "$OWNER" == root ]]; then git -C "$REPO" pull --ff-only; else sudo -u "$OWNER" git -C "$REPO" pull --ff-only; fi
  [[ -f "$APP/app/routes/seventh_seat/url.py" ]] || die "the blog on GitHub does not have the seventh_seat page yet; run the Mac step first"
  UNIT="$(grep -lsF "$APP" /etc/systemd/system/*.service /lib/systemd/system/*.service | head -1)"
  [[ -n "$UNIT" ]] || UNIT="$(grep -lsiE 'gunicorn' /etc/systemd/system/*.service | head -1)"
  [[ -n "$UNIT" ]] || die "could not find the blog's service; run: systemctl list-units --type=service | grep -i gunicorn"
  SERVICE="$(basename "$UNIT")"; echo "service: $SERVICE"
  systemctl restart "$SERVICE"; sleep 3
  systemctl is-active --quiet "$SERVICE" || die "$SERVICE did not come back; run: journalctl -u $SERVICE -n 40"
fi

say "2/3 Installing the reviewed exhibit"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
if [[ -n "${SEVENTH_SEAT_ZIP_FILE:-}" ]]; then cp "$SEVENTH_SEAT_ZIP_FILE" "$TMP/r.zip"; else curl -fsSL "$ZIP_URL" -o "$TMP/r.zip"; fi
echo "$ZIP_SHA  $TMP/r.zip" | sha256sum -c --quiet - || die "downloaded release does not match its published SHA-256"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)-site"
DEST="$BASE/releases/$STAMP/seventh-seat"
OVERLAY_URL="https://raw.githubusercontent.com/RavenSeldon/seventh-seat/main/deploy/site-overlay"
mkdir -p "$TMP/overlay"
for f in index.html app.js RELEASE.json; do
  if [[ -n "${SEVENTH_SEAT_OVERLAY_DIR:-}" ]]; then cp "$SEVENTH_SEAT_OVERLAY_DIR/$f" "$TMP/overlay/$f"
  else curl -fsSL "$OVERLAY_URL/$f?$(date +%s)" -o "$TMP/overlay/$f" || die "could not fetch the site overlay ($f)"; fi
done
python3 - "$TMP/r.zip" "$DEST" "$TMP/overlay" <<'PY'
# The public archive supplies the verified data, diorama and vendored library; the overlay supplies
# the restyled hub (index.html, app.js) and its new RELEASE.json. Every final file must match that receipt.
import hashlib, json, os, sys, zipfile
from pathlib import Path
z = zipfile.ZipFile(sys.argv[1]); dest = Path(sys.argv[2]); overlay = Path(sys.argv[3]); prefix = "seventh-seat-research/exhibit/"
files = {n[len(prefix):]: z.read(n) for n in z.namelist() if n.startswith(prefix) and not n.endswith("/")}
for f in ("index.html", "app.js", "RELEASE.json"): files[f] = (overlay / f).read_bytes()
rel = json.loads(files["RELEASE.json"])
if rel.get("data_status") != "experimental": sys.exit("release is not the experimental exhibit")
names = set(files) - {"RELEASE.json"}
if names != set(rel["files"]): sys.exit("exhibit files differ from the receipt")
for name in sorted(names):
    if ".." in Path(name).parts or name.startswith("/"): sys.exit("unsafe path in archive")
    if hashlib.sha256(files[name]).hexdigest() != rel["files"][name]["sha256"]: sys.exit(f"{name} does not match the receipt")
for name, data in files.items():
    p = dest / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data); os.chmod(p, 0o644)
for d in [dest, *[p for p in dest.rglob("*") if p.is_dir()]]: os.chmod(d, 0o755)
print(f"verified and installed {len(names)} files + RELEASE.json (archive data + restyled hub)")
PY
chmod 755 "$BASE" "$BASE/releases" "$BASE/releases/$STAMP"
ln -sfn "releases/$STAMP" "$BASE/current.new" && mv -T "$BASE/current.new" "$BASE/current"
(cd "$BASE/releases" && ls -1 | sort | head -n -3 | xargs -r rm -rf --)
echo "live release: $STAMP"
[[ -n "${SKIP_CHECKS:-}" ]] && exit 0

say "3/3 Checking the live site"
fail=0
for path in /seventh-seat/ /seventh-seat/seven/ /seventh-seat/data/summary.json / /first-notice/ /schrodingers_civ/; do
  code="$(curl -s -o /dev/null -w '%{http_code}' "$SITE$path")"; echo "  $code  $path"; [[ "$code" == 200 ]] || fail=1
done
CSP="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["content_security_policy"])' "$BASE/current/seventh-seat/RELEASE.json")"
curl -sI "$SITE/seventh-seat/" | tr -d '\r' | grep -qiF "content-security-policy: $CSP" && echo "  page carries its own verified CSP" || { echo "  page CSP is not the release's"; fail=1; }
[[ $fail == 0 ]] || die "a check failed (the files are installed; nothing else was changed). Copy everything above to Claude."
printf '\nDONE: %s/seventh-seat/\n' "$SITE"
