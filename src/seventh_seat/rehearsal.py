"""End-to-end scripted dry run (Runbook Thu; ROADMAP Thursday item 3). Offline, no credentials.

scenario -> oracle certificate -> agents and tools through the real model-call path
(adapter, cache, budget reservation, engine) -> hash-chained event log -> cached
replay -> outcomes recomputed from act records -> validated exhibit snapshot.
Plus interrupted-run recovery and a budget-stop rehearsal.

A scripted transport stands in for the provider. Every number produced here is a
scripted fixture (E-011 `scripted-fixture`), never experimental data. The
selected configuration's request shape (GPT-6 Luna, `gm-v2`) is used throughout.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from .agents.providers import Adapter, InfrastructureError, MODELS
from .agents.qualification import MAX_TOKENS
from .agents.runtime import Caller, drive, no_hazard_scenario, run_with_recovery
from .agents.storage import Budget, BudgetStop, ResponseCache
from .agents.tools import definitions
from .observatory.snapshot import from_engine
from .world.engine import Engine
from .world.events import canonical, read_jsonl, sha256_hex, verify_records
from .world.oracle import certify, reference_trades
from .world.params import CALIBRATION_SEEDS, EVALUATION_SEEDS
from .world.scenario import generate

PROVIDER = "openai"                 # gm-v2 selection
DRY_SEED = 9001                     # outside calibration, evaluation, GM and smoke seeds
DATA_STATUS = "scripted-fixture"
CAPS = {"total": 4, "preparation": 4, "openai": 2, "anthropic": 2}


def _wire(calls=()):
    return {"id": "resp_dry", "model": MODELS[PROVIDER], "status": "completed",
            "output": [{"type": "reasoning", "id": "rs_dry", "summary": [], "encrypted_content": "SCRIPTED"}] +
            [{"type": "function_call", "id": f"fc{i}", "call_id": f"c{i}", "name": n, "arguments": json.dumps(a)}
             for i, (n, a) in enumerate(calls)],
            "usage": {"input_tokens": 900, "output_tokens": 60,
                      "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0}}}


def scripted_transport(sc, trade, fail_first=0):
    """Plays a scripted policy from what an agent is shown; no engine access."""
    state = {"calls": 0, "fail": fail_first}
    trades = reference_trades(sc)

    def transport(request):
        state["calls"] += 1
        if state["fail"] > 0:
            state["fail"] -= 1
            raise InfrastructureError("APIConnectionError", None, True)
        last = request["input"][-1]
        if last.get("role") != "user":
            return _wire()                                    # end the turn after tool results
        obs = json.loads(last["content"])
        me, phase, role = obs["role"]["district"], obs["phase"], obs["role"]
        river = min(role["entitlement"], role["demand"])
        if phase == "P1":   # one neutral post, so the claim description is exercised
            return _wire([("post", {"text": f"{me} planning this season's allocation."})] +
                         ([("offer", {"to": b, "units": u, "price": 0.5}) for s, b, u in trades if s == me] if trade else []))
        if trade and phase == "P2":
            return _wire([("accept", {"offer_id": o["offer_id"]}) for o in obs["offers_to_me"]] or [])
        if phase in ("P3", "P4"):
            alt = 0
            if not trade:
                credits = Fraction(role["credits"])
                alt = int(max(0, min(role["demand"] - river, (credits - river * role["price_river"]) // role["price_alt"])))
            return _wire([("plan" if phase == "P3" else "commit", {"river": river, "alt": alt})])
        return _wire()
    transport.state = state
    return transport


def outcome_from_acts(records, sc):
    """G9 rehearsal: recompute outcomes from authorized act records only, not engine summaries."""
    final = {d.id: None for d in sc.districts}
    for r in records:
        if r["authorized"] and r["action"] in ("plan", "commit") and r["actor_id"] in final:
            if r["action"] == "commit" or not (final[r["actor_id"]] or {}).get("commit"):
                final[r["actor_id"]] = {"river": r["args"]["river"], "alt": r["args"]["alt"],
                                        "commit": r["action"] == "commit"}
    T = sum((v or {"river": 0})["river"] for v in final.values())
    return {"total_withdrawal": T, "shortfall": max(0, sc.M - (sc.F - T)),
            "no_commit_count": sum(not (v or {}).get("commit") for v in final.values())}


def run(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=False)
    checks, record = {}, {"data_status": DATA_STATUS, "provider_config": MODELS[PROVIDER],
                          "max_tokens": MAX_TOKENS, "seed": DRY_SEED, "episodes": {}}
    assert DRY_SEED not in CALIBRATION_SEEDS and DRY_SEED not in EVALUATION_SEEDS
    sc = generate(DRY_SEED, 14, "cheap")
    cert = certify(sc)
    checks["certificate_G3_G3b"] = cert["passes"] is True
    record["certificate"] = {"scenario_id": cert["scenario_id"], "passes": cert["passes"], "checks": cert["checks"],
                             "trade_reference_withdrawal": cert["trade_reference"]["total_withdrawal"]}
    request = Adapter(PROVIDER, MAX_TOKENS).request()
    checks["containment_world_tools_only"] = (
        [t["name"] for t in request["tools"]] == [d["name"] for d in definitions()]
        and all(t["type"] == "function" for t in request["tools"]))

    budget = Budget(out / "ledger.sqlite", CAPS)
    cache = ResponseCache(out / "cache")
    for name, trade in (("reference-trades", True), ("no-trade", False)):
        log = out / f"{name}.jsonl"
        transport = scripted_transport(sc, trade)
        eng = Engine(sc, condition="E0S0", episode_id=f"dry-{name}", log_path=log)
        drive(eng, Caller(PROVIDER, cache, budget, transport), MAX_TOKENS)
        records = read_jsonl(log)
        replay = Engine(sc, condition="E0S0", episode_id=f"dry-{name}", log_path=out / f"{name}.replay.jsonl")
        drive(replay, Caller(PROVIDER, cache, replay=True), MAX_TOKENS)
        recomputed = outcome_from_acts(records, sc)
        calls = [r for r in records if r["action"] == "model_call"]
        snap = from_engine(eng, DATA_STATUS, label=f"Dry run: {name}",
                           description="Scripted fixture through the model-call path; not experimental.")
        (out / f"{name}.snapshot.json").write_text(canonical(snap) + "\n")
        checks[f"{name}_hash_chain"] = verify_records(records)[0]
        checks[f"{name}_replay_identical"] = (log.read_bytes() == (out / f"{name}.replay.jsonl").read_bytes())
        checks[f"{name}_outcome_from_acts"] = all(recomputed[k] == eng.outcome[k] for k in recomputed)
        checks[f"{name}_provenance"] = bool(calls) and all(r.get("model") and r.get("prompt_hash") and r.get("cache_key")
                                                          for r in calls)
        # 02 §8: truth (state hashes), view (hashed observations), claim (agent text), act (validated actions).
        checks[f"{name}_four_descriptions"] = (
            all(r["state_hash_before"] and r["state_hash_after"] for r in records)
            and all(r["view_hash"] for r in records if r["action"] == "observation")
            and any(r["action"] == "post" and r["authorized"] and r["claim_text"] for r in records)
            and any(r["action"] in ("plan", "commit") and r["authorized"] for r in records))
        # Log bytes include measured call latency, so only a cached replay is byte-identical;
        # independent runs are compared by their world-state hash sequence.
        record["episodes"][name] = {"log_sha256": sha256_hex(log.read_text()), "log_head": eng.log.head,
                                    "state_sequence_sha256": sha256_hex(canonical(eng.state_hashes())),
                                    "model_calls": len(calls), "outcome": {k: eng.outcome[k] for k in
                                    ("total_withdrawal", "downstream_flow", "shortfall", "breach", "demand_met",
                                     "unmet_min_need", "alt_units", "no_commit_count")},
                                    "snapshot_sha256": sha256_hex(canonical(snap))}
    ref, notr = record["episodes"]["reference-trades"]["outcome"], record["episodes"]["no-trade"]["outcome"]
    checks["mechanism_trade_reference_matches_certificate"] = (
        ref["total_withdrawal"] == cert["trade_reference"]["total_withdrawal"] and ref["breach"] is True)
    checks["mechanism_no_trade_within_cap"] = notr["breach"] is False

    # Interrupted-run recovery: three transport failures exhaust attempt 0; attempt 1 completes.
    flaky = scripted_transport(no_hazard_scenario(), False, fail_first=3)
    s = run_with_recovery(Caller(PROVIDER, ResponseCache(out / "cache-recovery"), budget, flaky, sleep=lambda x: None),
                          out / "recovery", "dry-recovery", MAX_TOKENS)
    again = run_with_recovery(Caller(PROVIDER, ResponseCache(out / "cache-recovery"), replay=True),
                              out / "recovery-replay", "dry-recovery", MAX_TOKENS)
    checks["recovery_rerun_completes"] = [a["status"] for a in s["attempts"]] == ["infrastructure_error", "completed"]
    checks["recovery_replays_identically"] = [a["status"] for a in again["attempts"]] == [a["status"] for a in s["attempts"]] \
        and again["attempts"][-1]["log_head"] == s["attempts"][-1]["log_head"]
    record["recovery"] = {"attempts": [a["status"] for a in s["attempts"]], "unresolved_reservations_kept": budget.summary()["unresolved_requests"]}
    budget.close()

    # Budget stop: caps below one reservation; no request may reach the transport.
    tiny = Budget(out / "ledger-tiny.sqlite", {"total": "0.10", "preparation": "0.10", "openai": "0.10", "anthropic": "0.10"})
    t = scripted_transport(no_hazard_scenario(), False)
    s = run_with_recovery(Caller(PROVIDER, ResponseCache(out / "cache-stop"), tiny, t), out / "budget-stop", "dry-stop", MAX_TOKENS)
    checks["budget_stop_before_any_request"] = s["status"] == "budget_stop" and t.state["calls"] == 0
    tiny.close()

    record["checks"] = checks
    record["passed"] = all(checks.values())
    (out / "dry_run.json").write_text(json.dumps(record, indent=2, sort_keys=True, default=str) + "\n")
    return record
