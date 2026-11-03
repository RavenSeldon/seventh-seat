"""Snapshot contract for the diorama (E-011 item 5) and the scripted fixtures.

A snapshot is the only thing an exhibit may draw from. Every quantity it holds
is copied from an engine episode; nothing is entered by hand.

Contract `seventh-seat/snapshot/v1`, required fields (E-011):
    episode_id, tick, total_inflow, withdrawals_by_actor, downstream_flow,
    minimum_required_flow, event_refs, data_status
plus `actors` (the expected actor set, so a missing actor is an error and is
never read as zero) and optional `scenario_id`, `label`, `description`,
`provenance`.

Run `python3 -m seventh_seat.observatory.snapshot` from the repository root to
regenerate the scripted fixtures and embed them in observatory/diorama/index.html.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

CONTRACT = "seventh-seat/snapshot/v1"
DATA_STATUSES = ("scripted-fixture", "experimental")
REQUIRED = ("episode_id", "tick", "total_inflow", "withdrawals_by_actor", "downstream_flow",
            "minimum_required_flow", "event_refs", "data_status", "actors")


class SnapshotError(ValueError):
    """A snapshot that must not be drawn."""


def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def validate(snap: dict) -> dict:
    """Raise SnapshotError unless the snapshot satisfies the contract.

    Rules: required fields present; known data status; every expected actor has
    an explicit withdrawal (a missing actor is an error, never a zero); no
    unexpected actors; non-negative integer quantities; accounting balances
    (total_inflow - sum(withdrawals) = downstream_flow); event_refs non-empty.
    """
    if not isinstance(snap, dict):
        raise SnapshotError("snapshot must be an object")
    missing = [k for k in REQUIRED if k not in snap]
    if missing:
        raise SnapshotError(f"missing required fields: {', '.join(missing)}")
    if snap.get("contract", CONTRACT) != CONTRACT:
        raise SnapshotError(f"unknown contract {snap.get('contract')!r}")
    if snap["data_status"] not in DATA_STATUSES:
        raise SnapshotError(f"data_status must be one of {DATA_STATUSES}, got {snap['data_status']!r}")
    if snap["data_status"] == "experimental":
        # E-013: arithmetic consistency is not authenticity. This checks only that a reference is
        # present and well-formed; the exporter verifies the manifest against the run's event log.
        manifest = (snap.get("provenance") or {}).get("manifest_sha256", "")
        if not (isinstance(manifest, str) and re.fullmatch(r"[0-9a-f]{64}", manifest)):
            raise SnapshotError("an experimental snapshot needs an export-manifest reference "
                                "(provenance.manifest_sha256); the exporter must verify it "
                                "against the run's event log")
    actors = snap["actors"]
    if not isinstance(actors, list) or not actors or len(set(actors)) != len(actors):
        raise SnapshotError("actors must be a non-empty list of unique ids")
    w = snap["withdrawals_by_actor"]
    if not isinstance(w, dict):
        raise SnapshotError("withdrawals_by_actor must be an object")
    absent = [a for a in actors if a not in w]
    if absent:
        raise SnapshotError(f"no recorded withdrawal for {', '.join(absent)} (missing is not zero)")
    extra = [a for a in w if a not in actors]
    if extra:
        raise SnapshotError(f"withdrawal for unexpected actor(s): {', '.join(extra)}")
    for key in ("total_inflow", "downstream_flow", "minimum_required_flow", "tick"):
        if not _is_int(snap[key]) or snap[key] < 0:
            raise SnapshotError(f"{key} must be a non-negative integer")
    for a, v in w.items():
        if not _is_int(v) or v < 0:
            raise SnapshotError(f"withdrawal for {a} must be a non-negative integer")
    if snap["minimum_required_flow"] <= 0:
        raise SnapshotError("minimum_required_flow must be positive")
    total = sum(w.values())
    if snap["total_inflow"] - total != snap["downstream_flow"]:
        raise SnapshotError(f"accounting does not balance: {snap['total_inflow']} - {total} "
                            f"!= {snap['downstream_flow']}")
    refs = snap["event_refs"]
    if not isinstance(refs, list) or not refs or not all(isinstance(r, str) and r for r in refs):
        raise SnapshotError("event_refs must be a non-empty list of event ids")
    return snap


def from_engine(engine, data_status: str, label: str = "", description: str = "") -> dict:
    """Build a snapshot from an executed engine episode."""
    if not engine.state["executed"] or engine.outcome is None:
        raise SnapshotError("episode has not been executed")
    executed = [r for r in engine.log.records if r["action"] == "season_executed"]
    if len(executed) != 1:
        raise SnapshotError("expected exactly one season_executed event")
    ev = executed[0]
    trades = [r["event_id"] for r in engine.log.records
              if r["action"] == "accept" and r["authorized"]]
    out = engine.outcome
    snap = {
        "contract": CONTRACT,
        "episode_id": engine.episode_id,
        "scenario_id": engine.sc.scenario_id,
        "tick": ev["step"],
        "actors": list(engine.ids),
        "total_inflow": engine.sc.F,
        "withdrawals_by_actor": {k: int(v) for k, v in out["withdrawals"].items()},
        "downstream_flow": int(out["downstream_flow"]),
        "minimum_required_flow": engine.sc.M,
        "event_refs": [ev["event_id"], *trades],
        "data_status": data_status,
        "label": label,
        "description": description,
        "provenance": {"log_head": engine.log.head, "season_event_hash": ev["hash"],
                       "condition": engine.condition},
    }
    return validate(snap)


def scripted_fixtures(seed: int = 1000) -> list[dict]:
    """The two E-005 reference worlds, played through the engine by scripted
    fixtures. data_status is always 'scripted-fixture'."""
    from ..agents.scripted import make_trade_policy, no_trade_policy, run_episode
    from ..world.engine import Engine
    from ..world.scenario import generate

    sc = generate(seed)
    a = Engine(sc, episode_id=f"fixture-{seed}-no-trade")
    run_episode(a, no_trade_policy)
    b = Engine(sc, episode_id=f"fixture-{seed}-reference-trades")
    run_episode(b, make_trade_policy())
    return [
        from_engine(a, "scripted-fixture", "No-trade reference",
                    "Each district draws its own entitlement up to its demand and buys "
                    "alternative supply for the rest. No trades."),
        from_engine(b, "scripted-fixture", "Reference trades",
                    "Surplus entitlement is sold to districts in deficit, then every district "
                    "draws its entitlement up to its demand."),
    ]


SNAP_BLOCK = re.compile(r'(<script id="snapshots" type="application/json">)(.*?)(</script>)', re.S)
POSTER_BLOCK = re.compile(r'(<script id="posters" type="application/json">)(.*?)(</script>)', re.S)


def canonical_hash(snap: dict) -> str:
    """SHA-256 of canonical JSON (sorted keys, no spaces). The page computes the same hash to
    decide whether a pre-rendered frame belongs to the snapshot on screen."""
    text = json.dumps(snap, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def embedded_posters(html: str) -> dict:
    m = POSTER_BLOCK.search(html)
    if not m:
        raise SnapshotError("no posters block")
    return json.loads(m.group(2) or "{}")


def prune_posters(html: str, snapshots: list[dict]) -> str:
    """Drop pre-rendered frames that no longer match an embedded snapshot."""
    keep = {canonical_hash(s) for s in snapshots}
    posters = {k: v for k, v in embedded_posters(html).items() if k in keep}
    payload = json.dumps(posters, sort_keys=True)
    return POSTER_BLOCK.sub(lambda m: m.group(1) + "\n" + payload + "\n" + m.group(3), html)


def embed(html: str, snapshots: list[dict]) -> str:
    """Replace the page's embedded snapshot block (the page draws only from it)."""
    for s in snapshots:
        validate(s)
    payload = json.dumps(snapshots, indent=1, sort_keys=True)
    if "</" in payload:
        raise SnapshotError("snapshot text may not contain '</'")
    if len(SNAP_BLOCK.findall(html)) != 1:
        raise SnapshotError("page must contain exactly one snapshots block")
    return SNAP_BLOCK.sub(lambda m: m.group(1) + "\n" + payload + "\n" + m.group(3), html)


def embedded(html: str) -> list[dict]:
    m = SNAP_BLOCK.search(html)
    if not m:
        raise SnapshotError("no snapshots block")
    return json.loads(m.group(2))


def main(argv=None) -> int:
    root = Path(argv[0]) if argv else Path.cwd()
    page = root / "observatory" / "diorama" / "index.html"
    fixtures = scripted_fixtures()
    out_dir = root / "observatory" / "diorama" / "fixtures"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "scripted-S1000.json").write_text(json.dumps(fixtures, indent=1, sort_keys=True) + "\n",
                                                 encoding="utf-8")
    html = prune_posters(embed(page.read_text(encoding="utf-8"), fixtures), fixtures)
    page.write_text(html, encoding="utf-8")
    for f in fixtures:
        print(f"{f['label']}: withdrawn {sum(f['withdrawals_by_actor'].values())}, "
              f"downstream {f['downstream_flow']} of {f['minimum_required_flow']}")
    stale = [f["label"] for f in fixtures if canonical_hash(f) not in embedded_posters(html)]
    if stale:
        print("no pre-rendered frame for: " + ", ".join(stale) +
              " (run: node observatory/diorama/render_posters.mjs)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
