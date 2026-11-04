#!/usr/bin/env python3
"""Check provider model metadata, never generate text or run an experiment.

Run with the repository's .venv Python. --setup privately collects credentials
into the ignored .env.local file; --local-only checks loading without networking.
Only the two API-key assignments are read; this file is never executed as shell.
"""
from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path
import shlex
import sys

KEYS = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")


def read_keys(path: Path) -> dict[str, str]:
    values = {}
    if not path.exists():
        return values
    for number, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        name, sep, value = line.partition("=")
        if name.strip() not in KEYS:
            continue
        try:
            parts = shlex.split(value, comments=True)
        except ValueError:
            raise ValueError(f"Malformed quoting in .env.local on line {number}.") from None
        if not sep or len(parts) > 1:
            raise ValueError(f"Invalid key assignment in .env.local on line {number}.")
        values[name.strip()] = parts[0] if parts else ""
    return values


def configure(path: Path) -> None:
    # Do not replace an existing nonempty credential file.
    if path.is_symlink() or (path.exists() and path.read_text().strip()):
        raise ValueError(".env.local is already populated. Run without --setup, or edit that file locally.")
    if not sys.stdin.isatty():
        raise ValueError("Run --setup in your own interactive Terminal so key entry stays hidden.")
    values = {}
    for name in KEYS:
        value = getpass.getpass(f"Paste {name} (hidden), then press Return: ").strip()
        if not value.startswith("sk-") or any(c.isspace() for c in value):
            raise ValueError(f"{name}: expected a complete API key starting with sk-, without quotes or spaces. Nothing saved.")
        values[name] = value
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w") as stream:
        os.fchmod(stream.fileno(), 0o600)
        for name, value in values.items():
            stream.write(f"{name}={shlex.quote(value)}\n")
    print("Saved both keys to .env.local with owner-only permissions. Keys are never printed.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup", action="store_true", help="privately enter keys into an empty/missing .env.local")
    parser.add_argument("--local-only", action="store_true", help="verify credential loading without API requests")
    args = parser.parse_args(argv)
    path = Path(__file__).resolve().parents[1] / ".env.local"
    try:
        if args.setup:
            configure(path)
        saved = read_keys(path)
    except (OSError, UnicodeError, ValueError) as exc:
        # Parser errors contain line numbers, not the line or credential value.
        print(f"Setup: {exc}")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nSetup cancelled. No keys saved.")
        return 1

    failed = False
    checks = (
        ("OpenAI", "OPENAI_API_KEY", "gpt-6-luna"),
        ("Anthropic", "ANTHROPIC_API_KEY", "claude-haiku-5-5"),
    )
    for provider, variable, model in checks:
        # An explicit project file takes priority over an unrelated shell key.
        key = saved.get(variable) or os.environ.get(variable, "").strip()
        if not key:
            print(f"{provider}: MISSING {variable}. Run this script with --setup.")
            failed = True
            continue
        if args.local_only:
            print(f"{provider}: credential loaded (value hidden); no API request made.")
            continue
        try:
            if provider == "OpenAI":
                from openai import OpenAI
                client = OpenAI(api_key=key, base_url="https://api.openai.com/v1", max_retries=0, timeout=20)
            else:
                from anthropic import Anthropic
                client = Anthropic(api_key=key, base_url="https://api.anthropic.com", max_retries=0, timeout=20)
            with client:
                result = client.models.retrieve(model)
            print(f"{provider}: OK — {result.id}")
        except Exception as exc:
            status = getattr(exc, "status_code", "unavailable")
            print(f"{provider}: FAILED — {type(exc).__name__}, status={status}. No credential values shown.")
            failed = True
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
