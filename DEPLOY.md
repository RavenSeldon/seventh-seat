# Deploying The Seventh Seat → https://benamuwo.me/seventh-seat/

**Status:** PLAN. Nothing is deployed, and the blog repository has not been touched. The release build (`make release`) and a deploy template (`scripts/deploy.sh`) exist; neither has been run against the server.

The same pattern as Schrödinger's Civilization and First Notice: static files on the droplet at `/srv/seventh-seat/current/seventh-seat/`, served by a small blueprint in the Neurascape Flask blog. Everything is built on the Mac; the droplet only receives files.

## Cost Guardrails (Binding)

| Rule | Limit | Why |
|---|---|---|
| Runtime compute | None: no model calls, no database, no server-side rendering | Flat hosting cost; nothing to secure |
| Whole release | 15 MB or less | Disk and transfer stay negligible |
| First load | 1.5 MB or less (HTML, CSS, JS and first-view data) | Fast on phones; small transfer per visit |
| Exhibit data | Precomputed, decimated JSON, lazy-loaded per exhibit | Full logs are not needed to view |
| Raw run logs | Not hosted on the droplet; published with the code (GitHub release), with SHA-256 hashes referenced from the exhibit | Keeps the droplet lean while staying verifiable |
| Media | SVG and WebP only; no audio or video | Largest avoidable cost |
| Fonts | System stack or one subset `woff2` | Size |
| Third-party requests | None at runtime: three.js is vendored into the release, pinned to the version the source page names | No dependency on a CDN staying up; no visitor data leaves the site |
| Runtime dependencies | Only static files and the blog's existing blueprint | Nothing to patch on the server |
| Releases kept on droplet | Last 3 (pruned by the author) | Disk |

Self-hosting cost is the droplet's existing fixed price. A static release adds cost only if monthly transfer exceeds the plan's included allowance, which the guardrails keep far away. Check the droplet's plan once at release time.

## Once: Blog Side (Author's Action, When the Exhibit Exists)

Copy the First Notice blueprint pattern (`beamu-blog/WebDev/Blog/app/routes/first_notice/`):

1. Create `app/routes/seventh_seat/` with `url.py` and `views.py`. Use prefix `/seventh-seat`, endpoint names prefixed `seventhseat_` (avoiding the short-alias collision documented in First Notice's `url.py`), override environment variable `SEVENTH_SEAT_ROOT`, local root `seventh_seat_release`, and production root `/srv/seventh-seat/current/seventh-seat`. Keep the explicit MIME table and `nosniff`.
2. Register the blueprint last in `app/routes/__init__.py`.
3. Add `/seventh-seat/` to the sitemap in `app/routes/main.py`.
4. Commit, push, pull on the droplet, and reload the blog service (same commands as First Notice's `DEPLOY.md`).

Until files are installed, `/seventh-seat/` returns 503. That is expected.

Serving rules for the blueprint (all standard Flask `send_from_directory` behaviour plus headers):

- **MIME types:** `.html` text/html; charset=utf-8, `.js` text/javascript, `.json` application/json, `.webp` image/webp, `.svg` image/svg+xml, `.txt` text/plain; charset=utf-8. Anything else: 404. Keep `X-Content-Type-Options: nosniff`.
- **Caching:** `index.html` and `RELEASE.json`: `Cache-Control: no-cache` (revalidate, so a new release shows at once). Everything under `vendor/three-<version>/` and `fixtures/`: `Cache-Control: public, max-age=31536000, immutable` (the version is in the path).
- **Compression:** let nginx gzip `text/html`, `text/javascript` and `application/json` (`gzip on; gzip_types text/javascript application/json;`; HTML is on by default). WebP is already compressed.
- **Content-Security-Policy:** copy the `content_security_policy` string from the release's `RELEASE.json` onto `index.html` responses. It allows only this site's own scripts, plus hashes for the page's two inline scripts, so it changes when the page's code changes; read it from the file at request time, or redeploy the blueprint with each release. `make release-check` serves the page with this exact policy and fails on any violation.

## Every Release (App Side)

```bash
make check                                    # unit tests, frozen docs, G-OBS on the page and on the release
git commit …                                  # deploy only committed work
make release                                  # dist/seventh-seat/ + RELEASE.json (commit, hashes, sizes, CSP)
SEVENTH_SEAT_HOST=user@droplet scripts/deploy.sh --dry-run
SEVENTH_SEAT_HOST=user@droplet scripts/deploy.sh
```

`scripts/build_release.py` copies the page, the four three.js files it uses (with the MIT licence) and the fixtures into `dist/seventh-seat/`, rewrites the importmap to the vendored files, and refuses to build if the release is over 15 MB, the first load is over 1.5 MB, a file type is outside the list above, or a third-party script or stylesheet remains.

`scripts/deploy.sh` (a template, not yet run) refuses a dirty tree or a release built from another commit, uploads to `releases/<UTC stamp>-<commit>/`, switches `current` atomically, keeps the newest three releases, then checks `/seventh-seat/`, `/seventh-seat/RELEASE.json`, `/`, `/schrodingers_civ/` and `/first-notice/`, and that the live `RELEASE.json` names this commit. Compare it with First Notice's script before the first run.

## Rollback

Identical to First Notice: point `current` at a previous release with an atomic `ln -sfn` and `mv -T`.

## Keeping It Cheap and Low-Maintenance

- The site is static files behind the blog that already runs. There is no process, database, key or queue to keep alive, so the marginal cost is disk and transfer on the existing droplet.
- Nothing is fetched from third parties at runtime, so there is nothing external to go down or to change version under the page.
- Releases are directories, so rollback is one symlink, and `RELEASE.json` says what is live.
- The heavy part (three.js, about 176 KB gzip) loads only when a visitor asks for the 3D scene, and is cached for a year once fetched.
- Upkeep is a yearly glance: renew nothing, update nothing. Upgrading three.js is optional and means changing one version in the page and `package.json`, then `make check`.

## Measured Release · 2026-11-03 (shell, scripted fixtures; not a publication)

| | Raw | Gzip |
|---|---|---|
| First load (`index.html`: page, fixtures, two WebP poster frames) | 186,867 B | 105,154 B |
| On entering the 3D scene (vendored three.js, four files) | | 175,952 B |
| Whole release (8 files) | 898,420 B | |

No font, model or backend requests. Before publication: rebuild from the final commit, and verify manifest-to-log provenance for any experimental snapshot.

## Four-exhibit candidate (7 November; not deployed)

`scripts/build_research_release.py --data EXHIBIT_DATA --output NEW_DIRECTORY` builds the research hub plus a nested `seven/` diorama, using verified exports rather than the old shell fixtures. See `observatory/research/README.md`. It preserves the same 15 MB whole-release and 1.5 MB first-load caps, counts the release manifest itself, and vendors the pinned Three.js files. Use the candidate's single CSP for both HTML pages. Experimental JSON under `data/` must be revalidated on release changes (do not apply the old immutable `fixtures/` caching rule to unversioned data). Before any deployment, inspect actual records in the release, run its browser checks with `--experimental`, review the concrete payload and obtain the author's publication/deployment decision. The earlier shell deployment commands do not automatically select this new candidate.
