# Superseded: `qualification_result_replay-live.json` (decision field)

**Superseded by:** `qualification_result_replay-live.corrected.json` (correction C-1, decision D-026), 4 November 2026.
**Superseded file SHA-256:** `0b1a6efa1b7ed747d77eb101160157a87042c1f90e2ba22df60c0869ef20b4db` (kept unchanged as evidence).

**What is wrong.** The declared `gm-v2` scorer, run on cache-only replay records, read their absent ledger spend as US$0 for both configurations, declared a cost tie, and "selected" Claude Haiku 5.5 on median latency. Unavailable cost evidence is not zero cost, so that `decision` and both `spend` blocks are invalid. Every other field (criteria, rules, tasks, episodes, outcome classes, pass/fail) is unaffected.

**What replaces it.** The corrected artifact reuses the declared scorer for every criterion and reports:

- `decision_from_this_run_evidence`: selection withheld, because the replay carries no cost evidence. The replay itself incurred no additional charge.
- `decision_with_verified_historical_cost`: GPT-6 Luna, reproducing the live decision (`qualification_result_live.json`). Historical spend was accepted only after checking that the live ledger rows exist and are settled, that the replay used exactly the live run's cache entries, and that the cached charges equal the ledger.

The live decision was never affected. The `gm-v1` replay file has the same flawed spend fields, but its decision (no configuration passed) does not depend on cost.
