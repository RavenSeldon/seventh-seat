# The Seventh Seat

*Who protects the party that isn't at the table?*

An experiment for the Apart Research Swarm Alignment Sprint (6–8 Nov 2026). Six LLM agents share a river. A seventh party, the downstream community, has no seat in their market. We test whether verified evidence (E) and an independent route to review (S) help the collective protect it, what that costs, and where the opportunity to protect it is lost.

**Status:** founding freeze `founding-v0.1` (2026-11-02). Founding design preserved with errata through E-013. **World engine, provider harness, scripted fixtures and the 3D observatory shell are implemented. Both provider smoke runs replay exactly; formal qualification and experimental runs remain ahead.**

## Read in This Order

1. [Charter](docs/00_CHARTER.md): the question, principles, scope, roles
2. [Design freeze](docs/01_DESIGN_FREEZE.md): what is tested and how it can fail
3. [World specification](docs/02_WORLD_SPEC.md): the watershed mechanics and event record
4. [Preregistration (draft)](docs/03_PREREGISTRATION.md): estimands, calibration rule; freezes Friday
5. [Prior-art ledger](docs/04_PRIOR_ART_LEDGER.md): what is already known; what may be cited
6. [Runbook](docs/05_RUNBOOK.md): schedule, gates, submission checklist
7. [Exhibit specification](docs/06_EXHIBIT_SPEC.md) and [ethics and dual-use draft](docs/07_ETHICS_AND_DUAL_USE.md)
8. [Decisions](docs/DECISIONS.md), [errata](docs/ERRATA.md), [AI assistance log](docs/AI_ASSISTANCE_LOG.md)

## Quick Start

```bash
make test             # unit tests (Python 3.10+, standard library only)
make frozen           # frozen founding docs still match FREEZE_MANIFEST.sha256
make diorama-setup    # once, optional: Node 18+, Playwright, Chromium and three.js for the browser checks
make dry-run          # end-to-end scripted dry run, offline, no provider calls
make check            # tests, frozen docs, G-OBS on the page and on the release build
open observatory/diorama/index.html   # the diorama shell (scripted fixtures, not results)
```

The [Wednesday harness guide](docs/WEDNESDAY_HARNESS.md) documents bounded live checks and offline replay. Live calls use optional dependencies (`.venv/bin/python -m pip install -e '.[providers]'`); offline tests remain standard-library only.

`make help` lists every target. Reproducing records (dry run, Gate GM): [docs/REPRODUCE.md](docs/REPRODUCE.md). Deploying is in [DEPLOY.md](DEPLOY.md).

**Frozen documents are read together with [the errata](docs/ERRATA.md).** E-001 to E-013 amend the founding design; where they differ, the erratum governs.

## Layout

```text
docs/                    founding documents (see FREEZE.md for which are frozen)
src/seventh_seat/
  world/                 PRE-SPRINT (declared): engine, scenarios, oracle, register, event log
  agents/                PRE-SPRINT (declared): model adapter, cache, scripted agents
  interventions/         WEEKEND (judged): verified ledger (E), direct route (S), S0 endorsements, supervisor
  analysis/              WEEKEND (judged): outcomes, ladder, AWC, bootstrap, figures
tests/                   acceptance gates G1–G9
experiments/             run configurations and calibration logs
observatory/             static exhibit source (built to dist/ by make release, deployed per DEPLOY.md)
scripts/                 build_release.py (static release + guardrails), deploy.sh (template)
report/                  the Apart report
```

## Principles

Reality before myth. What changes is the account, never the record. Behaviour, not minds. Nulls are results.

## Prior Work

Declared in [PREEXISTING_WORK.md](PREEXISTING_WORK.md). Only work after tag `pre-sprint-2026-11-05` is the judged sprint contribution.

## Hosting

Static release at `https://benamuwo.me/seventh-seat/`, served like Schrödinger's Civilization and First Notice. See [DEPLOY.md](DEPLOY.md).

## Licence

To be decided (OD-4).
