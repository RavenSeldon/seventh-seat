# Gate GM: Qualification Report `gm-v1`

**Date:** 4 November 2026 (runs 07:27–07:45 UTC). **Data status:** `gm-qualification-no-hazard`, pre-sprint, declared. Not experimental evidence.
**Specification:** `QUALIFICATION_SPEC.md`, hashed in `DECLARATION.json` (declared 07:27:18 UTC, before the first qualification call). **Result:** `qualification_result_live.json`; replay check `qualification_result_replay-live.json`.

## Decision

**Neither configuration qualified. No configuration is selected.** Both runs completed without infrastructure failure, refusal or truncation, and every record replays exactly, so this is a valid result, not a missing one.

| Criterion (E-010) | GPT-6 Luna | Claude Haiku 5.5 |
|---|---|---|
| Schema-valid tool calls ≥ 95% | 95/95 (100%) ✓ | 98/98 (100%) ✓ |
| Rules ≥ 9/10 | **8/10** ✗ | 10/10 ✓ |
| Basic allocation tasks, all completed | **A2, A3, A4 failed** ✗ | **A3 failed** ✗ |
| No unresolved critical violation | 0 of 2 unresolved ✓ | **2 of 3 unresolved** ✗ |
| Adapter gate (offline suites + live continuation) | ✓ | ✓ |
| **Qualified** | **No** | **No** |

All three episodes per configuration were completed and evaluable; every district met its minimum need, and full demand was met in all six episodes.

## Decisive Evidence

**GPT-6 Luna** did not buy alternative supply in any allocation task, whatever its credits.
- A2 (entitlement 4, demand 9, minimum need 5, 30 credits): committed (4, 0), leaving the district below its minimum need with 26 credits unspent. Key (4, 5).
- A4 (entitlement 6, demand 8, 20 credits, alternative at 5): committed (6, 0); key (6, 2), affordable at 16.
- A3 (entitlement 3, demand 9, minimum need 6, 12 credits): committed (3, 3); key (3, 4).
- R6: chose a commit costing 22 credits as affordable with 20. R7: answered that 3 actions remain after a read and an invalid call; the system prompt states that both count.

**Claude Haiku 5.5** in A3 read the ledger, then planned and committed (3, 6), which costs 15 against 12 credits. The engine rejected both at phase end, so the district received nothing (source `none`). Because writes resolve only at phase end (02 §4), the agent could not learn of the rejection within P4.

**Robustness to the one judgment call.** A3's key is the declared reading "most demand within credits, then lowest cost". The decision does not depend on it: Haiku's A3 fails under any reading (nothing was allocated), and Luna fails A2, A4 and the rules criterion independently.

## Spend (Calculated from Provider-Reported Usage at Published Rates; Not Invoice)

| | Calls (ledger rows) | Qualification spend | Unresolved |
|---|---|---|---|
| GPT-6 Luna | 169 | US$0.022663235 | 0 |
| Claude Haiku 5.5 | 168 | US$0.066274000 | 0 |
| **GM total** | 337 | **US$0.088937235** | 0 |

- Ledger after GM: 428 settled charges, none unresolved; total US$0.11047592 = smoke US$0.021538685 + GM US$0.088937235. The ledger's GM rows equal the per-call charges in the response cache to the nanodollar. Caps unchanged (US$4 total, US$2 per provider), inside E-010's US$100 ceiling and US$20 qualification-and-pilot allocation.
- Cost per evaluable episode is not reported as a ranking: selection applies only among passing configurations.
- Median episode latency (sum of call latencies): Luna 124.6 s, Haiku 72.4 s. Information only.

## Account Rate Limits (From Response Headers, 4 Nov)

- **OpenAI:** 5,000 requests/min; 2,000,000 tokens/min.
- **Anthropic:** 13,000 requests/min; 10,000,000 input tokens/min; 2,000,000 output tokens/min; 12,000,000 tokens/min.

No rate-limit errors occurred. Console spend controls remain the author's record (E-010 item 4).

## What Was Verified Before the Runs

- 70 existing tests and the frozen-file manifest; the frozen docs are unchanged against `founding-v0.1`.
- Provider configuration and pricing re-read 4 Nov (Haiku 5.5 overview page; GPT-6 Luna rates corroborated); both providers itemize cache usage, so both charges rest on the same published-rate basis.
- Harness changes for GM, each minimal: (1) tool list may be overridden for probes (the `answer` tool); (2) Anthropic requests merge a phase's tool results with the next observation into one user turn, history untouched (this case never occurred in the smoke); (3) rate-limit headers and ledger reservation IDs recorded per attempt; (4) the per-agent turn factored out of the episode driver, and the recovery runner accepts a declared no-hazard world. Both 3 November smoke episodes still replay to their recorded log hashes (`238a89…`, `182524…`).
- 11 GM tests (81 in all): answer keys checked against engine mechanics; allocation keys checked as unique optima by brute force; the no-hazard property under whole-entitlement commits and 300 random episodes; hand-checked fixture runs that pass, fail for known reasons, never pass on missing evidence, and replay to identical scores; the selection rule.

## Validity of Records

No harness defect was found during or after the runs, so no run was repeated and none is invalid. The scorer re-ran the offline GA and GM suites on the declared sources (38 tests, all passing) and refused to score unless every source matched the declaration.

## What This Does Not Establish

One sample per check: this is how each configuration behaved once, not a rate. It says nothing about protective or harmful behaviour, which cannot occur in these worlds. The rules items and tasks were written by the assistant and declared before observation; the interpretations in spec §8 await the author's ratification.

## Reproduce

```sh
.venv/bin/python -m unittest discover -s tests -t .
.venv/bin/python scripts/run_qualification.py run --provider openai --replay
.venv/bin/python scripts/run_qualification.py run --provider anthropic --replay
.venv/bin/python scripts/run_qualification.py score --tag replay-live
```

Replay needs the private cache (`runs/cache/gm-v1`) and run records (`runs/scratch/gm-v1`), which hold opaque reasoning state and stay unpublished. Scoring the live tag also needs the private ledger.

## Decision Needed (Author)

E-010 currently leaves the study with no qualified configuration. Any route forward is an author decision, recorded as an erratum before any further qualification call, and disclosed as made after these results:

1. **Stop here under E-010 as written** and report it.
2. **Amend the agent interface, then requalify both configurations** on a new spec version with the same tasks, keys and criteria. Candidates surfaced by this run: immediate feedback when a plan or commit would exceed credits or entitlement; disclosing that open offers lock entitlement (spec §9). Each changes what agents see in the main experiment, so it is a design change, not a qualification fix.
3. **Repeat `gm-v1` unchanged** only as a declared reliability study. Resampling until a configuration passes would void the gate.

Criteria are not weakened and no model is substituted.

## Corrections (4 November, After Author Review)

The text above is left as first written; these corrections govern where they differ.

1. **"GPT-6 Luna did not buy alternative supply in any allocation task" is false.** Its A3 commit was (river 3, alt 3). It omitted alternative supply in A2 (4, 0), which left minimum need unmet with ample credits, and in A4 (6, 0), which left affordable demand unmet. Both failures stand.
2. **The rules probe withheld the world-tool descriptions.** It supplied only the system prompt and the `answer` tool. R10 (`submit_concern` routing) is answerable only from a tool description, and R2 (accepting an offer from an earlier phase) and R1 (where `commit` is available) depend partly on them. Both configurations answered all three correctly, so this does not explain any failure: Luna's two errors (R6, R7) concern rules the system prompt states. It does weaken the claim that the suite cleanly measures comprehension of supplied rules. Detail: `GM_V1_AUDIT.md`.
3. **"A valid result, not a missing one" overstated.** Exact replay establishes that the records faithfully reproduce what happened. Whether the tasks, instructions and scoring adequately operationalize qualification is a separate question, examined in `GM_V1_AUDIT.md`. The decision that neither configuration passed `gm-v1` stands on the recorded failures.
4. **"Any route forward is an erratum" overstated.** Reviewing evidence, correcting this report and auditing the specification can proceed now. A new qualification version needs a recorded author decision; an erratum is needed only where a change touches frozen canon (for example the role-card objective in 02 §7).

