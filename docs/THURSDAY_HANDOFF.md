# Thursday preparation and Friday handoff

Prepared 5 November 2026. This is a pre-sprint planning artifact, not an evaluation lock or a report of experimental findings. Vancouver is UTC−7; event times below are converted from the organizer's UTC schedule.

## Starting point

- Repository reviewed at `63a55ad`; working tree was clean; only `founding-v0.1` existed locally.
- 94 Python tests and all four frozen-document hashes passed on 5 November. One SQLite ResourceWarning appeared; the suite passed. Browser checks were not rerun in this preparation review.
- GM is closed: GPT-6 Luna, medium effort, no temperature, 4096 maximum output tokens; both configurations passed gm-v2. C-1 preserves the live cost-based decision. Do not rerun qualification for a better score.
- The recorded 4 November rehearsal passed 18 checks. It is a scripted fixture, not experimental evidence.
- Interventions and analysis directories contain planning READMEs only. The experimental runner remains weekend work: `run_with_recovery` intentionally refuses hazard worlds.

## Preparation checklist

- [x] Read latest organizer email, live rules/schedule and the official report template.
- [x] Conduct a bounded novelty search; append verified claims and bibliographic corrections to the ledger.
- [ ] Resolve the newly surfaced closest-prior-art leads (PA-38/39) against primary manuscripts. OpenReview requires browser verification; no priority claim is allowed in the meantime.
- [x] Prepare a report outline matching the official template, with explicit missing-result fields.
- [x] Align infrastructure-failure wording in the draft preregistration with existing E-010.
- [x] Record the author's calibration decision (D-028/E-014) and apply it to draft preregistration §6 before any pilot.
- [x] Prepare an inventory of pre-sprint tracked files and today's documentation additions.
- [x] Required participant survey and Discord access: both confirmed complete by the author on 5 November.
- [ ] Confirm provider-console spending controls. Header-derived rate limits and local ledger caps do not establish console configuration.
- [ ] Review the final diff, commit and create `pre-sprint-2026-11-05` at the complete pre-sprint boundary. The inventory is not a tag.

## Friday dependency order

1. Confirm the latest rules and the declared pre-sprint boundary.
2. Implement E0/E1 ledger content, S0 consent-gated/S1 direct routing, endorsements and the identical scripted supervisor. E-004 defines S1 as direct routing; endorsements remain present but inert. Use the qualitative HOLD from E-001.
3. Implement the hazard-world runner with E-010 retry/rerun rules, persistent budget accounting and exact replay. Keep all four cells within the same model configuration and tool surface.
4. Implement truth/act-derived outcomes and descriptive process measures. Verify hand-computed fixtures, identity integrity, evidence integrity and attributable supervision (G4/G5/G8/G9).
5. Apply the settled calibration rule, preserving all pilot attempts and excluding all pilot data from evaluation. Measure runtime and spend here; no-hazard qualification cost is not an evaluation forecast.
6. Complete the evaluation lock: protocol commit; model and settings; prompt/tool hashes; calibration record and parameters; excluded seeds; evaluation seed list and cost-stratum assignment; cell-order and bootstrap seeds; comparisons; fixed stop. Tag `prereg-frozen` only after these are real.
7. Launch evaluation only after required gates pass. Complete scenario blocks where possible. Delays reduce attainable sample size rather than moving the stop or relaxing the protocol.

## Events and fixed milestones

| Vancouver date/time | Item |
|---|---|
| Thu 5 Nov 15:00 | Optional Grant Fleming talk |
| Fri 6 Nov 08:00 | Early logistics session |
| Fri 6 Nov 12:00 | Optional Rowan Howard-Jones talk |
| Fri 6 Nov 13:15 | Optional Elias Stengel-Eskin talk |
| Fri 6 Nov 14:30 | Kickoff keynote, Judd Rosenblatt |
| Fri 6 Nov 15:30 | Logistics session |
| Sat 7 Nov 23:00 | Fixed collection stop (Sun 8 Nov 06:00 UTC) |
| Sun 8 Nov 20:00 | Internal final-submission target |
| Mon 9 Nov 04:59 | Official cutoff (Mon 9 Nov 11:59 UTC; Sun 8 Nov 23:59 AoE) |

RSVP to desired talks for Zoom access. Talks are recorded. This checklist creates no RSVP or calendar event.

## Submission finish line

Official-template PDF, at most eight main-text pages; 150–250-word abstract reflecting actual results; correct author/affiliation; required Limitations and Dual-Use / Ethical Considerations appendix; AI assistance and pre-existing work disclosed; citations verified at claim level; every reported number reproducible from released records; working links; final submission receipt. A null or descriptive result can satisfy these criteria. Additional observatory work follows the research and report priorities.

## Source checks

- Rules/schedule, read 5 Nov: https://apartresearch.com/sprints/swarm-alignment-2026
- Official template, read through connected Drive 5 Nov (modified 4 Nov): https://docs.google.com/document/d/1_1_27EyZriMlc8n8EBE2YScaeyMjm-8xjR097nmHXAE/edit
- Registration checklist: organizer's 1 Nov welcome email; 4 Nov preparation email confirms separate talk RSVPs.
- Vancouver offset: https://engage.gov.bc.ca/govtogetherbc/engagement/daylight-saving-time/

## Decisions still needed before release

Calibration procedure is settled; its actual pilot record is still needed before the evaluation lock. Code/document licence and public repository timing are needed before publication; affiliation must be confirmed before submission. Neutral district IDs can remain. No new names, branding work or deployment are prerequisites for kickoff.
