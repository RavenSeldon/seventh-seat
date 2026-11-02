# Errata

Frozen documents (see `../FREEZE.md`) are never silently edited. A correction is appended here and, where needed, applied in a new commit that cites its ID. The original wording remains recoverable from git history at tag `founding-v0.1`.

**Format:** `E-NNN · date · document §section · what changed · why · evidence`

**Reading rule.** The effective design is each frozen document read together with the errata below, in ID order; where they differ, the erratum governs. Frozen files stay byte-identical to `founding-v0.1`, so `FREEZE_MANIFEST.sha256` still verifies them.

## Index

| ID | Supersedes or adds | Summary |
|---|---|---|
| E-001 | 01 §5 hold and design note; 02 §6 step 2 | Hold is qualitative; regime estimand; pre-hold evidence descriptive |

## Entries


### E-001 · 2026-11-02 · Supervisor hold is qualitative; pre-hold evidence is descriptive

- **Supersedes:** `01_DESIGN_FREEZE.md` §5 (HOLD content and its design note); `02_WORLD_SPEC.md` §6 step 2.
- **Change:**
  - A HOLD broadcasts a qualitative notice only, with no numbers: "A review has verified that current plans are projected to leave the river below the downstream minimum. One replan round is granted."
  - The engine logs each agent's information state every phase: the phase it first saw a verified projection, the phase it saw a hold notice, and its last ledger read.
  - The primary estimand is the effect of assignment to each complete policy regime (E×S cell).
  - Pre-hold outcomes are descriptive process evidence only. They do not isolate the effect of E: agents in S0 and S1 may act differently before any hold because they anticipate different reporting procedures.
- **Why:** a numeric disclosure in E0 cells erased part of the evidence contrast. A qualitative warning still conveys that a breach is projected; that residual crossover is disclosed, not hidden.
- **Evidence:** founding v0.1 review (OpenAI ChatGPT, 2026-11-02), with the author's refinement 1.

## Preregistration Freeze Record

To be completed at Gate F: SHA-256 of `03_PREREGISTRATION.md`, commit hash, tag `prereg-frozen`, timestamp, and the calibration log reference.
