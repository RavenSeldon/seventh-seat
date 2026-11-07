#!/usr/bin/env python3
"""Install the Seventh Seat blueprint into the Neurascape blog checkout. Never commits.

    python3 deploy/blog/apply_to_blog.py --blog ~/Root/beamu-blog            # dry run: show the diff
    python3 deploy/blog/apply_to_blog.py --blog ~/Root/beamu-blog --write    # apply to the working tree

Three edits, each idempotent and anchored on text that must already exist (else it stops):
  1. copy deploy/blog/seventh_seat/ to WebDev/Blog/app/routes/seventh_seat/
  2. app/routes/__init__.py: import and register seventh_seat_bp last (after First Notice)
  3. app/routes/main.py: add /seventh-seat/ to the sitemap after /first-notice/
  4. app/__init__.py: the site-wide CSP no longer overwrites a CSP a route already set
     (only this blueprint sets one, so every other page is unchanged)
The author reviews `git diff`, commits, pushes and reloads the droplet.
"""
import argparse
import difflib
import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "seventh_seat"
FILES = ("__init__.py", "url.py", "views.py")

EDITS = [
    ("app/routes/__init__.py",
     "    from app.routes.first_notice.url import first_notice_bp\n",
     "    from app.routes.first_notice.url import first_notice_bp\n"
     "    from app.routes.seventh_seat.url import seventh_seat_bp\n"),
    ("app/routes/__init__.py",
     "    app.register_blueprint(first_notice_bp)\n",
     "    app.register_blueprint(first_notice_bp)\n"
     "    # Static research exhibit at /seventh-seat/ -- same pattern, same reason.\n"
     "    app.register_blueprint(seventh_seat_bp)\n"),
    ("app/routes/main.py",
     "        {'loc': '/first-notice/', 'priority': '0.7', 'changefreq': 'weekly'},\n",
     "        {'loc': '/first-notice/', 'priority': '0.7', 'changefreq': 'weekly'},\n"
     "        # Static research exhibit served by the seventh_seat blueprint.\n"
     "        {'loc': '/seventh-seat/', 'priority': '0.7', 'changefreq': 'monthly'},\n"),
    ("app/__init__.py",
     "        response.headers['Content-Security-Policy'] = csp\n",
     "        # A route that sets its own verified policy (the /seventh-seat/ release) keeps it.\n"
     "        response.headers.setdefault('Content-Security-Policy', csp)\n"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blog", required=True, help="beamu-blog checkout")
    ap.add_argument("--write", action="store_true", help="apply (default: dry run)")
    a = ap.parse_args()
    repo = Path(a.blog).expanduser().resolve()
    app = repo / "WebDev/Blog"
    if not (app / "app/routes/first_notice/url.py").is_file():
        sys.exit(f"not the blog checkout (no First Notice blueprint): {repo}")
    if a.write:
        dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                               capture_output=True, text=True, check=True).stdout.strip()
        if dirty:
            sys.exit("blog working tree has uncommitted changes; commit or stash them first")

    new_texts, changed = {}, False
    for rel, anchor, replacement in EDITS:
        path = app / rel
        text = new_texts.get(rel, path.read_text(encoding="utf-8"))
        if replacement in text:
            new_texts[rel] = text
            continue
        if text.count(anchor) != 1:
            sys.exit(f"{rel}: expected anchor exactly once, found {text.count(anchor)}; stopping")
        new_texts[rel] = text.replace(anchor, replacement)
    for rel, text in new_texts.items():
        old = (app / rel).read_text(encoding="utf-8")
        if old != text:
            changed = True
            sys.stdout.writelines(difflib.unified_diff(
                old.splitlines(True), text.splitlines(True), f"a/WebDev/Blog/{rel}", f"b/WebDev/Blog/{rel}"))

    dest = app / "app/routes/seventh_seat"
    copies = [f for f in FILES if not (dest / f).is_file() or not filecmp.cmp(SRC / f, dest / f, shallow=False)]
    for f in copies:
        changed = True
        print(f"{'new' if not (dest / f).exists() else 'update'}: WebDev/Blog/app/routes/seventh_seat/{f}")

    if not changed:
        print("blog already carries the Seventh Seat blueprint; nothing to do")
        return
    if not a.write:
        print("\ndry run only; re-run with --write to apply to the working tree")
        return
    dest.mkdir(exist_ok=True)
    for f in copies:
        shutil.copyfile(SRC / f, dest / f)
    for rel, text in new_texts.items():
        (app / rel).write_text(text, encoding="utf-8")
    print("\napplied. Review with: git -C", repo, "diff && git -C", repo, "status")


if __name__ == "__main__":
    main()
