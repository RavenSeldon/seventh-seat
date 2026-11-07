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

**5 November preparation update (supersedes older pending-preparation wording below):** GM and rehearsal are complete. The current handoff is `docs/THURSDAY_HANDOFF.md`. Citation search and claim verification added bibliographic corrections (including PA-17 and PA-22), a bounded prospective contribution sentence, and two close leads PA-38/39 whose primary manuscripts remain unverified; G0 therefore stays open. The official template was read and a pre-sprint outline plus nine candidate references prepared. The author approved calibration D-028/E-014 and confirmed survey/Discord complete. Draft preregistration §7 now states the existing E-010 recovery rule explicitly. Disclosure and a review inventory were prepared. A fresh offline rehearsal passed all 18 checks; all 10 declared gm-v2 source hashes matched. No model calls or research runs occurred.

**Code to write (pre-sprint, declared):**
1. GM is decided and closed (`gm-v2`, GPT-6 Luna; C-1 applied; D-025–D-027). Not to be reopened.
2. ~~End-to-end scripted dry run~~ done 2026-11-04 (`experiments/dry_run_2026-11-04.json`, 18 checks; `make dry-run`; `docs/REPRODUCE.md`) and rechecked offline 5 Nov (`experiments/preparation_checks_2026-11-05.json`). Remaining: primary-source follow-up, console controls, final review/commit and tag `pre-sprint-2026-11-05`.

**Code to write (weekend, judged):** E ledger, S direct route, S0 endorsement path, supervisor; hazard-world runner; calibration execution; runs; analysis; figures; completed report; experimental exhibit data.

**Human actions:** see `docs/05_RUNBOOK.md` → Human Actions (API access confirmed; record account rate limits and console spend controls; re-read the live sprint page Fri; commits, pushes, deploy, submission).

**Hosting (once, when the exhibit is ready):** the blog blueprint and server settings listed in `DEPLOY.md` → Once: Blog Side.

## Decisions of Record

See `docs/DECISIONS.md` (through D-028; qualms Q-1 to Q-6; open decisions OD-1 to OD-6 and their later dispositions).

## Resume Point

GM closed (GPT-6 Luna). Dry run, report outline/bibliography, calibration clarification and review inventory are prepared. Next: PA-38/39 primary-source follow-up to close G0; provider-console control confirmation; review/commit/tag the pre-sprint boundary. Follow `docs/THURSDAY_HANDOFF.md`. Weekend runner note: `run_with_recovery` refuses hazard worlds by design; the evaluation runner (with the same recovery rules) is weekend work. Preserve the budget ledger and GM records in `runs/` (private). Before committing observatory changes: `make check`.


## Friday continuation — 6 November 2026

Inherited uncommitted Friday interventions, runner and analytics were preserved and reviewed. Added recovery/integrity corrections, calibration and evaluation orchestration, an unattended local controller, source archives and a stricter budget ledger. All 147 offline tests pass; all 160 possible planned pilot/evaluation scenarios across the five kappa settings pass the oracle; four founding-document hashes match. Evidence: `experiments/continuation_checks_2026-11-06.json`.

A live eight-seed calibration pilot is now running. Its data is private and excluded from evaluation. No evaluation lock or evaluation result yet. Caps: US$33/provider, US$66 overall, US$20 qualification/pilot including historical spend. `runs/controller-status.json` records unattended progress. The controller waits for reviewed gates and the `prereg-frozen` tag before evaluation. Current handoff: `docs/FRIDAY_CONTINUATION.md`.

The author authorized a local commit. The proposed Thursday tag was withdrawn before creation. Historical pre-sprint disclosure is retained; this continuation is dated today. No push, deployment or submission occurred.

### 6 November — reproducible report preparation

Added local curated export and manuscript-table commands with six focused regression checks. Replayed the first live pilot episode offline: event bytes identical, no additional paid calls. Retained official template and pending-results manuscript source; rechecked six cited primary abstracts. No evaluation lock or intervention result is claimed at this checkpoint.

### 6 November — evaluation running and report layout ready

The fixed pilot completed with 4/8 breaches at kappa 14; the predeclared rule accepted the initial setting. Evaluation was frozen at 2339497 (`prereg-frozen`) and began at 02:37 UTC on 7 November (19:37 Vancouver on 6 November). A separate offline finisher waits for validated completion and prepares private tables and a curated record bundle. The manuscript builder was checked on a clearly labelled synthetic layout fixture: five main pages plus two reference/appendix pages, all pages verified, eight clickable PDF links. Actual results still require final interpretation and render review.

### 6 November — audited pilot export and exhibit data preparation

All eight pilot episodes, their declaration and result were curated locally and reproduce the frozen evaluation decision without any paid calls. A new exhibit exporter verifies the evaluation export, binds final water snapshots to exact log/manifest/event hashes, retains missing episodes and selects the first complete locked scenario for witness detail. Synthetic fixtures cannot be labelled experimental. Three focused exhibit checks and the R-001 denominator regression bring the offline suite to 162 passing tests. R-001 is disclosed in `docs/REPORTING_CORRECTIONS.md`; the scientific freeze is unchanged. Collection continues; no final findings or publication are claimed.
