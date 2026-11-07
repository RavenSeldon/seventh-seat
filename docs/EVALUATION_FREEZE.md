# Evaluation freeze record

Recorded on 6 November 2026 in Vancouver, at 2026-11-07T02:37:07.006985+00:00. Evaluation had not started when this record was prepared.

The effective preregistration is frozen by the `prereg-frozen` tag on the commit containing this record, the lock and passing gate evidence. Its earlier DRAFT heading is historical; this record establishes the effective status without rewriting the hashed document.

- Scientific source checkpoint: `f949dac1c6b17d6dba884e71f8302d12bf3cf651`.
- Preregistration SHA-256: `62b9367cf90145aa496ac5eab3f88ec88b97715df4d6b04f682b9f91a85d37c8`.
- Design-amendments SHA-256: `1ee987f59eaa7f2a42df54ff7084ac4eeaff088997f131e9575369bac5489b9c`.
- Lock SHA-256 (canonical JSON without trailing newline): `62270e5ede50da114dee38f411521ea7813c1f44ca37d3cf3467758f9d9dc6e2`.
- Calibration result SHA-256: `97899fd8fca59d7c4ded0a69ac328263577dbed9800c7de54ad6301056defe2f`; retained trace: `experiments/pilot-calibration-summary.json`; private source records: `runs/pilot-2026-11-06/`.
- Calibration: all eight fixed episodes evaluable; four breaches at kappa 14; accepted on the first batch, no adjustment. No pilot data enters evaluation contrasts.
- Configuration: GPT-6 Luna, medium reasoning effort, no temperature, maximum 4096 output tokens. Original gm-v2 selection is retained.
- Sample: 24 scenarios, seeds 2000–2023, 12 cheap and 12 costly; all four cells per scenario. Cell order and strata are in `experiments/evaluation-lock.json`. Seeds 1000–1099 are excluded.
- Estimators: frozen E and S contrasts, exploratory interaction; 10000 scenario bootstrap resamples, seed `13851877781056479794`. Both primary directional intervals are reported without multiplicity adjustment.
- Fixed stop: 8 November 06:00 UTC, Saturday 7 November 23:00 Vancouver. New blocks require 3735.726 seconds of timing reserve; in-flight episodes may finish.
- Caps: USD33 OpenAI, USD33 Anthropic, USD66 overall, USD20 preparation, including imported historical charges. No top-ups or model substitution.

## Administrative record placement

The draft requested writing freeze metadata into `docs/ERRATA.md`. That file is already included in the immutable pre-pilot declaration. To preserve that evidence, this administrative record and the tagged JSON lock carry the freeze metadata instead. This is a disclosed record-location deviation, not a change to hypotheses, calibration, model, outcomes, seeds or stopping rules. The source checkpoint precedes the metadata commit to avoid a self-referential Git hash; the tag identifies the complete metadata commit.

## Authority and review

The author authorized continuation within the provider caps, local commits and reviewed checkpoint pushes to RavenSeldon/seventh-seat. The continuation uses that authorization to freeze the settled design and run the accepted evaluation. No Thursday boundary tag is created. Existing prior-work disclosure remains accurate.

The gate record binds all 32 declared source/protocol files and names its evidence. All 158 offline tests pass. One live pilot episode replayed byte-for-byte without paid calls; all 160 planned seed/parameter scenarios passed the oracle. The inherited AWC proxy limitation remains disclosed. Future documentation checkpoints may descend from this tag, but bound scientific bytes, lock and gate evidence must remain unchanged for resumption. The tag will not be moved.

This is authorization to collect under the settled protocol, not evidence of intervention effectiveness or a completed submission. Publication, final manuscript review and the author's submission receipt remain outstanding.
