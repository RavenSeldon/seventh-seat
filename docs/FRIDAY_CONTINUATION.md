# Friday continuation and unattended execution

6 November 2026. Current implementation and operational record; not a claim of completed research.

The current repository is `/Users/theda/Root/seventh-seat`. The chat workspace's `review/` directory is stale. A hashed snapshot of the inherited Friday work, a reviewed continuation copy, an application manifest and backups live in `/Users/theda/Documents/ChatGPT/Seventh Seat/`.

## Verified implementation

147 Python tests pass. The four founding-document hashes match. Existing browser checks were not rerun because the observatory was not changed. Qualification inputs are archived byte-for-byte under `experiments/gm/v2-sources/`; no qualification result was rewritten or rerun.

Corrections cover completed-log recovery before a manifest, immutable run identities, concurrent-writer exclusion, budget-stop prefixes, malformed/tampered logs, empty contrasts, actual commit precedence, and same-phase invisible proposals. The scripted calibration rehearsal resumes without more transport calls and cannot authorize an experimental lock. Some inherited tests emit SQLite ResourceWarnings; the new production episode runner closes its budget and transport after every attempt.

## Hard spending limits

The author set US$33 per provider with no top-up. The new durable ledger enforces US$66 overall, US$33 OpenAI, US$33 Anthropic and US$20 preparation. It imports the 774 settled historical live charges, US$0.206879365, preserving charge IDs. The original ledger remains read-only. Synthetic dry-run ledgers are excluded. Uncertain requests keep their full reservation; there is no automatic refund/reconciliation or provider switch. The ledger, not a sum of event-log cost fields, is authoritative when interruption prevents a cost event from being logged.

Provider account balances are author-reported; console enforcement was not independently inspected. The local reservation system supplies the enforced run caps. A US$0.278072 OpenAI in-flight reservation is conservative headroom, not a measured charge.

## Controller

`scripts/keep_run_alive.py` adopts the current pilot, waits for a reviewed evaluation lock, runs evaluation and computes analysis. It uses an exclusive process lock and a `caffeinate` assertion tied to its process. It does not create Git tags, authorize an unfinished gate, extend the stop, send notifications, deploy or submit.

Private status: `runs/controller-status.json`. Private process output: `runs/controller.log`, `runs/pilot-worker.log`, `runs/evaluation-worker.log`, `runs/analysis-worker.log`. All `runs/` content is gitignored. Keep the laptop open and connected to working power. `caffeinate` prevents idle sleep while the controller lives; it cannot guarantee survival of lid closure, shutdown, power loss or network loss.

If the controller is interrupted, restart with `.venv/bin/python scripts/keep_run_alive.py`. Existing manifests and attempt budgets govern resumption. A corrupt/torn log fails closed for manual audit. A terminal pilot failure stops collection; it is never silently replaced with another seed. A failed evaluation process also stops for inspection.

## Before evaluation

1. Complete E-014 calibration and inspect its retained trace and timing. The pilot has eight fixed seeds and at most four settings; no outcome-guided resampling.
2. Verify all generated evaluation scenarios with the oracle. Record gate evidence against exact source hashes.
3. Prepare `experiments/evaluation-lock.json` from the actual pilot. Create the author's reviewed protocol commit and `prereg-frozen` tag; the CLI checks the tagged bytes against the lock. The existing pre-sprint inventory and Git history identify prior work. The author declined creating the proposed Thursday tag; this continuation is committed with its actual 6 November date. Prior-work disclosure is retained.
4. The controller may then launch 24 fixed, balanced four-cell blocks. Collection stops launching episodes at 8 November 06:00 UTC (Saturday 23:00 Vancouver); episodes already in flight can finish. New blocks need a measured timing reserve. All omitted/failed cells are reported.

The per-episode outputs include the inherited conservative AWC operationalization; it uses phase-end remaining attention and ordinary-phase routing cutoffs. This is a descriptive proxy, not a causal measure or proof of comprehension. A later methods audit should evaluate its treatment of extra replan opportunity without changing primary outcomes silently.

## Actual finish line

Verified analysis, a report in the official template, all reported numbers recomputable from curated released records, verified citation claims, prior-work/assistance disclosure, and the author's final submission receipt. Neither a pilot nor a passing test suite meets that finish line. Public export, publication/licence, and submission remain outstanding.

## Report and export checkpoint

One completed live pilot episode has replayed from the existing provider cache with a byte-identical event log and no transport or budget supplied; `experiments/live-pilot-replay-2026-11-06.json` records the digest. Six additional export/report checks cover reproducibility, missing blocks, credential-cache exclusion, tampering, symlink rejection and hand-computed table values.

`scripts/export_research.py` creates a local allowlisted export only after the run writer has released its lock and every planned episode is accounted for. `scripts/report_results.py` verifies the export receipt, recomputes the analysis and writes manuscript tables. Neither command publishes anything. The official-template manuscript source in `report/working/` remains explicitly pending empirical results.

The launcher now permits descendant documentation checkpoints after `prereg-frozen` while verifying every bound scientific file, the lock and the gate record against that tag. This preserves resumption without moving the tag. `scripts/finish_outputs.py --wait` waits locally for successful collection, then verifies the export and prepares tables, the bound calibration summary and a private cost estimate. It stops on a collector failure and does not publish or mark the manuscript reviewed.
