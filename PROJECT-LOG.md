# Project Log: The Seventh Seat

## Done

- Founding documents written and frozen at tag `founding-v0.1` (verified by `sha256sum -c FREEZE_MANIFEST.sha256` and `git tag -l`)
- Prior-art ledger first pass, 2026-11-02 (sources searched and statuses recorded in `docs/04_PRIOR_ART_LEDGER.md`)
- Errata E-001 to E-009 applied as nine individual commits, frozen files unchanged (verified by `git diff --quiet founding-v0.1 HEAD -- docs/00_CHARTER.md docs/01_DESIGN_FREEZE.md docs/02_WORLD_SPEC.md docs/06_EXHIBIT_SPEC.md` and the manifest)
- Runbook times corrected to Vancouver UTC−7 (tzdata 2026e)
- Pushed to the GitHub remote by the author (`origin/main` at 321a6ab)
- E-010 applied: qualification and provider integrity
- E-011 applied: The Witnessed World (diorama as the 3D rendering of The Seven Seats)
- **Diorama shell built (2026-11-03, uncommitted):** `observatory/diorama/index.html` (plan poster and 2D panel without WebGL; three.js scene on request with calibrated plan and orbit views), snapshot contract `src/seventh_seat/observatory/snapshot.py`, engine-generated scripted fixtures, G-OBS checks in both halves (`tests/test_snapshot.py`, `observatory/diorama/check_gobs.mjs`), all passing. Measured first load 14 KB gzip; the 3D scene adds 174 KB. Time used: about 1 of the 3 hours E-011 allows
- **Diorama v2 (2026-11-03, uncommitted; E-013):** topology corrected to a shared commons (the v1 ring implied an order the model lacks); full-width cinematic theatre with HUD, dais, brass-and-stone seats, tone mapping and decorative glow; four-step guided reveal labelled as staging; hash-guarded pre-rendered frames (`render_posters.mjs`); experimental snapshots require a manifest; render on demand. G-OBS 12 contract tests and 68 browser checks pass. First load 108 KB gzip; 3D adds 175 KB. Time used: about 1.5 of 3 hours in total
- Submission policy: submit once, final, on Sunday (author, 2026-11-03)
- **Tuesday core built (2026-11-03, uncommitted; awaiting the author's review and commit):** `pyproject.toml` (standard library only), scenario generator, oracle with G3 and G3b certificates and the E-006 frontier, hash-chained event log, engine with the E-004 tool set and weekend hooks (`ledger_view`, `report_router`, `end_of_phase`), scripted fixtures, 30 tests. Gates G3, G3b, G7 and G6 pass; G2 passes at engine level (the model-cache half is Wednesday)
- **Finding F-1 (executable check):** across all 400 calibration and evaluation scenarios, at both cost strata, `price_of_protection` = 0 and the E-006 utility frontier is flat. At the generator's budgets every district can meet full demand within the safe cap by buying alternative supply, so harm buys credits (14 cheap, 56 costly per 14-unit breach), never utility. E-006's avoidable-harm metric therefore equals the shortfall. Resolved by E-012 (approved 2026-11-03; uncommitted with tonight's code)
- Hosting pattern confirmed by reading First Notice's `DEPLOY.md` and the blog's `first_notice` blueprint, read-only (plan in `DEPLOY.md`)

## Review and polish · 2026-11-03

- Repository review confirms the world core, E-012 and diorama v2 are committed at `d136a4a`, `a313a4a` and `b421716` respectively. The earlier “uncommitted” notes above describe the state when those entries were written.
- Codex reviewed the live Neurascape and Schrödinger’s Civilization references, the rendered exhibit, its source and the governing documents. Added navigation, source-snapshot inspection, camera reset, motion control, mobile framing and keyboard focus handling; repaired UTF-8/viewport declarations, stale reveal narration on fixture changes, and fixture disclosure in full screen.
- WebP posters and system fonts now follow the media/font guardrails in `DEPLOY.md`. Quantitative geometry, engine code, fixtures and frozen documents are unchanged. Details and remaining release gates: `observatory/diorama/REVIEW.md`.
- This polish is pre-sprint assistance and remains uncommitted for the author’s review. No push, deployment, model run or submission was performed.

## Remaining

**Code to write (pre-sprint, declared):**
1. Model adapters for the E-010 slate, response cache, tool loop and containment; adapter gate GA, then GM qualification. Complete the model-cache half of G2 and remaining G1/G6 coverage.
2. End-to-end scripted dry run; tag `pre-sprint-2026-11-05`. The world core, scripted agents and fixture-labelled observatory shell are already built.

**Code to write (weekend, judged):** E ledger, S direct route, S0 endorsement path, supervisor; calibration; runs; analysis; figures; report; exhibit data.

**Human actions:** see `docs/05_RUNBOOK.md` → Human Actions (OD-1 model and budget by Tue; OD-2 team by Wed; re-check the resubmission rule Fri; commits, pushes, deploy, submission).

## Decisions of Record

See `docs/DECISIONS.md` (D-001 to D-016; qualms Q-1 to Q-6; open decisions OD-1 to OD-6).

## Resume Point

Start with Remaining item 1 (adapters and GA, then GM). Human actions now: API keys and console spend limits for Anthropic and OpenAI; ask the Apart help desk about resubmission and prior work.
