# Pre-existing Work (Declared to Apart)

Only work done during the sprint (Fri 6 to Sun 8 Nov 2026) is judged. Everything below predates it and is declared here and in the report.

## Conceptual and Methodological Lineage

| Work | Date | What is reused |
|---|---|---|
| Schrödinger's Civilization (Apart AI Incident Response Sprint) | Sept 2026 | The idea of separating record, observation and claim, generalized here into four descriptions of every event. No code is reused unless listed below. That repository is frozen and is not modified |
| First Notice (Mangrove Middle Powers Hackathon) | Oct 2026 | The static-release hosting pattern (blueprint plus atomic symlink release) and the evidence-first presentation discipline |

## Pre-Sprint Artifacts in This Repository

| Artifact | Created | Tag |
|---|---|---|
| Founding documents (`docs/00`–`07`, `DECISIONS.md`, `AI_ASSISTANCE_LOG.md`, `ERRATA.md`, `README.md`, `DEPLOY.md`, `PROJECT-LOG.md`, `FREEZE.md`) | 2026-11-02 | `founding-v0.1` |
| Pre-sprint code (world engine, scenario generator, feasibility oracle, permit register, event log, model adapter, scripted agents, observatory shell including the 3D diorama shell per E-011, scripted fixture only) | 3–4 Nov, implemented | `pre-sprint-2026-11-05` (pending) |
| Qualification gm-v1/gm-v2, correction C-1, scripted rehearsal and reproducibility instructions | 4 Nov | `pre-sprint-2026-11-05` (pending) |
| Citation verification and close-prior-art search; calibration clarification D-028/E-014; report outline and candidate bibliography; handoff, status updates and file inventory | 5 Nov | `pre-sprint-2026-11-05` (pending) |

A review inventory is supplied in `experiments/pre_sprint_inventory_2026-11-05.json`: all tracked files at base commit `63a55ad`, their founding-to-base change status and hashes, plus this preparation pass's additions/changes. It excludes its own bytes to avoid a self-referential digest and excludes ignored private caches, scratch records, credentials and build dependencies. Those excluded records still predate the sprint and are not claimed as weekend work.

**The final tag does not yet exist.** After review/commit, create `pre-sprint-2026-11-05` at the complete boundary, then use `git diff --stat founding-v0.1 pre-sprint-2026-11-05` and `git ls-tree -r --name-only pre-sprint-2026-11-05` for the authoritative committed list. A timestamped inventory is evidence of a snapshot, not a substitute for that tag. The inventory reports pending paths separately and must be regenerated if further pre-sprint files change.

Diorama v3 (2026-11-03: visual and accessibility polish, motion controls, WebP posters, browser regression checks) is Ben Amuwo's pre-sprint work, with OpenAI Codex assisting; see `observatory/diorama/REVIEW.md`. The release build, deploy template and expanded browser checks of the same day are also pre-sprint.

## Weekend Contribution (Judged)

Planned sprint-period work after the declared pre-sprint boundary: the E and S interventions, escalation paths, supervisor, hazard-world evaluation runner, calibration execution, evaluation lock, evaluation runs, analysis, figures, completed report and experimental exhibit data. Thursday's calibration procedure, report outline and bibliography are pre-existing preparation; only the actual weekend additions are claimed as sprint work. Neither a later commit nor a tag changes when an artifact was created.

## Third-Party Software

| Software | Licence | Use |
|---|---|---|
| three.js 0.160.0 | MIT | 3D scene; vendored into the release with its licence |
| Playwright 1.63.0 | Apache-2.0 | Development only: browser checks and poster rendering; not deployed |
| OpenAI Python SDK 3.42.1 | Apache-2.0 | Optional local provider adapter; not deployed in the static exhibit |
| Anthropic Python SDK 2.4.0 | Apache-2.0 | Optional local provider adapter; not deployed in the static exhibit |

On 3 November, Ben Amuwo directed implementation of the Wednesday provider harness with OpenAI Codex assistance: tool schemas, adapters, private histories, response cache, persistent budget accounting, recovery, 27 additional offline tests and two live no-hazard smoke episodes with exact cached replay. This is pre-sprint engineering, not qualification or experimental evidence. SDK licences were checked in installed package metadata.

On 4 November, Gate GM model qualification (E-010) was specified, implemented and run with Anthropic Claude assistance: `experiments/gm/` (specification, declaration, results, report), `src/seventh_seat/agents/qualification.py`, `scripts/run_qualification.py`, `tests/test_qualification.py`, and small harness changes listed in the report. `gm-v1`: neither configuration qualified. `gm-v2` (D-025, after the `gm-v1` audit): both qualified and GPT-6 Luna was selected; it added a world-tool reference to rules questions, two sentences on reserved entitlement to the `offer` and `plan` descriptions, and an explicit objective to allocation probes. This is pre-sprint engineering on no-hazard worlds, not experimental evidence. The same day: replay-scoring correction C-1, and an end-to-end scripted dry run (`src/seventh_seat/rehearsal.py`, `scripts/dry_run.py`, `docs/REPRODUCE.md`), offline with scripted fixtures only.

On 5 November, OpenAI Codex assisted with the literature and submission-template review, report outline and candidate bibliography, preparation checklist, disclosure inventory and status corrections. The author selected the calibration clarification before any pilot (D-028/E-014); the draft preregistration's infrastructure handling was aligned with existing E-010. The existing scripted rehearsal was rerun offline and passed all 18 checks. No provider call, pilot, evaluation or experimental finding was produced. Actual historical human/assistant effort hours were not established by this review and are not estimated here; earlier visual-work declarations remain part of the record.
