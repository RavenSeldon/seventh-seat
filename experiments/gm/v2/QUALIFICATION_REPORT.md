# Gate GM: Qualification Report `gm-v2`

**Date:** 4 November 2026 (declared 08:22:17 UTC; runs 08:22–08:35 UTC). **Data status:** `gm-qualification-no-hazard`, pre-sprint, declared. Not experimental evidence.
**Specification:** `QUALIFICATION_SPEC.md` (D-025), hashed in `DECLARATION.json` before any `gm-v2` call. **Result:** `qualification_result_live.json`.
**Provenance:** this revision followed the failed `gm-v1` attempt (`../QUALIFICATION_REPORT.md`, `../GM_V1_AUDIT.md`), which stays on record unchanged. It adopted three corrections to the instrument (rules reference, documented entitlement reservation, explicit allocation objective) and no change to configurations, worlds, keys, thresholds or the selection rule.

## Decision

**Both configurations passed `gm-v2`. Selected: GPT-6 Luna (`gpt-6-luna`, Responses API, reasoning effort medium), by lowest spend per evaluable episode.**

| Criterion (E-010) | GPT-6 Luna | Claude Haiku 5.5 |
|---|---|---|
| Schema-valid tool calls ≥ 95% | 109/109 ✓ | 105/105 ✓ |
| Rules ≥ 9/10 | 10/10 ✓ | 10/10 ✓ |
| Basic allocation tasks (A1–A4; all episodes at minimum need) | all ✓ | all ✓ |
| No unresolved critical violation | 0 violations ✓ | 0 violations ✓ |
| Adapter gate (offline suites 42/42; live continuation; no format rejection) | ✓ | ✓ |
| **Qualified** | **Yes** | **Yes** |
| Spend per evaluable episode (3 evaluable) | **US$0.008661282** | US$0.023473200 |
| Median episode latency (sum of call latencies) | 110.6 s | 81.9 s |

The ranking is identical under the measured and upper spend bounds (no unresolved reservations). Latency did not enter the decision because costs were not tied.

## Evidence

- Allocation commits equal their keys for both: A1 (8, 0), A2 (4, 5), A3 (3, 4), A4 (6, 2).
- Tool checks T1–T3 passed for both. No provider refusals, truncations, infrastructure errors or rate-limit errors.
- Episodes, all evaluable with six explicit commits and every district at or above minimum need. Demand met (recorded, not scored): Luna 48/48, **44/50**, 51/51; Haiku 48/48, 50/50, 51/51. Luna's gm-q2 shortfall in demand fulfilment is within the gate but is worth knowing.
- Provider-reported model strings: `gpt-6-luna`, `claude-haiku-5-5`.

## What Changed Between `gm-v1` and `gm-v2`, and What That Does Not Show

The `gm-v1` failures stand: Luna left a district below minimum need (A2) and missed two rules items; Haiku overspent its credits (A3). Under `gm-v2` the same tasks, keys and thresholds were met by both after the instrument corrections. This shows the configurations pass a better-specified instrument once each. It does not show which correction mattered, that `gm-v1` failures were caused by the instrument, or how either configuration behaves in repeated runs: both results are single samples. Allocation probes now carry a more explicit objective than the episodes and the eventual experiment.

## Spend (Calculated From Provider-Reported Usage at Published Rates; Not Invoice)

| | `gm-v1` | `gm-v2` | Qualification total |
|---|---|---|---|
| GPT-6 Luna | US$0.022663235 | US$0.025983845 | US$0.048647080 |
| Claude Haiku 5.5 | US$0.066274000 | US$0.070419600 | US$0.136693600 |
| **Total** | US$0.088937235 | **US$0.096403445** | **US$0.185340680** |

Ledger: 774 settled charges, none unresolved; total US$0.206879365 = smoke US$0.021538685 + qualification US$0.185340680. `gm-v2` ledger rows equal the cache's per-call charges to the nanodollar. Caps unchanged (US$4 total, US$2 per provider). The selection rule uses `gm-v2` spend only, as declared.

## Verification

- 85 tests pass (15 GM), including checks of the actual outgoing requests: every rules question carries the identical world-tool reference with `answer` the only callable tool; both reservation sentences appear in every world request for both providers; the allocation objective appears only in A1–A4; keys equal the independent optimum of the stated objective; only the declared task text differs from the archived `gm-v1` module.
- Frozen founding docs verified. `gm-v1` public results and private records are byte-identical to before `gm-v2`; its sources are archived in `../v1-sources/` and match its declaration.
- Replay reproduces every `gm-v2` score and all six episode logs exactly.

## Defect Found After the Run (Not Corrected)

`score --tag replay-live` applies the selection rule to replay records, which carry no ledger spend. Both costs read as US$0, so the rule reports a cost tie and "selects" Haiku on latency. **The `decision` field in `qualification_result_replay-live.json` is invalid and must be ignored**; that file evidences score and log reproducibility only. The live decision is unaffected (it uses the ledger). The scorer is a hashed `gm-v2` source, so a fix (withhold selection when spend is unavailable) awaits a recorded author decision under D-025; it would change no live result. The `gm-v1` replay file contains the same field but selected nothing.

## Consequences for the Experiment

- The tool descriptions now include the reservation sentences, so the 3 November smoke replays only with the archived `gm-v1`-era sources. Prompt and tool-description hashes are fixed at G10 (Friday) as planned.
- For the Evaluation lock (E-009, 03 §8): model `gpt-6-luna`, Responses API, reasoning effort medium, no temperature, `max_output_tokens` 4096, encrypted reasoning items returned.
- Account limits observed for OpenAI: 5,000 requests and 2,000,000 tokens per minute.

## Reproduce

```sh
.venv/bin/python -m unittest discover -s tests -t .
.venv/bin/python scripts/run_qualification.py run --provider openai --replay
.venv/bin/python scripts/run_qualification.py run --provider anthropic --replay
.venv/bin/python scripts/run_qualification.py score --tag replay-live   # scores only; ignore its decision field
```

Replay needs the private cache (`runs/cache/gm-v2`) and run records (`runs/scratch/gm-v2`); the live score also needs the ledger.

## Correction C-1 (4 November, D-026)

The defect above is now corrected, outside the declared `gm-v2` sources, which remain unchanged with every earlier output.

- `qualification_correction.py` and `scripts/rescore_qualification.py` treat missing cost evidence as unavailable, never US$0; withhold cost-based selection when a passing configuration lacks evidence; report a replay's own additional charge (zero) separately from the original qualification spend; and accept historical spend only after verification. Eight tests cover missing cost, genuinely zero cost (zero-charge ledger rows remain evidence), verified history reproducing the live selection, and unverifiable history.
- Corrected artifact `qualification_result_replay-live.corrected.json` (own provenance: correction source hashes, `gm-v2` declaration hash, 42 + 8 offline tests passing): selection withheld on the replay's own evidence; with verified historical cost, **GPT-6 Luna**, identical to the live decision.
- The invalid replay decision is explicitly superseded: `qualification_result_replay-live.SUPERSEDED.md`. The "ignore its decision field" comment under Reproduce no longer applies; use the corrected command below.

```sh
.venv/bin/python scripts/rescore_qualification.py   # after the two replay runs; writes the corrected artifact once
```

The five declared interpretations are retained for this completed qualification (D-027).

