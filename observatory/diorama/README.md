# The Seven Seats: Diorama Shell

PRE-SPRINT shell (declared in `PREEXISTING_WORK.md`), built under design rules E-011 ("The Witnessed World") and E-013 (shared-commons topology). It is the three-dimensional rendering of exhibit 1 of 4, not a fifth exhibit.

## What It Is

One static page, `index.html`, in two parts:

- **The theatre (full width).** On load it shows a pre-rendered frame of the current snapshot, with a sparse HUD: downstream flow against the minimum, and the shortfall. If no frame was rendered for this exact snapshot, it shows the flat plan instead. No WebGL is started until the viewer chooses **Enter the diorama**. The live scene then offers:
  - **Cinematic:** a perspective view you can orbit. It has decorative glow and water motion, and its widths are not a reading.
  - **Calibrated plan:** fixed, top-down, orthographic. The glow is off, and widths can be compared.
  - **Guided reveal:** four steps (the assembly, the water, the seventh seat, the record). It is labelled as a staging of one recorded final state, not a replay of events.
  - **Full screen**, where the browser allows it.
- **The instrument (below).** The calibrated flat plan, the panel of numbers ("The reading"), and the legend of measured marks and scenery. It stays usable without WebGL or the CDN.

**Topology (E-013).** All six districts draw from one shared commons at once, and one outlet carries the remainder to the seventh seat. Seat positions are arbitrary and symmetric. An earlier version drew a river passing the districts in sequence, an order the model does not contain.

**Rendering.** Frames are drawn only when something changes: camera movement, a reveal step, or the water motion in the cinematic view. An idle calibrated plan renders nothing, and the scene pauses when the page is hidden. Reduced-motion settings stop the water motion and turn camera moves into cuts. Pixel density and shadows are reduced on low-power devices.

The page draws only from the snapshots embedded in its `<script id="snapshots">` block. Those snapshots are generated from engine episodes; no value is entered by hand.

## Data

- **Contract:** `seventh-seat/snapshot/v1`, defined and validated in `src/seventh_seat/observatory/snapshot.py`. The page repeats the same validation in JavaScript.
- **Validation refuses:**
  - unbalanced accounting;
  - a missing district (missing is never read as zero);
  - an unknown data status;
  - an empty event record.
- **Current data:** two scripted fixtures from scenario `S1000-k14-cheap`, played through the engine by the scripted agents in `agents/scripted.py`:
  - No-trade reference: 70 drawn, 30 of 30 delivered.
  - Reference trades: 84 drawn, 16 of 30 delivered.

  Both carry `data_status: scripted-fixture` and the page shows a persistent label. They are not experimental results.

To regenerate the fixtures and the page's embedded block, from the repository root:

```bash
PYTHONPATH=src python3 -m seventh_seat.observatory.snapshot      # snapshots; drops frames that no longer match
node observatory/diorama/render_posters.mjs                     # re-render the pre-rendered frames
```

**Pre-rendered frames.** Each frame is filed under the SHA-256 of its snapshot's canonical JSON, and the page shows a frame only when that hash matches the snapshot on screen. A frame therefore never appears over data it was not made from. A test checks that every filed frame belongs to an embedded snapshot. A layout change does not alter the hash, so re-render the frames after changing the scene.

**Experimental data.** A snapshot marked `experimental` is refused unless it carries `provenance.manifest_sha256`, the export manifest that verified it against the run's event log. Balanced arithmetic alone does not prove a snapshot came from a real run (E-013).

## Gate G-OBS

| Half | Command | Checks |
|---|---|---|
| Contract (stdlib) | `python3 -m unittest discover -s tests -t .` (`tests/test_snapshot.py`, 12 tests) | Fixtures reproduce the reference worlds; invalid snapshots are refused, including experimental ones without a manifest; the page embeds exactly the engine's fixtures; every pre-rendered frame matches an embedded snapshot |
| Browser (Node + Playwright) | `node observatory/diorama/check_gobs.mjs [--three-dir node_modules/three] [--shots out/]` (68 checks) | Scripted label visible; no WebGL before it is requested; each frame shown only for its own snapshot; HUD, panel, flat plan and 3D meshes agree with the snapshot (widths measured from the drawn SVG and mesh geometry); no sequential river course; glow is decorative and off in the calibrated plan; the idle plan renders nothing; the reveal states the recorded numbers and is labelled "not a replay"; the camera reaches the seventh seat even when steps are clicked quickly; no horizontal scroll at phone width; the WebGL fallback works |

`--three-dir` serves three.js from a local copy, for offline runs. Both halves passed on 2026-11-03.

## Measured Size (2026-11-03, before release)

| File | Raw | Gzip |
|---|---|---|
| `index.html` (with fixtures and two pre-rendered frames) | 194.1 KB | 107.8 KB |
| three.js 0.160.0 `three.module.min.js` (loaded on request) | 670.7 KB | 166.2 KB |
| `OrbitControls.js` | 29.9 KB | 6.5 KB |
| `CSS2DRenderer.js` | 4.4 KB | 1.5 KB |
| `RoomEnvironment.js` | 3.7 KB | 1.2 KB |

- **First load:** about 108 KB, plus web fonts. The two embedded JPEG frames are most of it.
- **Opening the diorama:** adds about 175 KB.

Both are within the `DEPLOY.md` budget (1.5 MB first load, 15 MB release). three.js currently loads from jsDelivr (pinned to 0.160.0). Self-hosting it is a release-time decision. Re-measure before any release.

## Not Yet Built (Weekend or Later)

- Connecting the page to one validated experimental episode, with its export manifest. This happens only after the analysis gates pass.
- Event-by-event replay of trades, concerns and holds. This needs validated per-event states; the current reveal stages only a final state.
- The Ladder, The Witness Record and Two Rivers exhibits.
