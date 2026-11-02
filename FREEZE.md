# Freeze Record

**Tag:** `founding-v0.1` · **Date:** 2026-11-02 · **Manifest:** `FREEZE_MANIFEST.sha256`

## Frozen (Change Only via `docs/ERRATA.md`)

- `docs/00_CHARTER.md`
- `docs/01_DESIGN_FREEZE.md`
- `docs/02_WORLD_SPEC.md` (values marked [calibrated] may change once, by the preregistered rule, and the change is logged)
- `docs/06_EXHIBIT_SPEC.md` (data rules frozen; visual details may evolve)

Verify with: `sha256sum -c FREEZE_MANIFEST.sha256`

## Living (Edited in Place, History in Git)

- `docs/03_PREREGISTRATION.md`: draft until Gate F, then frozen and recorded in `ERRATA.md`
- `docs/04_PRIOR_ART_LEDGER.md`, `docs/05_RUNBOOK.md`, `docs/07_ETHICS_AND_DUAL_USE.md`
- `docs/DECISIONS.md`, `docs/ERRATA.md`, `docs/AI_ASSISTANCE_LOG.md` (append-only)
- `README.md`, `DEPLOY.md`, `PREEXISTING_WORK.md`, `PROJECT-LOG.md`

## Amendment Procedure

1. Append an erratum (`E-NNN`) stating what changes, why, and on what evidence.
2. Apply the change in a commit whose message cites the erratum ID.
3. Regenerate the manifest and record the new hash beside the erratum.

Earlier wording stays recoverable at the tag. What changes is the account, never the record.
