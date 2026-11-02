# Deploying The Seventh Seat → https://benamuwo.me/seventh-seat/

**Status:** PLAN. Nothing is deployed, and the blog repository has not been touched. Executed by the author once the exhibit exists.

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
| Releases kept on droplet | Last 3 (pruned by the author) | Disk |

Self-hosting cost is the droplet's existing fixed price. A static release adds cost only if monthly transfer exceeds the plan's included allowance, which the guardrails keep far away. Check the droplet's plan once at release time.

## Once: Blog Side (Author's Action, When the Exhibit Exists)

Copy the First Notice blueprint pattern (`beamu-blog/WebDev/Blog/app/routes/first_notice/`):

1. Create `app/routes/seventh_seat/` with `url.py` and `views.py`. Use prefix `/seventh-seat`, endpoint names prefixed `seventhseat_` (avoiding the short-alias collision documented in First Notice's `url.py`), override environment variable `SEVENTH_SEAT_ROOT`, local root `seventh_seat_release`, and production root `/srv/seventh-seat/current/seventh-seat`. Keep the explicit MIME table and `nosniff`.
2. Register the blueprint last in `app/routes/__init__.py`.
3. Add `/seventh-seat/` to the sitemap in `app/routes/main.py`.
4. Commit, push, pull on the droplet, and reload the blog service (same commands as First Notice's `DEPLOY.md`).

Until files are installed, `/seventh-seat/` returns 503. That is expected.

## Every Release (App Side)

A `scripts/deploy.sh` adapted from First Notice's: build, size check against the guardrails, upload to staging, atomic symlink swap, then curl checks for `/seventh-seat/`, `/`, `/schrodingers_civ/` and `/first-notice/`. Written during exhibit work, not before.

## Rollback

Identical to First Notice: point `current` at a previous release with an atomic `ln -sfn` and `mv -T`.
