# analysis (WEEKEND, judged)

Outcomes from truth and act fields only, witness ladder, AWC, scenario-clustered bootstrap, figures.

- `episodes.py` — every preregistered per-episode measure (03 §2) recomputed from the event record: shortfall, breach, U, unmet minimum need, alternative-supply cost, call-outcome classes, reports by route, phase latencies, validity metrics, witness ladder (01 §9 / E-002), AWC at hazard onset (01 §8).
- `contrasts.py` — E, S and E×S within-scenario contrasts; scenario-level cluster bootstrap, 10,000 resamples, percentile 95% intervals, fixed seed.
- `run.py` — `python3 -m seventh_seat.analysis.run --run RUN` (or `make analyze RUN=...`): writes `RUN/analysis/results.json` and SVG figures. Incomplete blocks are dropped from contrasts and listed (03 §7); the 25% refusal flag is applied (E-010a).
- `figures.py` — dependency-free SVG: contrasts with intervals, shortfall by cell with zero share, witness ladder (labelled descriptive).
