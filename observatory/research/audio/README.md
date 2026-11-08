# Optional soundtrack

These eight M4A recordings are reused unchanged from the author's Rushii project at the author's explicit request. Player mechanics build on Rushii / SchroCiv Tale. No music was generated or purchased. See `experiments/experience-asset-provenance.json` for exact byte counts and hashes; see `LICENSING.md` for the separate artwork/audio rights boundary.

## Drop in a track

1. Put audio here with an ordered, ASCII filename: `07-my-track.m4a`. Supported extensions: `.mp3`, `.m4a`, `.aac`, `.ogg`. Use letters, numbers, dots, underscores or hyphens; no spaces. Choose codecs supported by your target browsers (AAC in M4A and MP3 are the existing baseline).
2. Run the ordinary `scripts/build_research_release.py` command in `docs/READING_EDITION.md`. The builder automatically sorts filenames and writes `audio/playlist.json`. Do not edit the generated playlist by hand.
3. Run `observatory/research/check_research.mjs --release NEW_DIRECTORY --experimental`, review the release receipt and publish a new version. The complete presentation must stay below 20 MiB. Old releases remain immutable.

Music starts only after pressing the star button. Settings provide volume and next track. The playlist repeats after a three-second pause. The embedded diorama shares the parent player, so music continues during exploration. A full page navigation remembers the track, position and volume for the current tab session, but requires another play gesture. Audio is optional atmosphere, never evidence or a simulation event. An empty audio folder removes the player; failed audio does not prevent reading or using the diorama.
