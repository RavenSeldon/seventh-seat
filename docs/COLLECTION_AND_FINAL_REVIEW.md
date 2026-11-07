# Collection and final review

6 November 2026. This is a durable handoff, not a declaration of completed research.

## Where the work lives

The active repository is `/Users/theda/Root/seventh-seat`. The chat workspace at `/Users/theda/Documents/ChatGPT/Seventh Seat` contains source backups and document QA artifacts; its old `review/` copy is not the live checkout. Do not restart from that stale copy.

The author has authorized continued work, local commits and reviewed checkpoint pushes to `https://github.com/RavenSeldon/seventh-seat` on `main`. Private `runs/`, credentials and budget databases stay excluded. There is no authorization here to change repository visibility, publish private logs, deploy the blog or submit the paper. Prepare concrete reviewed outputs before requesting any remaining publication/submission approval.

## Collection

The eight fixed pilot episodes completed at kappa 14, with four breaches. E-014 accepted that first setting. No adjustment, replacement seed or extra pilot is needed. The closed gm-v2 selection remains GPT-6 Luna, medium reasoning, no temperature, 4096 output tokens.

Evaluation was frozen at `2339497631ded053e8423282b3c3dec9fa7dd760`, tagged `prereg-frozen`, and pushed. The scientific source checkpoint is `f949dac1c6b17d6dba884e71f8302d12bf3cf651`. The metadata placement deviation is disclosed in `EVALUATION_FREEZE.md`; do not silently edit the pilot-hashed preregistration or ERRATA. The tag never moves.

The plan is 24 fixed scenarios, 12 cheap and 12 costly, each with four cells. Collection starts no new episodes after 8 November 06:00 UTC (Saturday 7 November 23:00 Vancouver); in-flight episodes may finish. New blocks need the locked timing reserve. The outcome does not change the stop or sample plan.

The durable ledger is `runs/research-budget.sqlite`. Caps remain USD33 OpenAI, USD33 Anthropic, USD66 overall, USD20 preparation, including historical charges. Uncertain requests retain their full reservation. Never increase caps, refund uncertainty without evidence, switch models or requalify because of outcomes. Provider usage costs are published-rate estimates, not invoices.

Two detached local workers are active:

- `scripts/keep_run_alive.py`: adopt/resume the pilot, validate the freeze, run evaluation, compute integrity-checked analysis. Status: `runs/controller-status.json`.
- `scripts/finish_outputs.py --wait --exhibits`: after `results_ready`, create an allowlisted local export, recompute report tables, verify the bound calibration summary and write a private cost summary, then prepare source-bound exhibit data and a private static review build. Status: `runs/report-output-status.json`.

Each uses an exclusive process lock and a `caffeinate` assertion. Keep the Mac open and connected to power. The workers survive chat inactivity, but not guaranteed shutdown, power loss or lid closure. They use no model calls for monitoring.

If a worker is gone, inspect its status/log and unfinished manifests first. The same command resumes within the recorded attempt budget; do not duplicate an active writer. If collection stopped for an integrity error, audit it before retrying. Existing terminal episodes are never resampled. Documentation checkpoints may descend from the freeze tag; the launcher verifies scientific files, lock and gates against the tag before resuming.

## After the workers finish

Expected private directory: `runs/report-output-2026-11-06/`:

- `curated-records/`: verified evaluation logs/manifests, lock, index, analysis and an export receipt. No provider caches, keys or budget database.
- `report-tables.json` and `report-tables.md`: complete-block means/contrasts and explicitly scoped descriptive/all-attempt summaries.
- `calibration-records/`: eight completed pilot episodes, declaration and result, independently reproducing the frozen decision; already curated locally by `scripts/export_calibration.py`.
- `calibration-summary.json`: checked against the lock's calibration-result hash.
- `exhibit-data/` and `exhibit-review/`: source-bound final snapshots, summaries, filtered witness details and static review build. Browser review of actual data is still required.
- `private-cost-summary.json`: local accounting only; do not include in a public export by default.

Recompute the table bundle before using it, rather than trusting an edited copy:

```bash
cd /Users/theda/Root/seventh-seat
.venv/bin/python scripts/report_results.py --run runs/report-output-2026-11-06/curated-records --out runs/report-output-2026-11-06
```

Confirm all 96 planned episode IDs are accounted for, report every missing cell and incomplete block, and retain refusal episodes. H1/H2 use the unrounded frozen intervals. H3 is exploratory; H4 trade-disabled was not collected. Do not silently reinterpret the inherited AWC proxy as comprehensive replan opportunity or internal comprehension.

## Build the manuscript

`report/working/manuscript.json` is the retained pending-results draft. `assemble_verified_manuscript.py` writes a new file from the computed bundle, and `build_manuscript.py` fills the official Word template. The assembler is a starting point for scientific review, not a substitute for it. It fails if no complete blocks exist; that case needs an honest failure report instead of invented effect estimates.

Use the bundled document runtime:

```bash
DOC_PY=/Users/theda/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
"$DOC_PY" report/working/assemble_verified_manuscript.py --tables runs/report-output-2026-11-06/report-tables.json --pilot runs/report-output-2026-11-06/calibration-summary.json --output runs/report-output-2026-11-06/manuscript.json
"$DOC_PY" report/working/build_manuscript.py --data runs/report-output-2026-11-06/manuscript.json --output runs/report-output-2026-11-06/seventh-seat.docx
```

Read and follow the documents skill before further document edits. Render with its `render_docx.py` and the bundled LibreOffice runtime; inspect every final page. The synthetic layout rehearsal had five main pages and two reference/appendix pages, all reviewed; it is NOT an empirical paper. The actual report must be checked again, including 150–250 abstract words, at most eight main pages, clickable citations, table/interval precision, accurate prior work and assistance, ethics appendix and no pending publication placeholders.

The manuscript assembler has a `--layout-fixture` option that visibly labels synthetic layout checks. Never pass that option for the actual paper and never substitute its outputs for research. QA fixtures remain in the chat workspace, outside the research run.

## Remaining finish line

1. Verify completed collection and interpret the actual results, including nulls and limitations. Review every numeric claim against the regenerated bundle.
2. Pilot curation is complete locally: eight episodes reproduce the locked decision, with a hashed receipt. Verify both that receipt and the eventual evaluation export again before publication; neither is published yet.
3. Resolve publication visibility/licence with the author only after the reviewed payload is concrete. Add actual accessible code/data links to the paper and test them.
4. Render and inspect the final empirical DOCX/PDF, complete the runbook submission checklist and preserve hashes of the delivered artifacts.
5. `scripts/export_observatory.py` now prepares source-bound final snapshots, descriptive summaries and witness details from a completed curated evaluation export. Run it with `--run .../curated-records --output .../exhibit-data` after collection. Witness detail is the first complete scenario in locked order, never outcome-selected. The four-exhibit interface is implemented and checked against a labelled representative fixture (46 browser checks; desktop and phone visual review). After the automatic build, run `node observatory/research/check_research.mjs --release runs/report-output-2026-11-06/exhibit-review --experimental`, inspect actual rendered views and verify actual release sizes before any publication. The old scripted shell remains explicitly separate.
6. The author requested one final submission on Sunday. Do not claim submission or completion without the actual confirmation receipt.

The existing prior-work inventory and history remain accurate. The author declined a separate pre-sprint boundary tag; none was created. Today's continuation and actual evaluation freeze are dated 6 November in Vancouver.

Reporting correction R-001 is recorded in `REPORTING_CORRECTIONS.md`: concern submissions now count in the descriptive all-attempts action denominator. The finisher was refreshed to load it; scientific source hashes remain frozen. The offline suite now passes 162 tests.

7 November continuation: four-exhibit preparation and its optional unattended finishing step are ready. The idle finisher was refreshed successfully with `--wait --exhibits` (PID 60889 at 07:08 UTC); the paid collector was untouched. Always read current status rather than trusting a saved PID. An earlier approval-service usage limit temporarily blocked one browser-check launch; the retry after the stated reset passed all 46 checks.

Before manuscript interpretation, run the independent final-allocation arithmetic audit:

```bash
.venv/bin/python scripts/audit_report_records.py --run runs/report-output-2026-11-06/curated-records --output runs/report-output-2026-11-06/allocation-audit.json
```

It compares act-reconstructed primary and secondary outcomes with separately logged final district rows, then checks cell means and point contrasts using direct arithmetic. It does not replace the frozen bootstrap. The suite now passes 169 tests. The 7 November layout rehearsal (v7) remains five main pages and two reference/appendix pages, including R-001 and complete reference author lists; it is still synthetic QA only.
