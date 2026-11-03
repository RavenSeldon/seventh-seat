# Diorama review and polish · 2026-11-03

**Author:** Ben Amuwo. **Assistance:** OpenAI Codex. Against the working repository at `b421716`, the charter, frozen exhibit specification and E-011/E-013. This is a visualizer and implementation review, not an independent replication or full methodological audit.

## Assessment

The strongest part of the exhibit is the separation between an inviting scene and an inspectable instrument. The shared commons avoids inventing an upstream order between districts. Its single outlet makes the absent party legible. Keep that structure, the identical district seats, restrained brass, dark field and measured blue/coral distinction.

The references inspected were [Neurascape](https://benamuwo.me/) and [Schrödinger’s Civilization](https://benamuwo.me/schrodingers_civ/). Their celestial setting, fine circular motifs, editorial hierarchy and explicit separation of record from storytelling support a restrained polish. A lavender title accent is decoration; it introduces no new scientific encoding. No religious or philosophical symbol has been inserted as if it were an experimental variable.

## Findings corrected

- **Document setup:** the page lacked a doctype, language, UTF-8 declaration and standard mobile viewport. Served over HTTP, punctuation appeared as mojibake. These are now explicit; the default body margin is removed.
- **Narrative consistency:** selecting a new fixture during a reveal updated the data but could retain old captions. Selection now ends the old reveal; restarting narrates the current snapshot.
- **Disclosure in full screen:** the persistent status band was outside the full-screen element. An in-theatre status now retains the fixture disclaimer. “Read the numbers” exits full screen and focuses the instrument heading.
- **Navigation and accessibility:** skip/section links, larger touch targets, focus handoffs, announced fixture outcomes, a repaired SVG accessible name, and expandable source JSON make the record easier to reach and inspect.
- **Camera and motion:** Reset view returns to the overview and ends any reveal. Pause motion settles transitions and stops decorative water. Reduced motion takes priority. Offscreen scenes stop rendering. Phone framing gives the scene, captions and controls separate space; labels cannot paint over the interface.
- **Zero-flow handling:** a valid zero-inflow snapshot no longer produces a division-by-zero bar width; the bar scale is the greater of inflow and the downstream minimum and is labelled accordingly.
- **Hosting rules:** posters are now WebP, tied to the same canonical snapshot hashes; system fonts replace three externally requested font families. This brings those choices into line with `DEPLOY.md`.
- **Living documentation:** README status and the project resume point now acknowledge the implemented core and shell. Historical log entries remain recognizable; the new entry records their later committed state.

## Scientific boundaries preserved

Frozen document hashes, engine code, generated fixture JSON and the page’s embedded snapshot block remain unchanged. Channel geometry still derives from the same values and fixed scale. Coral continues to encode an actual shortfall. Cinematic perspective remains explicitly non-calibrated. The reveal remains labelled as staging a recorded final state, not an event replay. No experimental run, result, effect estimate or claim about agents’ mental states was added.

The current manifest check is structural: it requires a 64-character hexadecimal reference. It does not retrieve the manifest or authenticate the source log. The UI and README now describe that limit without calling a supplied reference verified evidence. The exporter and manifest-to-log verification remain a publication gate, as already anticipated in E-013.

## Validation

- `python3 -m unittest discover -s tests -t .`: **43 tests pass**.
- `node observatory/diorama/check_gobs.mjs`: **86 browser checks pass**, covering both fixtures, actual SVG and mesh widths, disclosure, fallback, camera/reveal behaviour, paused/offscreen rendering, reduced motion, full screen, source inspection and phone layout.
- `shasum -a 256 -c FREEZE_MANIFEST.sha256`: all four frozen documents match.
- Direct comparison with the reviewed repository confirms embedded snapshots and the fixture file are unchanged.
- Visual inspection of desktop, phone, plan, cinematic and reveal screenshots. Browser suite uses Chromium with software WebGL and system fonts; this is not a cross-browser/device certification.
- Posters regenerated with `node observatory/diorama/render_posters.mjs` after the camera/layout change. Snapshot hashes remain the same; imagery was regenerated, not reused over different data.

## Remaining publication gates

The work remains a pre-sprint shell. Before publishing experimental results: implement the exporter, verify each manifest against source logs, pass the analysis gates, measure the complete release, and make the release-time dependency-hosting decision. The other three exhibits and event-by-event replay remain future work. The author retains commit, push, deployment and submission authority.
