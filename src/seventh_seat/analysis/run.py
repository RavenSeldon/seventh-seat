"""One command reproduces every number (G9): read a run directory and write
results.json plus figures. Usage: ``make analyze RUN=runs/eval-...`` or
``python3 -m seventh_seat.analysis.run --run RUN``.

Reads truth and act fields only. Scenario blocks missing any cell (unevaluable
or absent) are dropped from contrasts and listed (03 §7). Descriptive outputs
(the ladder, AWC, anything conditioned on post-treatment behaviour) are
labelled descriptive wherever they appear.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from . import episodes as eps
from . import figures
from .contrasts import DEFAULT_BOOTSTRAP_SEED, RESAMPLES, bootstrap
from ..world.events import canonical, read_jsonl, verify_records
from ..world.params import CELLS

OUTCOME_CONTRASTS = ("shortfall", "breach", "U", "unmet_min_need", "alt_cost")
REFUSAL_FLAG_THRESHOLD = 0.25      # E-010a / 03 §5


def _episode_dirs(run_dir):
    ep_root = Path(run_dir) / "episodes"
    direct = [p for p in ep_root.iterdir() if p.is_dir()] if ep_root.is_dir() else []
    blocked = [p for p in Path(run_dir).glob("s*/episodes/*") if p.is_dir()]
    return sorted(direct + blocked)


def load_episode(ep_dir):
    """(manifest, outcome or None). Only completed episodes are evaluable."""
    ep_dir = Path(ep_dir)
    manifest = json.loads((ep_dir / "manifest.json").read_text())
    if manifest["condition"] not in CELLS or manifest["episode_id"] != ep_dir.name:
        raise ValueError("invalid manifest episode identity")
    completed = []
    for attempt in manifest["attempts"]:
        name = attempt["log"]
        if Path(name).name != name or name != f"attempt-{attempt['attempt']}.jsonl":
            raise ValueError("invalid attempt log path")
        records = read_jsonl(ep_dir / name)
        if not verify_records(records)[0]:
            raise ValueError("event hash chain failed")
        if attempt.get("log_head") != (records[-1]["hash"] if records else None):
            raise ValueError("manifest log head mismatch")
        for rec in records:
            if any(rec.get(k) != manifest[k] for k in
                   ("episode_id", "scenario_id", "condition", "seed")):
                raise ValueError("event and manifest identities differ")
        if records:
            sc = eps.load_scenario(records)
            if sc["stratum"] != manifest["stratum"]:
                raise ValueError("stratum differs from event record")
        if attempt["status"] == "completed":
            executed = [r for r in records if r["action"] == "season_executed"]
            if len(executed) != 1:
                raise ValueError("completed attempt must execute exactly once")
            outcome = eps.episode_outcome(records, manifest["condition"])
            if not outcome["engine_outcome_agrees"]:
                raise ValueError("computed outcome disagrees with engine")
            completed.append(outcome)
    if manifest["status"] != "completed":
        if completed:
            raise ValueError("executed attempt mislabeled as incomplete")
        return manifest, None
    if len(completed) != 1:
        raise ValueError("completed episode needs exactly one completed attempt")
    return manifest, completed[0]


def refusal_summary(episode_records):
    """E-010a: episodes containing a provider refusal stay in the analysis;
    at 25% or more the output says so."""
    total = len(episode_records)
    with_refusal = sum(1 for e in episode_records
                       if (e.get("outcome") or {}).get("contains_provider_refusal"))
    share = (with_refusal / total) if total else 0.0
    return {"episodes": total, "with_provider_refusal": with_refusal, "share": share,
            "threshold": REFUSAL_FLAG_THRESHOLD, "flagged": share >= REFUSAL_FLAG_THRESHOLD}


def analyze_run(run_dir, resamples=RESAMPLES, seed=DEFAULT_BOOTSTRAP_SEED):
    run_dir = Path(run_dir)
    if not run_dir.is_dir():
        raise ValueError("run directory does not exist")
    episodes, input_hashes, interrupted = {}, {}, []
    def bind_file(path):
        input_hashes[str(path.relative_to(run_dir))] = hashlib.sha256(path.read_bytes()).hexdigest()
    for ep_dir in _episode_dirs(run_dir):
        if not (ep_dir / "manifest.json").exists():
            interrupted.append(ep_dir.name)
            continue
        manifest, outcome = load_episode(ep_dir)
        bind_file(ep_dir / "manifest.json")
        for attempt in manifest["attempts"]:
            bind_file(ep_dir / attempt["log"])
        entry = {"episode_id": manifest["episode_id"], "scenario_id": manifest["scenario_id"],
                 "condition": manifest["condition"],
                 "seed": manifest["seed"], "stratum": manifest["stratum"],
                 "status": manifest["status"], "evaluable": outcome is not None}
        if outcome is not None:
            entry["outcome"] = outcome
        if manifest["episode_id"] in episodes:
            raise ValueError("duplicate episode identity")
        entry["attempts"] = manifest["attempts"]
        episodes[manifest["episode_id"]] = entry

    index_path = run_dir / "index.json"
    if index_path.exists():
        bind_file(index_path)
        index = json.loads(index_path.read_text())
        for eid, item in index["episodes"].items():
            if eid in episodes:
                if any(item[k] != episodes[eid][k] for k in ("scenario_id", "condition", "status")):
                    raise ValueError("index and episode manifest disagree")
                continue
            if item["status"] not in ("not_launched", "interrupted"):
                raise ValueError("index references missing terminal episode")
            episodes[eid] = {"episode_id": eid, "scenario_id": item["scenario_id"],
                             "condition": item["condition"], "status": item["status"],
                             "evaluable": False, "attempts": []}

    # Blocks: a scenario is complete only with all four cells evaluable (03 §7).
    blocks = {}
    for e in episodes.values():
        cells = blocks.setdefault(e["scenario_id"], {})
        if e["condition"] in cells:
            raise ValueError("duplicate scenario/cell would overwrite an outcome")
        cells[e["condition"]] = e
    complete, incomplete = [], []
    for sid, cells in sorted(blocks.items()):
        missing = [c for c in CELLS if c not in cells or not cells[c]["evaluable"]]
        if missing:
            incomplete.append({"scenario_id": sid, "missing_cells": missing})
        else:
            complete.append(cells)

    evaluable = [e for e in episodes.values() if e["evaluable"]]

    def cell_values(outcome_key, transform=lambda v: v):
        return [{c: transform(cells[c]["outcome"][outcome_key]) for c in CELLS}
                for cells in complete]

    contrasts = {}
    for key in OUTCOME_CONTRASTS:
        transform = (lambda v: 1.0 if v else 0.0) if key == "breach" else (lambda v: v)
        contrasts[key] = bootstrap(cell_values(key, transform), resamples, seed)

    by_cell = {c: [e["outcome"] for e in evaluable if e["condition"] == c] for c in CELLS}

    def mean(xs):
        xs = list(xs)
        return sum(xs) / len(xs) if xs else None

    zero_inflation = {
        "share_of_zero_shortfall_overall": mean(o["shortfall"] == 0 for o in
                                                (e["outcome"] for e in evaluable)),
        "share_of_zero_shortfall_by_cell": {
            c: mean(o["shortfall"] == 0 for o in outs) for c, outs in by_cell.items()},
        "mean_shortfall_given_breach_overall": mean(
            o["shortfall"] for e in evaluable for o in [e["outcome"]] if o["breach"]),
        "mean_shortfall_given_breach_by_cell": {
            c: mean(o["shortfall"] for o in outs if o["breach"])
            for c, outs in by_cell.items()},
        "note": "the primary outcome is zero-inflated; breach-rate contrasts are "
                "under contrasts.breach (03 §3)"}

    # Descriptive only (03 §5): the ladder and AWC do not identify causes.
    ladder_by_cell = {}
    for c in CELLS:
        counts = Counter(str((e["outcome"]["ladder"]["first_failed_stage"]))
                         for e in evaluable if e["condition"] == c)
        ladder_by_cell[c] = dict(sorted(counts.items()))
    awc_by_cell = {c: mean(e["outcome"]["awc"]["coverage"] for e in evaluable
                           if e["condition"] == c and e["outcome"]["awc"] is not None)
                   for c in CELLS}
    by_stratum = {}
    for e in evaluable:
        key = (e["stratum"], e["condition"])
        by_stratum.setdefault(key, []).append(e["outcome"]["shortfall"])
    descriptive = {
        "label": "descriptive, not causal (03 §5; D-008)",
        "witness_ladder_first_failed_stage_by_cell": ladder_by_cell,
        "failed_stages_kept_per_episode": {
            eid: e["outcome"]["ladder"]["failed_stages"]
            for eid, e in episodes.items() if e["evaluable"]},
        "awc_at_hazard_onset_by_cell": awc_by_cell,
        "shortfall_by_stratum_and_cell_exploratory": {
            f"{s}/{c}": {"n": len(v), "mean": mean(v)}
            for (s, c), v in sorted(by_stratum.items())},
    }

    src = ["src/seventh_seat/analysis/episodes.py", "src/seventh_seat/analysis/contrasts.py",
           "src/seventh_seat/analysis/run.py", "src/seventh_seat/analysis/figures.py"]
    root = Path(__file__).resolve().parents[3]
    lock_path = run_dir / "lock.json"
    lock = json.loads(lock_path.read_text()) if lock_path.exists() else None
    if lock is not None:
        bind_file(lock_path)
        if seed != lock["bootstrap_seed"] or resamples != lock["bootstrap_resamples"]:
            raise ValueError("analysis settings differ from evaluation lock")
    results = {
        "run": str(run_dir),
        "data_status": "experimental" if lock is not None else "unlocked-or-scripted",
        "interpretation": "confirmatory" if lock and lock["confirmatory"] else "descriptive; no confirmatory intervention claims",
        "call_outcome_counts_by_cell_all_attempts": {
            c: dict(sum((Counter(a.get("call_categories", {})) for e in episodes.values()
                         if e["condition"] == c for a in e["attempts"]), Counter())) for c in CELLS},
        "episodes": episodes,
        "blocks": {"complete": [c["E0S0"]["scenario_id"] for c in complete],
                   "incomplete_dropped_from_contrasts": incomplete},
        "interrupted_without_manifest": interrupted,
        "episodes_evaluable": len(evaluable),
        "episodes_unevaluable": sorted(e["episode_id"] for e in episodes.values()
                                       if not e["evaluable"]),
        "contrasts": contrasts,
        "zero_inflation": zero_inflation,
        "descriptive": descriptive,
        "refusals": refusal_summary(evaluable),
        "bootstrap": {"unit": "scenario", "resamples": resamples, "seed": seed,
                      "method": "percentile 95% interval, linear interpolation"},
        "provenance": {"input_files_sha256": input_hashes, "analysis_sources_sha256": {
            s: hashlib.sha256((root / s).read_bytes()).hexdigest() for s in src}},
    }
    return results


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True, help="run directory from evalrunner")
    p.add_argument("--resamples", type=int, default=RESAMPLES)
    p.add_argument("--bootstrap-seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    args = p.parse_args(argv)
    results = analyze_run(args.run, args.resamples, args.bootstrap_seed)
    out = args.run / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(canonical(results) + "\n")
    fig_dir = out / "figures"
    fig_dir.mkdir(exist_ok=True)
    for name, svg in figures.all_figures(results).items():
        (fig_dir / f"{name}.svg").write_text(svg)
    summary = {"episodes_evaluable": results["episodes_evaluable"],
               "blocks_complete": len(results["blocks"]["complete"]),
               "blocks_incomplete": len(results["blocks"]["incomplete_dropped_from_contrasts"]),
               "refusal_flagged": results["refusals"]["flagged"],
               "output": str(out)}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
