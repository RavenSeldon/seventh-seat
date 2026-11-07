# Reading edition and site polish — 7 November 2026

The reading edition preserves `report/final/manuscript.json` verbatim, including every paragraph, caption and table value. It adds a house-style web reader and nine-page dark PDF inspired by the author's Schrödinger's Civilization audit. The original submission-format PDF and immutable `research-2026-11-07` release remain unchanged. This is a presentation release, not another experiment or a submission.

The hub builds on Claude's `d03d5f9` copy and cyan/lavender/gold palette. Additions are publication navigation, links to the author's wider work, an integrity-gated headline finding, improved table spacing and keyboard-operable witness disclosures. Exact events, provenance links and scientific qualifications remain available. Neither primary hypothesis met its preregistered support rule.

## Rebuild

The HTML builder uses the Python standard library. PDF output additionally requires ReportLab and the DejaVu Serif/Sans TrueType fonts:

```sh
python scripts/build_reading_edition.py \
  --manuscript report/final/manuscript.json \
  --html observatory/research/paper/index.html \
  --pdf /tmp/seventh-seat-reading.pdf --fonts /path/to/dejavu/fonts
python scripts/build_research_release.py \
  --data runs/report-output-2026-11-06/exhibit-data \
  --output /tmp/seventh-seat-reading-site
node observatory/research/check_research.mjs \
  --release /tmp/seventh-seat-reading-site --experimental
```

The web reader links to the original research release and the separately versioned `reading-2026-11-07` PDF. It makes no third-party requests while reading. The PDF's creation timestamp is build metadata; the manuscript content is the unchanged released source.

## Verification

- 230 actual-experiment browser checks passed: data values, intervals, integrity failures, source text, desktop/mobile navigation, keyboard disclosure and locally scrolling tables.
- All 117 manuscript text items matched in the generated HTML and extracted PDF; all nine rendered PDF pages were visually inspected.
- All 32 evaluation-lock scientific source hashes matched. Every exhibit data file and 3D/vendored asset matches the original public research release. Only hub HTML/JS changed; `paper/index.html` was added.
- The offline Python suite passed; optional Flask-only tests were skipped in the research environment because Flask is not installed. No blog application code changed in this polish.
- No model-provider calls, new charges or new experimental observations.

## Deployment

Use the separately supplied `deploy/install_reading.sh` after the presentation archive is published. It verifies a pinned archive digest and every file receipt before switching the existing static release atomically. It leaves the blog checkout and all services alone, retains previous releases, and restores the previous symlink if the publication health checks fail. The existing blog blueprint already serves the new `paper/` HTML route.

Deployment must be reported separately from local/release verification. The Mac's existing `neurascape` SSH connection rejected authentication during this work; a prepared public archive is not evidence that the server has installed it.
