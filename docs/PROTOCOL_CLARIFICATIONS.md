# Calibration clarification record

Prepared 5 November 2026, before pilot or evaluation. **ADOPTED by the author on 5 November:** “Use the recommended rule.” Recorded as D-028 and E-014 and applied to draft preregistration §6. This document retains the proposal and its rationale; it is not an evaluation lock. The same response confirmed that the participant survey and Discord access are complete.

## Why a decision is necessary

The current draft allows 6–8 scenarios, lists two steps in either direction from κ=14, but permits three adjustments. It does not specify endpoint handling, revisiting a setting, pilot allocation across cost strata, or the case where no setting enters the target band while breach rates remain above it. Settling these before observing pilot outcomes removes avoidable discretion.

## Adopted rule

1. Use eight fixed E0S0 pilot scenario seeds, 1000–1007, four cheap and four costly under `assign_strata`. Record the exact mapping before calls. Reuse these seeds and strata for every tested κ; the generator may change demands and entitlements with κ, so these are not identical worlds across settings.
2. Start at κ=14. The ordered permitted levels are 8, 10, 14, 18, 22. The target is 30%–85%, inclusive; compare the unrounded fraction of eight completed pilot episodes (3–6 breaches qualifies).
3. Below 30%, move up one adjacent level; above 85%, move down one. Accept the first tested setting in range.
4. Count an adjustment as a change of κ after a completed pilot batch. Allow at most three adjustments after the initial batch, hence at most four batches (32 pilot episodes before infrastructure reruns). Stop earlier if the next level is outside the allowed set or has already been tested. Do not resample to improve the breach rate.
5. Use E-010 recovery: up to three provider attempts per request and one complete episode rerun with the same scenario/cell/seed. If a batch still lacks an evaluable episode, stop calibration as incomplete; repair infrastructure before deciding how to proceed. Never change the denominator or replace a scenario silently.
6. If the procedure ends outside the target band, retain the last tested setting and report the factorial descriptively, without confirmatory intervention claims. Distinguish low-baseline failure from a persistent high baseline or an exhausted search. Only low baseline is the founding global falsifier; a high baseline is a separate calibration failure, not evidence of no harm.
7. Keep all pilot records, attempted settings, outcomes, costs and stop reasons. Exclude all calibration seeds (1000–1099) from evaluation, including failed or superseded attempts. Evaluation seeds remain in 2000–2099.

## What is already determined

- E-010 already specifies the retry/rerun behavior. The draft preregistration §7 can be aligned without creating a new research decision.
- E-004 already makes S0 consent-gated and S1 direct. It is not a pure removal of consent with identical peer-action costs.
- E-001 already makes HOLD qualitative and the estimand the complete policy regime.
- E-012 already retires avoidable-harm/utility-gap endpoints. Alternative-supply cost remains an outcome; the substitution price is a scenario constant.

## Disposition

D-028 records the author's selection; E-014 makes the pilot-volume and descriptive-fallback interpretation explicit alongside the frozen design. Draft preregistration §6 now includes the operational procedure. Record the exact seed/stratum mapping and configuration before calls. No pilot was run as part of this preparation.
