# The Seventh Seat: common tasks. Python needs only the standard library; the browser checks
# need Node 18+ (once: make diorama-setup).
PY      ?= python3
DIORAMA := observatory/diorama
export PYTHONPATH := src

.PHONY: help test dry-run fixtures diorama-setup diorama-check posters release release-check check frozen

help:
	@echo "make test            unit tests (stdlib)"
	@echo "make frozen          frozen founding docs still match the manifest"
	@echo "make dry-run         end-to-end scripted dry run, offline (no provider calls)"
	@echo "make fixtures        regenerate the scripted snapshots and the page's embedded block"
	@echo "make diorama-setup   once: install Playwright, Chromium and three.js for the checks"
	@echo "make diorama-check   G-OBS browser checks on the source page"
	@echo "make posters         re-render the pre-rendered frames (after any change to the scene)"
	@echo "make release         build dist/seventh-seat/ and enforce the DEPLOY.md guardrails"
	@echo "make release-check   G-OBS browser checks on the release build, offline, with its CSP"
	@echo "make check           everything above that verifies, in order"

test:
	$(PY) -m unittest discover -s tests -t .

dry-run:
	$(PY) scripts/dry_run.py --output runs/scratch/dry-run-$$(date -u +%Y%m%dT%H%M%SZ)

frozen:
	shasum -a 256 -c FREEZE_MANIFEST.sha256

fixtures:
	$(PY) -m seventh_seat.observatory.snapshot

diorama-setup:
	cd $(DIORAMA) && npm ci && npx playwright install chromium

diorama-check:
	cd $(DIORAMA) && node check_gobs.mjs

posters:
	cd $(DIORAMA) && node render_posters.mjs

release:
	$(PY) scripts/build_release.py

release-check: release
	cd $(DIORAMA) && node check_gobs.mjs --page ../../dist/seventh-seat/index.html --offline

check: test frozen diorama-check release-check
