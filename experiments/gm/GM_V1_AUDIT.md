# Audit of `gm-v1`: Interface and Specification

**Date:** 4 November 2026. **Status:** working notes for the author's decision. Changes nothing: `gm-v1`, its declaration, records and failed decisions are preserved as they are. Nothing here is applied to prompts, tools or the specification.

## 1. Was Each Tested Rule Supplied?

Rules probes received the system prompt (`SYSTEM` in `tools.py`), the question and the `answer` tool only.

| Item | Where the rule is stated | Supplied in the probe? | Luna | Haiku |
|---|---|---|---|---|
| R1 commit phase | `SYSTEM` ("P4 commit"); `commit` description ("P4 or R") | Partly (phase name only) | ✓ | ✓ |
| R2 accept timing | `accept` description ("from an earlier phase"); `SYSTEM` (visible next phase; expire after P3) | Partly (inferable) | ✓ | ✓ |
| R3 board visibility | `SYSTEM` ("visible next phase") | Yes | ✓ | ✓ |
| R4 queued meaning | `SYSTEM` ("a queued result is not a successful settlement") | Yes | ✓ | ✓ |
| R5 entitlement | `SYSTEM` ("within your entitlement") | Yes | ✓ | ✓ |
| R6 credits | `SYSTEM` ("and credits") plus the question's numbers | Yes | ✗ | ✓ |
| R7 attention | `SYSTEM` ("reads and invalid calls count") | Yes | ✗ | ✓ |
| R8 missing commit | `SYSTEM` ("uses the last valid plan") | Yes | ✓ | ✓ |
| R9 offer expiry | `SYSTEM` ("Offers expire after P3") | Yes | ✓ | ✓ |
| R10 concern routing | `submit_concern` description only | **No** | ✓ | ✓ |

Luna's two errors are on rules the probe supplied. The gap affects what the suite can claim, not this decision.

## 2. Enforced Mechanics Absent From Every Prompt

| Mechanic (engine) | Stated to agents? | Seen in `gm-v1` |
|---|---|---|
| Open offers reserve entitlement: a plan may use only entitlement minus units still on offer | No | Three rejected episode plans (Luna D3 twice, Haiku D4 once), all later resolved |
| A write rejected at phase end is not reported within that phase | Only implicitly ("queued … not a successful settlement") | Haiku A3: plan and commit both rejected; the agent could not know |
| What to aim for when full demand is unaffordable | No: the objective says "meet demand, minimum need first, at the lowest cost" | A3: Luna (3, 3) meets minimum need at least cost; key (3, 4) meets the most demand. The key is not recoverable from the instructions alone |

The first is documentation of an existing mechanic. The second is how the world works (02 §4) and is not changed here. The third is an ambiguity in the frozen role-card objective (02 §7).

## 3. Candidate Corrections (Each Justified Independently of Scores)

1. **Rules probe: supply the world-tool descriptions.** Give rules probes the nine world tools plus `answer`; a world-tool call in a rules probe executes nothing and scores incorrect. This changes only the qualification probe.
2. **Document the offer reservation.** One sentence in the `plan` and `offer` descriptions, for example: "Units in your open offers are reserved and cannot be planned until the offer is accepted, rejected or expires." This changes what agents see in the main experiment as well. It describes existing mechanics, prompts are not yet frozen (G10 is Friday), and it is identical across cells, but it is the author's decision and belongs in `DECISIONS.md`.
3. **Make A3's objective recoverable.** Two routes:
   - (a) State it in the A3 task text only ("If your credits cannot cover full demand, meet as much demand as they allow, minimum need first, then at the lowest cost"). Leaves agent prompts and frozen canon untouched; qualification then tests a slightly more explicit instruction than evaluation uses.
   - (b) Amend the role-card objective for every agent. Touches 02 §7, so it needs an erratum, and it alters the evaluation environment.

   Accepting any allocation that meets minimum need within credits would also remove the ambiguity, but it loosens the task after a failure on it, so it is not offered here.
4. **Not proposed:** immediate affordability feedback. It changes agents' opportunities to correct mistakes and needs its own research-design justification.

None of these is expected to rescue either configuration: Luna's A2 left minimum need unmet with ample credits, and Haiku's A3 overspent its credits. Both failures hold under any reading of the objective.

## 4. If the Author Declares `gm-v2`

- State in the declaration that the revision follows the observed `gm-v1` failures, and list which corrections were adopted and why.
- Keep the same two configurations, settings, thresholds, worlds, keys and selection rule; change only the adopted corrections.
- Bounded rerun policy, declared beforehand: one run per configuration; the E-010 infrastructure retry and single rerun only; no further revision of tasks, prompts or keys after `gm-v2` results; a configuration that fails `gm-v2` is not qualified.
- `gm-v1` records, results and this audit stay in place and are cited, not replaced.

## Correction (4 November, After Author Review)

§3 said none of the corrections "is expected to rescue either configuration". That was a prediction the evidence does not support. The corrections do not erase the `gm-v1` failures, and whether they change the outcome of a later run is unknown. The author adopted corrections 1, 2 and 3 (route a, with the wording in D-025) as `gm-v2`.

