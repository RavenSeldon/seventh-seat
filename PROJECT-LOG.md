# Project Log: The Seventh Seat

## Done

- Founding documents written and frozen at tag `founding-v0.1` (verified by `sha256sum -c FREEZE_MANIFEST.sha256` and `git tag -l`)
- Prior-art ledger first pass, 2026-11-02 (sources searched and statuses recorded in `docs/04_PRIOR_ART_LEDGER.md`)
- Errata E-001 to E-009 applied as nine individual commits, frozen files unchanged (verified by `git diff --quiet founding-v0.1 HEAD -- docs/00_CHARTER.md docs/01_DESIGN_FREEZE.md docs/02_WORLD_SPEC.md docs/06_EXHIBIT_SPEC.md` and the manifest)
- Runbook times corrected to Vancouver UTC−7 (tzdata 2026e)
- Pushed to the GitHub remote by the author (`origin/main` at 321a6ab)
- E-010 applied: qualification and provider integrity
- E-011 applied: The Witnessed World (diorama as the 3D rendering of The Seven Seats)
- Submission policy: submit once, final, on Sunday (author, 2026-11-03)
- **Tuesday core built (2026-11-03, uncommitted; awaiting the author's review and commit):** `pyproject.toml` (standard library only), scenario generator, oracle with G3 and G3b certificates and the E-006 frontier, hash-chained event log, engine with the E-004 tool set and weekend hooks (`ledger_view`, `report_router`, `end_of_phase`), scripted fixtures, 30 tests. Gates G3, G3b, G7 and G6 pass; G2 passes at engine level (the model-cache half is Wednesday)
- **Finding F-1 (executable check):** across all 400 calibration and evaluation scenarios, at both cost strata, `price_of_protection` = 0 and the E-006 utility frontier is flat. At the generator's budgets every district can meet full demand within the safe cap by buying alternative supply, so harm buys credits (14 cheap, 56 costly per 14-unit breach), never utility. E-006's avoidable-harm metric therefore equals the shortfall. Resolved by E-012 (approved 2026-11-03; uncommitted with tonight's code)
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
