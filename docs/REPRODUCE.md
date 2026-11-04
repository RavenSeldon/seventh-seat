# Reproducing the Records

**Status:** LIVING, 4 November 2026 (pre-sprint). Covers what exists now: tests, frozen documents, the end-to-end dry run, and Gate GM qualification. The weekend's evaluation commands are added on Sunday, when the release is curated (Charter acceptance criterion 2).

## What Each Command Needs

| Command | Network | Credentials | Spend | Private files |
|---|---|---|---|---|
| Tests, frozen check, dry run | none | none | none | none |
| GM replay and rescore | none | none | none | cache, run records, ledger |
| GM live run | provider APIs | `.env.local` | charged to the ledger | writes all three |

Never re-run a live qualification to "reproduce" it: its records are the evidence, and a fresh run is a new sample.

## Environment

Python 3.10 or later. Tests, the dry run and replay use the standard library only. Live provider calls need the optional pinned SDKs (`pip install -e '.[providers]'`: `openai==3.42.1`, `anthropic==2.4.0`). The browser checks need Node 18+ (`make diorama-setup`, once).

## 1. Tests and Frozen Documents

```sh
make test      # 94 tests: world, oracle, permits, harness (G1, G2, G6, GA), GM scoring and correction, dry run
make frozen    # docs/00, 01, 02, 06 match FREEZE_MANIFEST.sha256
```

## 2. End-to-End Scripted Dry Run

```sh
make dry-run   # writes runs/scratch/dry-run-<UTC timestamp>/; prints passed and any failed check
```

Scenario seed 9001 (outside every reserved range), certified by the oracle (G3, G3b); six agents through the real model-call path in the selected configuration's request shape (GPT-6 Luna) with a scripted transport; hash-chained log; cached replay byte-identical; outcomes recomputed from act records; a validated `scripted-fixture` snapshot; interrupted-run recovery; a budget stop before any request; the real ledger untouched. Two episodes: the E-005 trade reference (withdrawal 84, shortfall 14, as certified) and no trade (68, within the cap).

- Recorded run: `experiments/dry_run_2026-11-04.json` (18 checks passed).
- **Determinism.** Independent runs, on Linux with Python 3.10 and on macOS with Python 3.12, give identical world-state sequences (`state_sequence_sha256`) and outcomes. Log bytes differ between independent runs only by measured call latency; a cached replay is byte-identical.
- All dry-run numbers are scripted fixtures, never experimental data.

## 3. Gate GM Qualification (Decided: GPT-6 Luna, `gm-v2`)

The live decision is `experiments/gm/v2/qualification_result_live.json`; the history is in `experiments/gm/` (`gm-v1` failed; audit; `gm-v2`; correction C-1). To reproduce scores and the decision without any provider call:

```sh
.venv/bin/python scripts/run_qualification.py run --provider openai --replay --tag live
.venv/bin/python scripts/run_qualification.py run --provider anthropic --replay --tag live
.venv/bin/python scripts/rescore_qualification.py --tag replay-live
```

- Each command verifies the `gm-v2` declaration first and refuses if any declared source changed.
- Replay directories and the corrected artifact are written once and never overwritten; to repeat, use a new tag (`--tag live` with a fresh `replay-` directory is refused if it exists, so move the old one aside first).
- The corrected artifact withholds cost-based selection on replay evidence alone and reproduces the live selection from verified historical cost. Do not use `score --tag replay-live` for the decision (superseded; see `qualification_result_replay-live.SUPERSEDED.md`).
- Replaying `gm-v1` needs its archived sources (`experiments/gm/v1-sources/`) restored over the tree.

## Private Records and Publication

Kept out of git (`.gitignore`): `runs/cache/` (exact provider requests and responses, including opaque reasoning state), `runs/scratch/` (run records, event logs, the budget ledger) and `.env*`. The published JSON in `experiments/` carries scores, hashes and amounts, not credentials or opaque state. Recomputing GM scores therefore needs the private records; before release, the author decides which logs to curate and publish.
