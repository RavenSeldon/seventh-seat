# Project Log: The Seventh Seat

## Done

- Founding documents written and frozen at tag `founding-v0.1` (verified by `sha256sum -c FREEZE_MANIFEST.sha256` and `git tag -l`)
- Prior-art ledger first pass, 2026-11-02 (sources searched and statuses recorded in `docs/04_PRIOR_ART_LEDGER.md`)
- Errata E-001 to E-009 applied as nine individual commits, frozen files unchanged (verified by `git diff --quiet founding-v0.1 HEAD -- docs/00_CHARTER.md docs/01_DESIGN_FREEZE.md docs/02_WORLD_SPEC.md docs/06_EXHIBIT_SPEC.md` and the manifest)
- Runbook times corrected to Vancouver UTC−7 (tzdata 2026e)
- Pushed to the GitHub remote by the author (`origin/main` at 321a6ab)
- E-010 applied: qualification and provider integrity
- Hosting pattern confirmed by reading First Notice's `DEPLOY.md` and the blog's `first_notice` blueprint, read-only (plan in `DEPLOY.md`)

## Remaining

**Code to write (pre-sprint, declared):**
1. World engine, seeded scenario generator, feasibility oracle (LP) with **G3b trade-off certification and the E-006 frontier**, ledger, append-only hash-chained event log. Gates G2, G3, G3b, G7. Implement against the errata, not the superseded tool list in `02` §5.
1b. Model adapters for the E-010 slate; adapter gate GA (E-010b); then GM qualification (E-008 as revised by E-010).
2. Model adapter with response cache, tool loop, scripted agents, containment. Gates G1, G2, G6.
3. Observatory shell with clearly labelled dummy data.
4. End-to-end scripted dry run; tag `pre-sprint-2026-11-05`.

**Code to write (weekend, judged):** E ledger, S direct route, S0 endorsement path, supervisor; calibration; runs; analysis; figures; report; exhibit data.

**Human actions:** see `docs/05_RUNBOOK.md` → Human Actions (OD-1 model and budget by Tue; OD-2 team by Wed; re-check the resubmission rule Fri; commits, pushes, deploy, submission).

## Decisions of Record

See `docs/DECISIONS.md` (D-001 to D-016; qualms Q-1 to Q-6; open decisions OD-1 to OD-6).

## Resume Point

Start with Remaining item 1 (G3b first), then 1b (GM). Human actions now: API keys and console spend limits for Anthropic and OpenAI; ask the Apart help desk about resubmission and prior work.
