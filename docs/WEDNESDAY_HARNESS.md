# Wednesday harness: implementation and verification

Living engineering record, 3 November 2026. Governing sources: world specification as amended by E-002/E-003/E-004 and provider/budget requirements E-010. This is pre-sprint work. It does not implement the weekend interventions or freeze experimental prompts.

## What is implemented

- The two fixed configurations: GPT-6 Luna through Responses, medium reasoning; Claude Haiku 5.5 with adaptive thinking, medium effort. No sampling overrides. Official SDKs disable automatic retries; the harness owns retries.
- Nine schema-checked world tools. Actor identity comes from the runner, never from tool arguments. Invalid schemas, unknown tools and attention overruns are rejected and logged. There are no model-accessible filesystem, shell, network, code-execution or provider-hosted tools.
- One private append-only history per district, including provider-required opaque reasoning state. Every parallel tool call receives a corresponding result. Refusal/truncation produces no world action, including when complete tool calls accompany an incomplete response.
- Exact request/response cache, keyed by provider, full request, scenario, cell, actor, phase, turn and episode attempt. Different episode attempts cannot accidentally reuse each other's samples. Replay requires cache hits and never loads credentials or calls a provider.
- Engine observations, action outcomes and model-call classifications are logged separately. Exact requests and raw responses live in the private cache; event records contain hashes and references, not opaque reasoning. These are transport artifacts, not evidence of beliefs or understanding.
- Persistent SQLite reservations in integer nanodollars. Transactions prevent concurrent overscheduling. Usage includes output reasoning tokens through the provider's total output field. An interrupted request retains its full reservation when billing is unknown. Never delete the ledger to reset a limit.
- At most three transport attempts, fixed two-second backoff; one full episode rerun on infrastructure failure, with identical scenario/cell/seed/engine episode ID but a separate attempt cache namespace. A second interrupted episode is marked missing. Refusals are not retried.

## Budget and pricing

The smoke command has a shared US$4 total/preparation cap and US$2 per provider, below E-010's US$100/US$20 ceilings. These caps persist across invocations. This ledger records smoke costs that must carry into subsequent qualification/pilot accounting; future budget expansion must preserve the existing charges and explicitly record revised caps, not start a fresh budget pretending earlier costs were zero.

Before each request, reserve the entire advertised context window rounded up to 1.1 million tokens at the highest applicable long-context/cache-write rate, plus the requested output maximum. This deliberately avoids estimating the size of opaque reasoning. It can stop scheduling with money still available; that is conservative headroom, not a claim that the request will cost that much. Lost responses can exhaust this headroom quickly and need billing reconciliation.

Usage-based dollar figures are calculated from the dated standard global API rate card; they are not provider invoice reconciliation. Missing cache-write detail is conservatively priced. No batch, regional premium, fast tier, hosted-tool fee or external spending is included. The runner uses the direct default provider endpoints and only custom world tools. Recheck pricing/configuration before qualification and before evaluation lock.

## Commands

From the repository root:

```sh
.venv/bin/python -m unittest discover -s tests -t .
shasum -a 256 -c FREEZE_MANIFEST.sha256
.venv/bin/python scripts/run_harness.py --provider openai --output runs/scratch/wednesday-openai-live
.venv/bin/python scripts/run_harness.py --provider anthropic --output runs/scratch/wednesday-anthropic-live
.venv/bin/python scripts/run_harness.py --provider openai --replay --output runs/scratch/wednesday-openai-replay
.venv/bin/python scripts/run_harness.py --provider anthropic --replay --output runs/scratch/wednesday-anthropic-replay
```

Output directories must be new. The default episode ID is stable for replay; choose a new `--episode-id` for a deliberately new sample. Reusing an ID intentionally reuses cached results. `--max-tokens` must match for replay. Never use these commands to create main evaluation data: the CLI is restricted to the dedicated no-hazard fixture and preparation spending.

Live runs use `.env.local` through the existing safe parser, with environment fallback. Offline tests need only the standard library. Live calls require the optional `providers` dependencies. Raw provider histories and the budget ledger remain in ignored local run directories; curate reproducibility artifacts before public release.

## Verification observed on 3 November

70/70 Python tests pass (43 existing, 27 harness tests); all frozen hashes match. Both live provider episodes completed the fixture: demand met 48/48, six commits. OpenAI used 48 calls; Anthropic 43. Both complete event logs replay byte-for-byte identically with the final harness implementation. There were no live refusals, truncations or infrastructure errors; those branches were exercised by offline wire fixtures.

Combined conservative usage accounting: US$0.021538685 (OpenAI US$0.006471585; Anthropic US$0.015067100). All reservations were settled after both processes finished. The first smoke used conservative cache-write accounting; subsequent code itemizes cache writes when the provider reports them. Historical charges were preserved. The shareable evidence record contains log hashes and source hashes, not credentials or opaque state: `experiments/harness_smoke_2026-11-03.json`.

A normal end-of-turn text response is classified `model_abstention` at the call level even when earlier calls in that turn acted. These counts are not episode-level refusal or task-failure rates.

## Acceptance and limits

Offline tests cover G1 containment, G2 complete cached episode replay, G6 action and financial limits, and GA wire-format continuity, parallel calls, truncation and error recovery for both providers. Adversarial fixtures are not model qualification. A live smoke validates the integration path; it does not prove all real-provider GA edge cases or satisfy GM.

The fixture has total entitlements 60, total demand 48, and safe cap 70. Any entitlement-valid execution remains below the cap. Its seed 17 is outside calibration/evaluation ranges. It is labelled `harness-no-hazard-smoke`, never experimental evidence. The same engine and tools are used, with reporting routes explicitly unconfigured until Friday.

Calls containing mixed tool results are conservatively classified invalid if any immediate result fails; per-tool results and final phase-resolution events remain available. A queued write is not yet a successful world action. Analytical validity must use the final engine events, not infer success from the call classification.

Before Thursday qualification: declare the GM checks/tasks; record actual account RPM/TPM limits; verify usage/pricing and handle any unresolved reservations; review prompt/tool descriptions and default 2048-token output limit. Preserve fixed medium effort. Qualification, model selection, E/S interventions, supervisor, experimental analytics and evaluation lock remain separate work.

## Provider references (read 3 November 2026)

- [OpenAI model configuration, context and pricing](https://developers.openai.com/api/docs/models/gpt-6-luna)
- [OpenAI reasoning-item preservation](https://developers.openai.com/api/docs/guides/reasoning)
- [Anthropic Haiku 5.5 changes and append-only thinking history](https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5)
- [Anthropic model limits and pricing](https://platform.claude.com/docs/en/models/haiku-5-5/overview)
- [Anthropic tool-result handling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls)

## Changes on 4 November (Gate GM)

Four small changes, made before the GM declaration and hashed with it: probes may pass their own tool list; Anthropic requests merge tool results with the next observation into one user turn (history unchanged); each attempt records rate-limit headers and its ledger reservation ID; the per-agent turn is factored out of `drive` and `run_with_recovery` accepts a declared no-hazard world. Both 3 November smoke logs still replay to their recorded hashes. The `final_replay_source_sha256` entries for `providers.py` and `runtime.py` in `experiments/harness_smoke_2026-11-03.json` describe the 3 November sources; current hashes are in `experiments/gm/DECLARATION.json`. GM outcome: `experiments/gm/QUALIFICATION_REPORT.md`. The `offer` and `plan` descriptions gained one sentence each under D-025 (`gm-v2`), so the 3 November smoke now replays only with the archived sources in `experiments/gm/v1-sources/`.
