# Decisions of Record

**Append-only.** Each decision carries a one-line rationale. Superseded decisions are marked, not deleted.

## Settled (2026-11-02)

| ID | Decision | Rationale |
|---|---|---|
| D-001 | Identities: The Seventh Seat (experiment and submission), The Witness Protocol (intervention under test), The Many Hands (programme) | Keeps the weekend claim narrow while preserving the programme |
| D-002 | Repository at `~/Root/seventh-seat`; public path `https://benamuwo.me/seventh-seat/` | Mirrors First Notice's static-release pattern |
| D-003 | World: synthetic watershed, six district agents, one unrepresented downstream community, tradable over-allocated entitlements, costlier alternative supply, oracle-certified safe allocation | Gives the externality a mechanism without scripting the outcome; harm falls outside the market (unlike GovSim) |
| D-004 | E0 = public notice plus permit register; E1 = E0 plus verified live projection | E0 must not mean zero information |
| D-005 | S0 = peer-mediated escalation (k = 2 endorsements); S1 = S0 plus a direct route | S0 must not mean "no way to report" |
| D-006 | One scripted supervisor with an identical policy in every cell; one hold at most; a hold is a replan, not enforcement | Keeps E and S separable; avoids a disguised enforcement gate |
| D-007 | Primary endpoint: mean downstream shortfall; breach rate secondary | Measures the amount of unprotected harm, not just its frequency |
| D-008 | AWC and the witness ladder are descriptive only; causal claims come from randomization alone | Post-treatment conditioning risks selection bias |
| D-009 | The E×S interaction is exploratory, reported with an interval | Not powered at 60–100 episodes |
| D-010 | Blocked design: each evaluation scenario runs in all four cells; calibration scenarios are disjoint; scenario-clustered bootstrap | Comparability plus honest uncertainty |
| D-011 | Pre-sprint (declared): world, oracle, register, event log, adapter, scripted agents, observatory shell. Weekend (judged): E and S, the escalation paths, the supervisor, calibration, runs, analysis, report | Lowers execution risk within Apart's rules |
| D-012 | Identity fixed; Phantom Scorer, identity churn, adaptive attention and reviewer deliberation deferred to The Many Hands | One identifiable experiment per weekend |
| D-013 | Hosting: static release only, served by a blueprint on the existing droplet; no runtime model calls, no database | Keeps self-hosting cost flat |
| D-014 | Only VERIFIED ledger entries are cited | Apart may disqualify made-up references |
| D-015 | Te Awa Tupua appears as a respectful contextual note, never as an equivalence | It arises from a specific Indigenous legal and cultural context |
| D-016 | Founding docs frozen at tag `founding-v0.1` with a SHA-256 manifest; changes only via `docs/ERRATA.md` | What changes is the account, never the record |

## Qualms Recorded at Lock-In

| ID | Qualm | Disposition |
|---|---|---|
| Q-1 | Pre-building the world shrinks the judged contribution to the interventions, runs, analysis and report. (An earlier assistant recommendation kept the world inside the weekend.) | Accepted: allowed by the rules if declared, and the interventions and results are the scientific contribution anyway. Boundary fixed in D-011 |
| Q-2 | Conflicting reports of the resubmission rule | Submit early; re-check the live page Friday (Runbook) |
| Q-3 | Several reviewer-cited sources are unlocated or partial (PA-17 author, PA-25 venue, PA-31, PA-33 to PA-37) | Not cited unless verified (D-014) |
| Q-4 | Concern-flag and escalation tools present in every cell may prime attention to the downstream community | Constant across cells; stated as a limitation of absolute rates |
| Q-5 | A hold reveals the verified projection even in E0 cells | Part of an identical supervisory response; disclosed in the paper |
| Q-6 | Small scale; the interaction is unpowered | Estimation framing; no significance chasing |

## Open Decisions

| ID | Question | Owner | Needed by |
|---|---|---|---|
| OD-1 | Model and version, temperature, max tokens, spend ceiling | Ben | Tue 3 Nov |
| OD-2 | Solo, or recruit a teammate on the Apart Discord | Ben | Wed 4 Nov |
| OD-3 | Names for the districts and the downstream community, if any | Ben | Thu 5 Nov |
| OD-4 | Licence (code and docs) | Ben | Before going public |
| OD-5 | GitHub remote and when the repository goes public | Ben | Sun 8 Nov |
| OD-6 | Affiliation line (independent researcher unless Foundry assets apply) | Ben | Sun 8 Nov |

## Amendments to Settled Decisions

| Decision | Amended by | Note |
|---|---|---|
| D-006 | E-001 | Hold notice is qualitative; primary estimand is the policy regime |
| D-008 | E-002 | Ladder stage 4 is now "Evidence-bearing concern", structurally defined |
| D-005 | E-004 | One `submit_report` tool in all cells; routing differs (board plus 2 endorsements versus direct); S reported as two reporting regimes |
