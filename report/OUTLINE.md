# The Seventh Seat: Verified Evidence and Reporting Access for an Unrepresented Party

**PRE-SPRINT OUTLINE — 5 November 2026. No experimental results exist. Not a submission-ready report.**

Benjamin Amuwo · Independent researcher (provisional; confirm before submission)

Structure follows Apart's official template, read 5 November: https://docs.google.com/document/d/1_1_27EyZriMlc8n8EBE2YScaeyMjm-8xjR097nmHXAE/edit

Aim for 4–6 main-text pages; eight is the hard cap, excluding references and appendices. This outline and any prose prepared before the sprint are pre-existing work and must be disclosed. Transfer the completed manuscript into the official template and verify its rendered PDF before submission.

## Abstract

**Write last, 150–250 words.** Include the question, synthetic setting, realized sample/model, effects with uncertainty, and a conclusion supported by those results. If calibration fails, explicitly describe the study as descriptive. Do not substitute qualification scores or scripted fixtures for findings.

## 1. Introduction (about half a page)

- Problem: coordinated resource use can impose costs on a party outside every acting district's objective.
- Research question: do verified projections and access to authorized review change downstream shortfall, demand fulfilment and protection costs?
- Prospective contribution: a scenario-blocked 2×2 comparison of verified aggregate evidence and consent-gated versus direct reporting to the same scripted supervisor, with downstream shortfall and a record-based account of missed protection opportunities.
- The externality is designed. In this world, harmful withdrawal is never necessary to satisfy legitimate demand; it can reduce the cost of doing so (E-012).
- No claim of being the first absent-stakeholder simulation, the first whistleblowing mechanism or a new hazard-analysis theory. PA-38/39 remain primary-source checks before final positioning.

## 2. Related Work (about half a page)

Use claim-level entries in `docs/04_PRIOR_ART_LEDGER.md`, 5 November addendum. Candidate references are in `references.bib`.

- GovSim (PA-09): sustainable cooperation over agents' shared resources. Our focal shortfall falls on a nonparticipant.
- Danassis et al. (PA-30): a reinforcement-learning policymaker sets prices and allocations for externalities. Our experiment manipulates evidence and access to review, without a price-setting intervention.
- Agrawal et al. (PA-24) and Paglieri et al. (PA-22): disclosure behavior and emergent peer responses already have empirical precedents.
- Rahman (PA-23): credits the proposal of an independent human-oversight route. Our supervisor is scripted; no claim of testing actual human oversight.
- Arslan (PA-17): independent evidence for accountability motivates separating engine records from agent conclusions.
- PHASE (PA-19): system-level hazard analysis and traceable accountability inform the descriptive ladder.
- **Unresolved close comparison:** read PA-38/39 primary manuscripts before describing what they establish or claiming a gap relative to them. The current outline makes no priority claim.

## 3. Methods (about 1½ pages)

### World and intervention regimes

Six fixed-identity district agents, one downstream nonparticipant, four decision phases, tradable entitlements and costlier alternative supply. Describe oracle certification, safe feasibility and the incentive trade-off. State the final calibrated κ and the cheap/costly strata.

| Cell | Ledger information | Reporting route |
|---|---|---|
| E0S0 | Entitlements, trades, F and M | Board proposal plus two other-district endorsements |
| E0S1 | Same basic information | Direct to supervisor |
| E1S0 | Basic information plus VERIFIED projection | Board proposal plus two other-district endorsements |
| E1S1 | Basic information plus VERIFIED projection | Direct to supervisor |

All nine tools are present in every cell; endorsements are inert in S1. The supervisor verifies current ground truth and can grant one qualitative HOLD/replan before the deadline. HOLD is an opportunity to reconsider, not enforced protection. State the information conveyed by the warning and the extra peer-action costs in S0.

### Model, qualification and sampling

- Selected configuration: GPT-6 Luna, Responses API, medium effort, no temperature, maximum output tokens 4096. Record actual returned identifier during evaluation.
- Summarize pre-sprint qualification transparently: gm-v1 failed; gm-v2 corrected three instrument issues, both candidates passed; selection used measured cost, not harm. C-1 corrected replay cost interpretation without changing the live decision.
- **TO COMPLETE:** pilot choice and full calibration trace; model/prompt/tool hashes; protocol commit; frozen seed/stratum/order list; completed scenario blocks; exact infrastructure omissions; fixed stop.
- Scenario is the clustering unit; messages and agent turns are not independent replications. Never use calibration episodes in evaluation.

### Outcomes and inference

Primary: downstream shortfall `max(0, M - (F - total_withdrawal))`. Secondary: breach, demand fulfilled, unmet minimum need, alternative-supply cost, report accuracy/routes, phase latencies and call-outcome classes. Describe E and S regime contrasts and exploratory interaction from the draft preregistration; 10,000 scenario-cluster bootstrap resamples, with a frozen seed. No multiplicity correction; interpret primary contrasts jointly.

AWC and the witness ladder are descriptive. Observable reads, concerns and reports do not establish understanding. Refusal episodes remain included. Report incomplete scenario blocks and how they affect contrasts.

## 4. Results (about 1–1½ pages)

**EMPTY UNTIL EVALUATION.** Populate only from released, reproducible artifacts.

| Planned artifact | Required inputs / claim discipline |
|---|---|
| Table 1: sample accounting | Attempted/completed episodes and blocks, missing cells, refusals, errors, truncations, costs |
| Table 2: cell outcomes | Shortfall, breach, demand fulfilment, unmet need and alternative cost; denominators explicit |
| Figure 1: regime contrasts | E, S and exploratory E×S estimates with scenario-cluster intervals |
| Figure 2: protection process | Descriptive first-failed ladder stage, retaining all failures in released data |
| Optional diagnostic comparison | Only if actually run; separate from the primary factorial |

For every value, record its release file and reproduction command. Show the share of zero shortfalls and conditional shortfall among breaching episodes. Report nulls and failed calibration directly. No illustrative fixture values belong in these tables.

## 5. Discussion and Limitations (about half a page)

Interpret the observed complete-regime contrasts within this synthetic setting. Address small sample and uncertain interaction; one qualified configuration; prompt dependence; qualitative HOLD crossover; unequal action costs of escalation regimes; designed rather than discovered externality; scripted supervision; and selection of complete scenario blocks. Constant tools or prompts do not guarantee equal psychological effects across regimes. Qualification is a single-sample competence gate, not proof of optimal behavior.

## 6. Conclusion

**Write after results.** State the measured answer and its scope. If the estimate is inconclusive, say so. No claim about real communities, ecosystems, consciousness or deployed safety follows automatically.

## Code and Data

- Code: **TO COMPLETE** with a verified accessible release link and commit.
- Data: **TO COMPLETE** with curated event records, release manifest and documented commands.
- Distinguish public artifacts from private provider caches. Opaque provider reasoning state and credentials are not report evidence.

## Prior Work and Author Contributions

Pre-sprint work includes the research design and literature review, world/oracle/runtime, qualification and correction, scripted rehearsal, observatory shell, this outline, and preparation documentation. Identify the final pre-sprint tag and inventory. Weekend contributions must be described from actual work after that boundary, not from the plan. Author: Benjamin Amuwo; assistance is documented separately.

## References

Use `references.bib` and the claim register. Add sources only after bibliographic and passage verification. Do not cite provisional PA-38/39 from an aggregator summary. Do not infer a venue from a search snippet.

## Appendix A. Limitations and Dual-Use / Ethical Considerations (required)

Start from `docs/07_ETHICS_AND_DUAL_USE.md`, then reconcile it with the actual methods, results and errata. Cover synthetic scope, behavior rather than belief, no substitution for real stakeholder representation, the limits of engine-produced verification, and possible misuse of knowledge about failed oversight. State that model-provider API calls occurred; experimental agents had only world tools and contacted no real-world targets.

## Appendix B. Reproducibility and Deviations

Protocol and prompt hashes; model settings; seed/stratum list; calibration log; complete exclusion accounting; all post-lock deviations; exact commands for every reported number. Separate pilot, qualification, scripted fixtures and evaluation data.

## LLM Usage Statement

Draft from `docs/AI_ASSISTANCE_LOG.md`, distinguishing assistance with planning, implementation, review and writing from the author's decisions. State only verification actually performed; do not claim independent verification merely because multiple assistants agreed.
