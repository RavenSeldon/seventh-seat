# Four-exhibit research observatory

A static interface for the Seven Seats, Ladder, Witness Record and Two Rivers. It accepts only a local source-bound exhibit export; it has no backend, provider credentials or model calls. The 3D view retains the existing diorama, with the first complete scenario's four final snapshots substituted and stale scripted posters removed.

Every effect shows its interval and scenario count. Ladder counts are descriptive over all evaluable episodes; means and contrasts use complete blocks. No-hazard records are labelled separately. Witness detail follows locked scenario order, then displays one district's observations, quoted claims and actions against evaluator-visible phase-end projections. Matched reruns are never described as counterfactuals. Every missing cell remains visible, and every mark is mapped in the shipped source table.

## Local build after collection

From the repository root:

```bash
.venv/bin/python scripts/export_observatory.py --run runs/report-output-2026-11-06/curated-records --output runs/report-output-2026-11-06/exhibit-data
.venv/bin/python scripts/build_research_release.py --data runs/report-output-2026-11-06/exhibit-data --output runs/report-output-2026-11-06/exhibit-review
node observatory/research/check_research.mjs --release runs/report-output-2026-11-06/exhibit-review --experimental
```

The unattended finisher's `--exhibits` option performs the first two steps after verified collection. Destinations must be new; resumption verifies completed file receipts rather than overwriting them. A partial build without its receipt stops for review. The finisher does not run the browser review, publish the exhibit or declare the manuscript final.

Serve a built directory with a local HTTP server to preview it; opening index.html as a file cannot fetch the verified JSON. `RELEASE.json` gives the CSP to use when hosting. Both the hub and nested diorama share that policy. The browser validator serves the release locally with its exact CSP and refuses all third-party requests. `--experimental` is required for actual records; omit it only for the labelled representative regression fixture. Tests cover data agreement, source mismatch rejection, quoted HTML escaping, missingness, lazy loading, keyboard access and phone layout.

## Size and publication

The builder enforces 15 MB for the whole release (including its own manifest) and 1.5 MB for initial HTML, JS and first-view data. Witness JSON and the vendored 3D library load only when requested. A synthetic rehearsal is about 0.86 MB total and 0.09 MB on entry; actual experimental sizes and browser rendering still require review. The release is not automatically deployed. Raw full logs, caches and budget databases are not part of it; witness detail contains only filtered observations/world events for the preselected scenario.
