# Reporting corrections after the evaluation freeze

These corrections concern reporting and exhibit preparation. The scientific sources, evaluation lock, gates, treatment definitions, outcomes and analysis remain byte-identical to `prereg-frozen`. The pilot-hashed ERRATA is preserved; this separate record avoids silently rewriting that freeze.

## R-001 — 6 November 2026: concern actions in the descriptive denominator

During offline report preparation, before final evaluation tables existed, `scripts/report_results.py` was found to filter attempted actions using `record_concern`. The engine emits `submit_concern`. Valid concern submissions were therefore omitted from the all-attempts action denominator, potentially overstating the descriptive invalid-action rate. The script now imports the frozen analyzer's `TOOL_ACTIONS` set. Its invalid-action rule is unchanged.

A regression fixture has twelve valid commits, one valid concern and one wrong-phase commit. The corrected count is fourteen attempted actions, one invalid, with rate 1/14; the previous filter counted thirteen. The primary outcomes, factorial contrasts, hypothesis decisions, calibration and frozen scientific analysis are unaffected. No experimental outcome was used to choose this correction.

The idle report finisher was restarted to load the corrected reporting module; the paid collector continued untouched. The final tables will be recomputed from the curated records using the corrected script. This is a disclosed reporting correction, not an amendment to the experimental design.
