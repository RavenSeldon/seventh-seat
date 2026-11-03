# Runbook: 2–8 November 2026

**Status:** LIVING. All times are Vancouver local time, UTC−7: British Columbia stays on UTC−7 year-round from 1 Nov 2026 (confirmed against tzdata 2026e). UTC is given for anything hard. The sprint page's "PT" means US Pacific, now UTC−8, so add one hour for Vancouver.

## Hard Facts (from PA-01, fetched 2026-11-02)

- **Sprint:** Fri 6 Nov to Sun 8 Nov 2026.
- **Deadline:** Sun 8 Nov 23:59 AoE, which is Mon 9 Nov 11:59 UTC, or **Mon 9 Nov 04:59 Vancouver time**.
- **Internal submission target:** Sun 8 Nov 20:00 Vancouver time (Mon 9 Nov 03:00 UTC).
- **Report:** PDF on the official template; at most 8 pages excluding references and appendices; abstract of 150–250 words; author names and affiliations; a mandatory Limitations and Dual-Use / Ethical Considerations appendix.
- **Prior work:** only the weekend's work is judged. Prior work must be stated clearly, and pre-sprint code marked as pre-existing in both the README and the report. Every submission is screened for this.
- **AI tools:** allowed. The author is responsible for everything, and made-up results or references can disqualify a project.
- **Limits:** at most two projects per person.
- **Resubmission: RESOLVED BY POLICY (author, 2026-11-03).** Submit once, the final checked version, on Sunday. The rule discrepancy recorded on 2026-11-02 (assistant's direct reads: same title replaces files; a ChatGPT review: it does not) therefore no longer matters, and the help-desk question is not needed. The live page is still re-read on Friday.

## Talks (Optional)

- Thu 5 Nov 06:15 (13:15 UTC): Adaption workshop
- Thu 5 Nov 08:00 (15:00 UTC): John Kitaoka, open problems in securing systems against agent swarms
- Sat 7 Nov 06:00 (13:00 UTC): Justin Shenk, modeling agent swarms
- Sat 7 Nov 12:00 (19:00 UTC): Jurgis Kemeklis, mitigating insider threats with AI control

## Schedule

| When | Work | Boundary |
|---|---|---|
| Mon 2 Nov | Founding freeze `founding-v0.1` (this commit) | Pre-sprint, declared |
| Tue 3 Nov | World engine, scenario generator, feasibility oracle, permit register, event log. Tests G2, G3, G3b, G7 | Pre-sprint, declared |
| Wed 4 Nov | Model adapters with cache for the E-010 configurations; adapter gate GA (E-010b); harness budget enforcement G6 (E-010 item 5). Scripted agents, tool loop, containment test G1, replay G2. Observatory diorama shell per E-011 (scripted fixture only; at most 3 hours in total across Tue–Thu, only after each day's gates pass) | Pre-sprint, declared |
| Thu 5 Nov | Model qualification GM (E-010) and model choice. Final novelty pass G0. End-to-end scripted dry run. Finalize `PREEXISTING_WORK.md`. Tag `pre-sprint-2026-11-05` | Pre-sprint, declared |
| Fri 6 Nov | Implement E (verified ledger), S (direct route), the S0 endorsement path, and the supervisor. Gates G4, G5, G8, G9. Calibration pilot, then the Evaluation lock (E-009; G10, G11). Launch evaluation runs | **Weekend (judged)** |
| Sat 7 Nov | Finish runs by 23:00 Vancouver time (Sun 8 Nov 06:00 UTC; fixed stop). Trade-disabled and mechanical-gate arms if budget allows. Analysis, ladder, figures | **Weekend (judged)** |
| Sun 8 Nov | Report, appendix, README and reproducibility commands. Submit by 20:00. Exhibit build | **Weekend (judged)** |

## Gates (Acceptance Conditions)

| Gate | Condition | When |
|---|---|---|
| G0 | Final novelty pass appended to the ledger; the contribution sentence revised if needed | Thu |
| G1 Containment | Agents cannot reach files, network, shell or any action outside the world API | Wed |
| G2 Replay | A cached episode replays to an identical state-hash sequence | Tue/Wed |
| G3 Feasibility | The oracle certifies every generated scenario; infeasible ones are rejected and logged | Tue |
| G-OBS Exhibit | E-011 tests: 2D and 3D agree, accounting balances, missing events error, scripted label visible, no-WebGL fallback renders | Before any exhibit release |
| GA Adapter | E-010(b): reasoning-state continuity tests (sequential and parallel calls, continuation, truncation, error recovery) pass for each configuration | Wed |
| GM Model | Qualification per E-008 as revised by E-010, on a no-hazard world; lowest measured cost per evaluable episode chosen | Thu |
| G3b Trade-off | Every scenario passes E-005: a safe allocation exists; the no-trade reference stays within the cap; the trade reference breaches; reference trades are strictly attractive to both sides; safety has a positive local price | Tue |
| G4 Identity | `actor_id` never changes; display names cannot alter permissions or history | Fri |
| G5 Evidence integrity | Only engine-produced records carry VERIFIED; agent text never does | Fri |
| G6 Attention | No agent exceeds `B` actions in a phase; overruns are rejected and logged | Wed |
| G7 Permits | The entitlement and trade checker agrees with hand-verified edge cases | Tue |
| G8 Escalation | Reports are attributable; supervisor decisions are logged; the policy is byte-identical across cells | Fri |
| G9 Analytics | Every primary and secondary outcome is computed from truth and act fields only | Fri |
| G10 Prompt freeze | Prompt templates hashed and recorded before the first evaluation run | Fri |
| G11 Calibration | The calibration rule was applied and every step logged; pilot data is excluded | Fri |
| Evaluation lock | E-009 record: protocol commit, prompt and tool hashes, model configuration, calibrated parameters, calibration exclusion, seeds and strata, planned comparisons, stopping time (tag `prereg-frozen`) | Fri |

## Submission Checklist (Sun)

- [ ] Official template; at most 8 pages before references and appendices
- [ ] Title; abstract of 150–250 words; author and affiliation (independent researcher unless decided otherwise)
- [ ] Limitations and Dual-Use / Ethical Considerations appendix (draft in `07_ETHICS_AND_DUAL_USE.md`)
- [ ] Prior work declared in the README and the report (`PREEXISTING_WORK.md`)
- [ ] Every citation marked VERIFIED in `04_PRIOR_ART_LEDGER.md`
- [ ] Every number recomputable by a documented command
- [ ] Tracks selected (Track 2 primary; Tracks 3 and 4 secondary)
- [ ] Code link works (public repository at submission is the author's decision, OD-5)
- [ ] Links in the PDF work
- [ ] Submitted by 20:00 Vancouver time; confirmation email received

## Human Actions (Ben)

1. By Wed: API keys for Anthropic and OpenAI (Google optional), a spend limit set in each provider console, and the account rate limits noted (E-010). The slate itself is fixed.
2. Claim Adaption credits at adaptionlabs.ai/app with the sprint email (optional; they are for training and datasets, not required here).
3. OD-2 resolved: solo (D-018).
4. Friday: re-check the resubmission rule on the live page.
5. Commits, pushes, the GitHub remote, deployment and submission.
