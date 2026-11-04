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
- **Interface dressing (2026-11-03):** controls, reveal card and instrument restyled after benamuwo.com; smaller title block so it covers less of the scene

- **Wednesday harness implemented early (2026-11-03):** two E-010 adapters, nine schema-checked tools, per-district opaque histories, response cache, persistent transactional budget reservations, bounded retries and episode recovery. 70 Python tests pass; frozen hashes match. Both live no-hazard smoke episodes completed and replayed to byte-identical event logs. Combined conservative usage accounting US$0.021538685; no unresolved reservations after both finished. These are integration checks, not GM qualification or experimental findings. Details: `docs/WEDNESDAY_HARNESS.md`; shareable evidence: `experiments/harness_smoke_2026-11-03.json`.

- **Gate GM run, 2026-11-04 (`experiments/gm/`): neither configuration qualified; none selected.** Specification `gm-v1` (10 rules items, 4 allocation tasks, 3 tool checks, 3 no-hazard episodes per configuration) declared and hashed at 07:27:18 UTC before any call. GPT-6 Luna: rules 8/10; allocation tasks A2–A4 failed (no alternative supply in A2 and A4, leaving A2 below minimum need; A3 committed (3, 3) against a declared key of (3, 4)). Claude Haiku 5.5: rules 10/10; A3 failed (plan and commit exceeded credits, district received nothing; 2 unresolved critical violations). Both: 100% schema-valid calls, adapter gate passed, all episodes evaluable, no refusals, truncations or infrastructure errors. Records replay exactly. GM spend US$0.088937235 (Luna 0.022663235, Haiku 0.066274000), all settled; ledger total US$0.11047592 under unchanged caps. Account rate limits recorded from response headers. 81 tests pass. Report: `experiments/gm/QUALIFICATION_REPORT.md`
- **Gate GM `gm-v2`, 2026-11-04 (D-025; `experiments/gm/v2/`): both configurations passed; GPT-6 Luna selected** by lowest spend per evaluable episode (US$0.008661 vs Haiku US$0.023473). Revision followed the `gm-v1` failures and was disclosed as such; three instrument corrections only (rules reference, reserved-entitlement sentences in `offer`/`plan`, explicit A1–A4 objective). Declared 08:22:17 UTC; one run each; all criteria met by both; replay exact; `gm-v1` records unchanged and its sources archived. `gm-v2` spend US$0.096403445; qualification total US$0.185340680; ledger total US$0.206879365, all settled. Replay-scoring defect corrected as C-1 (D-026) without touching declared sources: missing cost is unavailable, never US$0; the corrected replay artifact withholds selection on its own evidence and reproduces Luna from verified historical cost; the invalid replay decision is explicitly superseded. Interpretations retained (D-027). 93 tests pass. Report: `experiments/gm/v2/QUALIFICATION_REPORT.md`

## Remaining

**Code to write (pre-sprint, declared):**
1. GM is decided and closed (`gm-v2`, GPT-6 Luna; C-1 applied; D-025–D-027). Not to be reopened.
2. ~~End-to-end scripted dry run~~ done 2026-11-04 (`experiments/dry_run_2026-11-04.json`, 18 checks; `make dry-run`; `docs/REPRODUCE.md`). Remaining: author review and commit, then tag `pre-sprint-2026-11-05`.

**Code to write (weekend, judged):** E ledger, S direct route, S0 endorsement path, supervisor; calibration; runs; analysis; figures; report; exhibit data.

**Human actions:** see `docs/05_RUNBOOK.md` → Human Actions (API access confirmed; record account rate limits and console spend controls; re-read the live sprint page Fri; commits, pushes, deploy, submission).

**Hosting (once, when the exhibit is ready):** the blog blueprint and server settings listed in `DEPLOY.md` → Once: Blog Side.

## Decisions of Record

See `docs/DECISIONS.md` (D-001 to D-024; qualms Q-1 to Q-6; open decisions OD-1 to OD-6).

## Resume Point

GM closed (GPT-6 Luna). Dry run and reproducibility instructions done. Next: citation review (G0), report skeleton, pre-sprint disclosure (`PREEXISTING_WORK.md` file list), then author review, commit and tag `pre-sprint-2026-11-05`. Weekend runner note: `run_with_recovery` refuses hazard worlds by design; the evaluation runner (with the same recovery rules) is weekend work. Preserve the budget ledger and the GM records in `runs/` (private). Human action: console spend controls. Before committing observatory changes: `make check`.
