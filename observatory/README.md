# observatory

Static exhibit source: The Seven Seats, The Ladder, The Witness Record, Two Rivers. Spec: `docs/06_EXHIBIT_SPEC.md`. Budget: `DEPLOY.md`.

- `research/`: four-exhibit interface and release browser checks. Built from `scripts/export_observatory.py` output; see its README. Experimental rendering is reviewed only after completed collection.
- `diorama/`: pre-sprint shell of The Seven Seats as a 3D diorama (E-011), scripted fixtures only. See `diorama/README.md`.

The source page is served as is during development; `make release` builds the deployable copy in `dist/seventh-seat/` with three.js vendored, and `make release-check` runs the browser checks against it offline.
