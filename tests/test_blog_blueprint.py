"""The /seventh-seat/ blog blueprint serves a reviewed release with its own CSP (needs Flask).

Reproduces the two blog behaviours that matter: the app-level after_request hook that sets a
site-wide CSP (as patched by deploy/blog/apply_to_blog.py, i.e. setdefault), and create_app()'s
short-name endpoint alias loop, which must not let this blueprint capture url_for('index').
Skipped where Flask is not installed, so the stdlib suite is unaffected.
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HAS_FLASK = importlib.util.find_spec("flask") is not None
SITE_CSP = "default-src 'self'; script-src 'self' 'unsafe-inline'"
RELEASE_CSP = "default-src 'none'; script-src 'self'; img-src 'self' data: blob:"


def load_blueprint():
    """Load deploy/blog/seventh_seat under a unique name: it must not shadow src/seventh_seat."""
    import importlib
    name = "seventh_seat_blog_blueprint"
    if name not in sys.modules:
        pkg = ROOT / "deploy" / "blog" / "seventh_seat"
        spec = importlib.util.spec_from_file_location(
            name, pkg / "__init__.py", submodule_search_locations=[str(pkg)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return importlib.import_module(name + ".url").seventh_seat_bp


def make_release(base):
    r = base / "release"
    for rel, body in {
        "index.html": "<!doctype html><title>hub</title>",
        "app.js": "export {};",
        "data/summary.json": "{}",
        "seven/index.html": "<!doctype html><title>seven</title>",
        "seven/vendor/three-0.160.0/build/three.module.min.js": "export {};",
        "seven/vendor/three-0.160.0/LICENSE.txt": "MIT",
        "notes.py": "print('never served')",
    }.items():
        p = r / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    (r / "RELEASE.json").write_text(json.dumps({"content_security_policy": RELEASE_CSP}))
    (base / "secret.json").write_text("{}")
    return r


@unittest.skipUnless(HAS_FLASK, "Flask not installed (blog-side check only)")
class BlogBlueprint(unittest.TestCase):
    def setUp(self):
        from flask import Flask, url_for
        self.tmp = tempfile.TemporaryDirectory()
        self.release = make_release(Path(self.tmp.name))
        os.environ["SEVENTH_SEAT_ROOT"] = str(self.release)
        seventh_seat_bp = load_blueprint()
        app = Flask(__name__)

        @app.route("/")
        def index():
            return "blog home"

        app.register_blueprint(seventh_seat_bp)
        # create_app()'s alias loop, verbatim in effect
        for rule in list(app.url_map.iter_rules()):
            ep = rule.endpoint
            if "." in ep and ep != "static":
                short = ep.split(".", 1)[1]
                if short not in app.view_functions:
                    app.view_functions[short] = app.view_functions[ep]
                    app.url_map._rules_by_endpoint.setdefault(short, []).extend(
                        app.url_map._rules_by_endpoint.get(ep, []))

        @app.after_request
        def site_headers(response):  # the blog hook after apply_to_blog.py
            response.headers.setdefault("Content-Security-Policy", SITE_CSP)
            response.headers["X-Content-Type-Options"] = "nosniff"
            return response

        self.app, self.url_for = app, url_for
        self.c = app.test_client()

    def tearDown(self):
        os.environ.pop("SEVENTH_SEAT_ROOT", None)
        self.tmp.cleanup()

    def test_hub_and_diorama_carry_release_csp(self):
        for path in ("/seventh-seat/", "/seventh-seat/seven/"):
            r = self.c.get(path)
            self.assertEqual(r.status_code, 200, path)
            self.assertTrue(r.mimetype == "text/html", path)
            self.assertEqual(r.headers["Content-Security-Policy"], RELEASE_CSP, path)
            self.assertEqual(r.headers["Cache-Control"], "no-cache")
            self.assertEqual(r.headers["X-Content-Type-Options"], "nosniff")

    def test_blog_pages_keep_site_csp(self):
        r = self.c.get("/")
        self.assertEqual(r.headers["Content-Security-Policy"], SITE_CSP)

    def test_slashless_redirects(self):
        self.assertEqual(self.c.get("/seventh-seat").status_code, 308)
        r = self.c.get("/seventh-seat/seven")
        self.assertEqual(r.status_code, 308)
        self.assertTrue(r.headers["Location"].endswith("/seventh-seat/seven/"))

    def test_types_and_caching(self):
        js = self.c.get("/seventh-seat/app.js")
        self.assertEqual((js.status_code, js.mimetype, js.headers["Cache-Control"]), (200, "text/javascript", "no-cache"))
        data = self.c.get("/seventh-seat/data/summary.json")
        self.assertEqual((data.mimetype, data.headers["Cache-Control"]), ("application/json", "no-cache"))
        self.assertEqual(self.c.get("/seventh-seat/RELEASE.json").headers["Cache-Control"], "no-cache")
        v = self.c.get("/seventh-seat/seven/vendor/three-0.160.0/build/three.module.min.js")
        self.assertEqual(v.headers["Cache-Control"], "public, max-age=31536000, immutable")
        self.assertNotIn("Content-Security-Policy", {k: v for k, v in data.headers.items() if v == RELEASE_CSP})

    def test_icons_audio_and_range_requests(self):
        for name,mime in {"seal.png":"image/png","favicon.ico":"image/vnd.microsoft.icon","site.webmanifest":"application/manifest+json","experience.css":"text/css","track.m4a":"audio/mp4","track.mp3":"audio/mpeg","track.aac":"audio/aac","track.ogg":"audio/ogg"}.items():
            (self.release/name).write_bytes(b"0123456789")
            response=self.c.get("/seventh-seat/"+name)
            self.assertEqual((response.status_code,response.mimetype),(200,mime))
            self.assertEqual(response.headers["X-Content-Type-Options"],"nosniff")
        response=self.c.get("/seventh-seat/track.m4a",headers={"Range":"bytes=2-5"})
        self.assertEqual((response.status_code,response.data),(206,b"2345"))
        self.assertEqual(response.headers["Content-Range"],"bytes 2-5/10")

    def test_refuses_unlisted_types_and_escapes(self):
        for path in ("/seventh-seat/notes.py", "/seventh-seat/../secret.json",
                     "/seventh-seat/%2e%2e/secret.json", "/seventh-seat/missing.json"):
            self.assertEqual(self.c.get(path).status_code, 404, path)

    def test_missing_policy_or_release_is_not_served(self):
        (self.release / "RELEASE.json").unlink()
        self.assertEqual(self.c.get("/seventh-seat/").status_code, 503)
        os.environ["SEVENTH_SEAT_ROOT"] = str(self.release / "absent")
        self.assertEqual(self.c.get("/seventh-seat/").status_code, 503)

    def test_blog_index_alias_not_captured(self):
        with self.app.test_request_context():
            self.assertEqual(self.url_for("index"), "/")


if __name__ == "__main__":
    unittest.main()
