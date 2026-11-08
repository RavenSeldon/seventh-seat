"""Serve a separately deployed static release; never import the blog or its models.

Follows the First Notice blueprint, with the serving rules in seventh-seat's DEPLOY.md:
an explicit MIME allowlist (anything else is 404), revalidated HTML and data, year-long
caching only for the version-pinned vendor tree, and the release's own
Content-Security-Policy, read from its RELEASE.json at request time.

The blog's app-level after_request hook sets a site-wide CSP. For the release's policy to
survive, that hook must not overwrite a CSP a route has already set (one-line change in
app/__init__.py, applied by seventh-seat's deploy/blog/apply_to_blog.py).
"""
import json
import os
from pathlib import Path

from flask import Response, redirect, request, send_from_directory, url_for

# Release roots, in resolution order:
#   1. SEVENTH_SEAT_ROOT                       -- explicit override (use this in production)
#   2. <project root>/seventh_seat_release     -- a local copy beside the app, for preview
#   3. PRODUCTION_ROOT                         -- the deployed release symlink from DEPLOY.md
# views.py lives at <project root>/app/routes/seventh_seat/views.py.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOCAL_ROOT = PROJECT_ROOT / "seventh_seat_release"
PRODUCTION_ROOT = Path("/srv/seventh-seat/current/seventh-seat")

# Exactly the types DEPLOY.md permits. Anything else is refused with 404.
MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript",
    ".json": "application/json",
    ".webp": "image/webp",
    ".png": "image/png",
    ".ico": "image/vnd.microsoft.icon",
    ".css": "text/css",
    ".webmanifest": "application/manifest+json",
    ".m4a": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".svg": "image/svg+xml",
    ".txt": "text/plain; charset=utf-8",
}
IMMUTABLE = "public, max-age=31536000, immutable"


def _release_root():
    """Resolve the release root once per request, so a release switch is atomic."""
    override = os.environ.get("SEVENTH_SEAT_ROOT")
    if override:
        return Path(override).resolve()
    if LOCAL_ROOT.is_dir():
        return LOCAL_ROOT.resolve()
    return PRODUCTION_ROOT.resolve()


def _release_csp(root):
    try:
        value = json.loads((root / "RELEASE.json").read_text(encoding="utf-8"))["content_security_policy"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return value if isinstance(value, str) and value and "\n" not in value else None


def _cache_control(relative):
    parts = relative.split("/")
    # Version-pinned vendored library: the version is in the path, so it never changes.
    if "vendor" in parts:
        i = parts.index("vendor")
        if i + 1 < len(parts) and parts[i + 1].startswith("three-"):
            return IMMUTABLE
    # index.html, RELEASE.json and unversioned data/*.json must revalidate.
    return "no-cache"


def _headers(response, cache="no-cache"):
    response.headers["Cache-Control"] = cache
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


def _missing():
    return _headers(Response("Not found.\n", status=404, mimetype="text/plain"))


def publication(asset_path=""):
    root = _release_root()
    if not root.is_dir():
        return _headers(Response("Release files are not installed.\n", status=503,
                                 mimetype="text/plain"))
    candidate = (root / asset_path).resolve()
    if not candidate.is_relative_to(root):
        return _missing()
    if candidate.is_dir():
        if not request.path.endswith("/"):
            target = (url_for("seventh_seat.seventhseat_file", asset_path=asset_path + "/")
                      if asset_path else url_for("seventh_seat.seventhseat_index"))
            if request.query_string:
                target += "?" + request.query_string.decode("latin-1")
            return redirect(target, code=308)
        candidate = (candidate / "index.html").resolve()
        if not candidate.is_relative_to(root):
            return _missing()
    mimetype = MIME_TYPES.get(candidate.suffix.lower())
    if mimetype is None or not candidate.is_file():
        return _missing()
    relative = str(candidate.relative_to(root))
    response = send_from_directory(str(root), relative, mimetype=mimetype, conditional=True)
    if candidate.suffix.lower() == ".html":
        csp = _release_csp(root)
        if csp is None:
            # A release without its verified policy is not served.
            return _headers(Response("Release policy missing.\n", status=503,
                                     mimetype="text/plain"))
        response.headers["Content-Security-Policy"] = csp
    return _headers(response, _cache_control(relative))
