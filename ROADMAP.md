# Roadmap to the Seventh Seat finish line

Living review · 3 November 2026 · Vancouver dates. This roadmap implements the charter, design freeze, errata E-001–E-013 and runbook; it does not amend them.

## Current update — Thursday 5 November

**This update supersedes the pending-GM/dry-run statements in the historical sections below.** Both configurations passed gm-v2; GPT-6 Luna is selected and GM is closed. C-1 corrects replay selection without changing the live decision. The end-to-end scripted rehearsal passed 18 checks on 4 November. Current verification: 94 tests and four frozen hashes passed; browser checks were not rerun today.

Today's preparation adds a bounded novelty review and claim register, a report outline based on the official template, candidate references, pre-sprint inventory, and an explicit Friday handoff. Two close literature leads still need primary manuscripts, so G0 is open and no priority claim is made. The author approved the calibration rule (D-028/E-014) before data and confirmed survey/Discord complete. Infrastructure wording now matches E-010. See `docs/THURSDAY_HANDOFF.md` for the current checklist and event times.

Remaining before the pre-sprint boundary: primary-source follow-up, console spending-control confirmation, review/commit and the actual `pre-sprint-2026-11-05` tag. Friday still owns interventions, the hazard-world runner, analytics, calibration and evaluation. The existing no-hazard recovery runner is not the evaluation runner. No experimental results exist.

## Progress update — Wednesday work completed early, 3 November

Provider adapters, bounded tool loop, response cache, containment checks, attention/spend enforcement and retry/recovery are implemented. 70 Python tests pass. Both real-provider no-hazard smoke episodes complete and replay to byte-identical logs. Conservative combined token-cost accounting is US$0.021538685, with no unresolved reservations. See `docs/WEDNESDAY_HARNESS.md`. GM qualification and experimental work are still pending. The baseline assessment below records the earlier review; its missing-harness items are superseded by this update.

## Where we were at the review

The deterministic foundation and scripted exhibition exist. The LLM experiment does not yet exist end to end. There are no experimental findings to present.

- Verified in this review: all 43 Python tests pass; all four files in FREEZE_MANIFEST.sha256 match their hashes.
- Implemented: world engine, certified scenarios, oracle, permits, seeded scheduling, hash-chained events, scripted agents, snapshot fixtures, diorama, static release builder and browser-check infrastructure.
- Browser coverage: project records report 97 checks. These were not rerun in this review; current visual appearance and release checks are not independently re-certified here.
- Author reports successful OpenAI and Anthropic model-metadata checks. This confirms access, not generation, reasoning continuity, valid tool use or model qualification.
- Missing: provider adapters, response cache and full agent tool loop; enforced spend accounting; qualification; E/S interventions and supervisor; experimental analytics; authenticated experimental snapshot export; report and evaluation dataset.
- Working tree already contains an untracked API-check helper and a modified assistance log. Review these with the author’s next commit.

The exhibit must remain explicitly scripted until it is connected to verified experimental records. Scenic water, lighting and symbols are metaphors; calibrated quantities must derive from the snapshot. A syntactically valid manifest hash alone does not authenticate a dataset.

## Wednesday 4 November — make one trustworthy episode possible

1. Implement the two fixed E-010 provider configurations, preserving provider-specific reasoning and continuation state. Add the nine-tool dispatcher and cache, with complete request/response provenance and no credentials in logs.
2. Enforce world-only access and per-phase action limits. Test containment (G1), cached state-hash replay (G2), attention limits (G6), and sequential/parallel tool calls, continuation, truncation and recovery (GA).
3. Add persistent cost accounting with reservations for in-flight calls. Enforce the qualification/pilot and overall caps; stop cleanly when funds or quota are insufficient. Record actual provider rate limits and available balances. The current account funding is not the same thing as the protocol’s maximum authorized budget.
4. Classify valid calls, refusals, abstentions, invalid calls, infrastructure errors and truncations separately; implement E-010 retry and episode-rerun rules.

**Done when:** one bounded episode completes through the real adapter path and replays identically from cache; failure cases and budget stopping pass. Save commands and evidence in the project log. Do not begin evaluation.

## Thursday 5 November — qualify and rehearse

1. Run GM on the dedicated no-hazard world: the prescribed deterministic checks and short episodes for each configuration. Apply the schema-validity, rule-following and critical-violation criteria before selecting by measured cost per evaluable episode (latency tie-break). Never choose using harm outcomes.
2. Finish G0: verify the prior-art ledger and write the precise contribution sentence. Resolve unverified citations by verifying, replacing or removing them.
3. Complete an end-to-end scripted rehearsal: scenario → agents/tools → event log → replay → output artifacts. Include interrupted-run recovery and a budget-stop rehearsal.
4. Resolve draft protocol ambiguities before Friday’s lock: calibration boundary behavior and the meaning of “at most three adjustments”; align infrastructure exclusions with E-010’s one episode rerun. Record author decisions explicitly; do not silently change the design.
5. Finalize PREEXISTING_WORK.md and README disclosure; log actual pre-sprint effort, including visual work. Author reviews and commits, then tags pre-sprint-2026-11-05.

**Done when:** a qualified configuration, measured costs, passing harness gates, reproducible rehearsal and accurate pre-existing-work boundary are recorded. If neither configuration qualifies, fix and requalify; do not declare readiness.

## Friday 6 November — kickoff, interventions, then evaluation lock

Kickoff readiness means a qualified harness and a declared starting point. It does not require completed research or a finished public observatory.

1. Re-read the live sprint rules and confirm submission logistics.
2. Implement the weekend research: E0/E1 evidence, S0 endorsements/S1 direct route and the scripted supervisor. Preserve the same tool surface across cells and no numeric leakage through the neutral HOLD notice.
3. Pass G4 identity, G5 evidence integrity, G8 attributable escalation/identical supervisor policy and G9 truth/act-based analytics. Check analytics against hand-computed fixtures before evaluating models.
4. Apply and log the preregistered calibration procedure (G11); exclude pilot data. Treat the global falsifier honestly if reached.
5. Record the full Evaluation lock: protocol commit, model/configuration, prompt/tool hashes (G10), parameters, seeds/strata, comparisons and fixed stop. Author tags prereg-frozen. Only then launch evaluation.

**Go/no-go:** no evaluation while any required gate or lock field is missing. Delayed readiness reduces completed sample size; it does not justify weakening the protocol or moving the fixed stopping time.

## Saturday 7 November — finish collection and compute

Complete blocked four-cell scenarios where possible. Stop at 23:00 Vancouver (Sunday 06:00 UTC), independent of observed results. Account for missing cells, failures and refusals under the frozen rules. Recompute outcomes, scenario-cluster uncertainty and the protection ladder from released records. Optional arms come only after primary work, within budget.

## Sunday 8 November — make every claim inspectable

Write and check the eight-page report, required abstract and appendices, verified references and prior-work disclosure. Provide documented commands that reproduce every reported number from the released logs. Check PDF links and code availability. Target the single final submission at 20:00 Vancouver, with confirmation received; verify the official deadline Friday.

A verified illustrative episode may support the report. Complete interactive Witness Record, Two Rivers and other observatory expansion can follow submission under E-011. Do not trade reproducibility or report quality for additional visual effects.

## Finish line

The submission is finished when the charter’s acceptance criteria hold: compliant report; recomputable numbers; verified citations; disclosed prior work; and hosting-budget compliance if an exhibit is deployed. A null or descriptive result can meet this finish line. A beautiful display with unsupported claims cannot.

The later observatory is finished when its four exhibits trace every quantitative mark to authenticated released records, separate what happened from what agents could know, distinguish concern from understanding, preserve calibrated comparisons and accessible fallbacks, and remain static and within budget.

## Ben’s remaining decisions and actions

- Note provider rate limits and configure spending controls; keys and basic access are already done. Keep credentials private.
- Review the protocol clarifications before lock, and decide publication/license and affiliation details before release.
- Own commits, tags, pushes, deployment and final submission, as specified in the charter.
- Keep Wednesday and Thursday focused on the harness and qualification. Resume visual polish only after research gates pass and within the declared scope.
