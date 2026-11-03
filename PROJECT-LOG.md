# Project Log: The Seventh Seat

## Done

- Founding documents written and frozen at tag `founding-v0.1` (verified by `sha256sum -c FREEZE_MANIFEST.sha256` and `git tag -l`)
- Prior-art ledger first pass, 2026-11-02 (sources searched and statuses recorded in `docs/04_PRIOR_ART_LEDGER.md`)
- Errata E-001 to E-009 applied as nine individual commits, frozen files unchanged (verified by `git diff --quiet founding-v0.1 HEAD -- docs/00_CHARTER.md docs/01_DESIGN_FREEZE.md docs/02_WORLD_SPEC.md docs/06_EXHIBIT_SPEC.md` and the manifest)
- Runbook times corrected to Vancouver UTC−7 (tzdata 2026e)
- Pushed to the GitHub remote by the author (`origin/main` at 321a6ab)
- E-010 applied: qualification and provider integrity
- E-011 applied: The Witnessed World (diorama as the 3D rendering of The Seven Seats)
- **Tuesday core (2026-11-03, `d136a4a`):** `pyproject.toml` (standard library only), scenario generator, oracle with G3 and G3b certificates and the E-006 frontier, hash-chained event log, engine with the E-004 tool set and weekend hooks (`ledger_view`, `report_router`, `end_of_phase`), scripted fixtures. Gates G3, G3b, G7 and G6 pass; G2 passes at engine level (the model-cache half is Wednesday)
- **Finding F-1 (executable check):** across all 400 calibration and evaluation scenarios, at both cost strata, `price_of_protection` = 0 and the E-006 utility frontier is flat. At the generator's budgets every district can meet full demand within the safe cap by buying alternative supply, so harm buys credits (14 cheap, 56 costly per 14-unit breach), never utility. E-006's avoidable-harm metric therefore equals the shortfall. Resolved by E-012 (`a313a4a`)
- Submission policy: submit once, final, on Sunday by 20:00 Vancouver (author, 2026-11-03)
- Hosting pattern confirmed by reading First Notice's `DEPLOY.md` and the blog's `first_notice` blueprint, read-only
- **Diorama v1 and v2 (2026-11-03, `b421716`; E-011, E-013):** snapshot contract, engine-generated fixtures, three.js scene with calibrated plan; shared-commons topology, cinematic theatre, guided reveal labelled as staging, hash-guarded pre-rendered frames, render on demand
- **Diorama v3 (2026-11-03, `6cbe6b1`), by Ben Amuwo:** document setup, navigation and focus handling, Reset view, Pause motion, offscreen pause, full-screen disclosure, inspectable snapshot source, phone layout, zero-inflow bar scale, WebP posters, system fonts, lavender title accent. Notes: `observatory/diorama/REVIEW.md`
- **Checks, release and polish (2026-11-03):**
  - G-OBS browser checks rewritten to wait for the render loop instead of fixed delays (stable across repeated runs), and extended: labels never overlap or leave the theatre (desktop, plan, phone, reveal), decoration off in the plan, water motion stops when paused, reduced or offscreen, no third-party requests, and the release's CSP causes no violation. 97 browser checks, 43 unit tests
  - `make` targets; `observatory/diorama/package.json` pins Playwright and three.js
  - Release build `scripts/build_release.py` (vendored three.js, guardrails enforced, `RELEASE.json` with commit, hashes, sizes and CSP); deploy template `scripts/deploy.sh` (not yet run)
  - Validator message now says what the check is: a manifest reference, verified by the exporter
  - Downstream label no longer collides with seat labels on a phone
  - The commons now shows (it sat beneath the dais top); water shading with moving caustics; 道 and ∞ light motifs, off in the calibrated plan

## Remaining

**Code to write (pre-sprint, declared):**
1. Model adapters for the E-010 slate, response cache, tool loop and containment; adapter gate GA, then GM qualification. Complete the model-cache half of G2 and remaining G1/G6 coverage.
2. End-to-end scripted dry run; tag `pre-sprint-2026-11-05`. The world core, scripted agents and fixture-labelled observatory shell are already built.

**Code to write (weekend, judged):** E ledger, S direct route, S0 endorsement path, supervisor; calibration; runs; analysis; figures; report; exhibit data.

**Human actions:** see `docs/05_RUNBOOK.md` → Human Actions (API keys and spend limits by Wed; re-read the live sprint page Fri; commits, pushes, deploy, submission).

**Hosting (once, when the exhibit is ready):** the blog blueprint and server settings listed in `DEPLOY.md` → Once: Blog Side.

## Decisions of Record

See `docs/DECISIONS.md` (D-001 to D-024; qualms Q-1 to Q-6; open decisions OD-1 to OD-6).

## Resume Point

Start with Remaining item 1 (adapters and GA, then GM). Human action now: API keys and console spend limits for Anthropic and OpenAI. Before committing observatory changes: `make check`.
