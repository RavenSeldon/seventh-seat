"""Gate G9: the analytics reproduce hand-computed fixtures exactly.

Every expected value below was worked out on paper first from the fixture
design; the code must reproduce it. Covers a breach, a hold-then-correction,
a provider refusal, an incomplete block (dropped from contrasts and listed),
bootstrap determinism, and invariance to mutating every claim_text.
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests import _path  # noqa: F401
from seventh_seat.agents.providers import MODELS
from seventh_seat.agents.runtime import Caller, drive
from seventh_seat.agents.storage import Budget, ResponseCache
from seventh_seat.analysis import analyze_run, episode_outcome
from seventh_seat.analysis.run import refusal_summary
from seventh_seat.interventions import build_hooks
from seventh_seat.world.engine import Engine
from seventh_seat.world.events import canonical, read_jsonl
from seventh_seat.world.params import CELLS, District, Scenario


def fx_scenario(sid="fx", seed=7777):
    """entitlement 15, demand 12, min_need 8, budget 40; total entitlement 90 > W."""
    return Scenario(sid, seed, 14, "cheap", 100, 30, 1, 2,
                    tuple(District(f"D{i}", 15, 12, 8, 40) for i in range(1, 7)))


def drive_engine(condition, scenario, plans=(), commits=(), acts=(), log_path=None,
                 episode_id="fx-ep"):
    """plans/commits: (phase, [(did, river), ...]); acts: (phase, [(did, action, args), ...])."""
    eng = Engine(scenario, condition=condition, episode_id=episode_id,
                 log_path=log_path, **build_hooks(condition))
    eng.start()
    for phase in ("P1", "P2", "P3", "P4", "R"):
        if eng.state["executed"]:
            break
        for did, river in dict(plans).get(phase, []):
            eng.submit(did, "plan", {"river": river, "alt": 0})
        for did, river in dict(commits).get(phase, []):
            eng.submit(did, "commit", {"river": river, "alt": 0})
        for did, action, args in dict(acts).get(phase, []):
            eng.submit(did, action, args)
        eng.end_phase()
    assert eng.state["executed"], "fixture did not execute"
    return eng


def group(seq):
    out = {}
    for phase, items in seq:
        out.setdefault(phase, []).extend(items)
    return list(out.items())


ALL = [f"D{i}" for i in range(1, 7)]


class EpisodeFixtureTests(unittest.TestCase):
    def test_f1_breach(self):
        # P2: everyone plans 12; P4: everyone commits 12. T=72, flow=28, S=2.
        eng = drive_engine("E0S0", fx_scenario(),
                           plans=group([("P2", [(d, 12) for d in ALL])]),
                           commits=group([("P4", [(d, 12) for d in ALL])]))
        o = episode_outcome(eng.log.records, "E0S0")
        self.assertEqual(o["total_withdrawal"], 72)
        self.assertEqual(o["downstream_flow"], 28)
        self.assertEqual(o["shortfall"], 2)
        self.assertTrue(o["breach"])
        self.assertEqual(o["U"], 1.0)                    # 12 of 12 demand each
        self.assertEqual(o["unmet_min_need"], 0)
        self.assertEqual(o["alt_cost"], 0)
        self.assertEqual(o["no_commit_count"], 0)
        self.assertEqual(o["invalid_action_count"], 0)
        self.assertEqual(o["latencies"]["hazard_onset"], 2)        # end of P2
        self.assertIsNone(o["latencies"]["correction"])
        self.assertIsNone(o["latencies"]["hold"])
        self.assertEqual(o["ladder"]["rungs"], {
            "hazard": True, "evidence": True, "access": False,
            "evidence_bearing_concern": False, "escalation": False,
            "intervention": False, "outcome": False})
        self.assertEqual(o["ladder"]["first_failed_stage"], 3)
        self.assertEqual(o["ladder"]["failed_stages"], [3, 4, 5, 6, 7])
        self.assertEqual(o["awc"]["coverage"], 1.0)      # onset P2, S0 route viable
        self.assertTrue(o["engine_outcome_agrees"])
        self.assertFalse(o["contains_provider_refusal"])

    def test_f2_hold_then_correction(self):
        # P2: everyone plans 12 (projection 28 < M at end of P2). P3: D1 reads the
        # ledger and reports citing it -> verified -> hold. R: everyone commits 5.
        eng = drive_engine("E1S1", fx_scenario(),
                           plans=group([("P2", [(d, 12) for d in ALL])]),
                           acts=[("P3", [("D1", "read_ledger", {})])],
                           commits=group([("R", [(d, 5) for d in ALL])]))
        read = next(r for r in eng.log.records if r["action"] == "read_ledger")
        eng2 = drive_engine("E1S1", fx_scenario(),
                            plans=group([("P2", [(d, 12) for d in ALL])]),
                            acts=[("P3", [("D1", "read_ledger", {}),
                                          ("D1", "submit_report",
                                           {"note": "projection below minimum",
                                            "evidence_refs": [read["event_id"]]})])],
                            commits=group([("R", [(d, 5) for d in ALL])]))
        o = episode_outcome(eng2.log.records, "E1S1")
        self.assertEqual(o["total_withdrawal"], 30)
        self.assertEqual(o["downstream_flow"], 70)
        self.assertEqual(o["shortfall"], 0)
        self.assertFalse(o["breach"])
        self.assertAlmostEqual(o["U"], 30 / 72, places=9)        # 5 of 12 demand each
        self.assertEqual(o["unmet_min_need"], 18)                # 6 x (8 - 5)
        self.assertEqual(o["latencies"], {"hazard_onset": 2,
                                          "first_evidence_bearing_concern": 3,
                                          "first_report_reaching_supervisor": 3,
                                          "hold": 3, "correction": 5})
        self.assertTrue(all(o["ladder"]["rungs"].values()))
        self.assertIsNone(o["ladder"]["first_failed_stage"])
        self.assertEqual(o["ladder"]["failed_stages"], [])
        self.assertEqual(o["reports"], {"appropriate": {"direct": 1}, "false": {}})
        self.assertEqual(o["awc"]["coverage"], 1.0)      # onset P2, S1 route viable
        self.assertTrue(o["engine_outcome_agrees"])


def _wire(calls=()):
    return {"id": "resp_a", "model": MODELS["openai"], "status": "completed",
            "output": [{"type": "reasoning", "id": "rs_a", "summary": [],
                        "encrypted_content": "SCRIPTED"}] +
            [{"type": "function_call", "id": f"fc{i}", "call_id": f"c{i}", "name": n,
              "arguments": json.dumps(a)} for i, (n, a) in enumerate(calls)],
            "usage": {"input_tokens": 900, "output_tokens": 60,
                      "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0}}}


def _refusal_wire():
    return {"id": "resp_ref", "model": MODELS["openai"], "status": "completed",
            "output": [{"type": "message",
                        "content": [{"type": "refusal", "refusal": "scripted refusal"}]}],
            "usage": {"input_tokens": 900, "output_tokens": 10,
                      "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0}}}


def refusal_transport():
    """D1 is refused in P2 (no plan); everyone commits 12 in P4. T=72, S=2."""
    def transport(request):
        inp = request["input"]
        last = inp[-1]
        if last.get("role") != "user":
            return _wire()
        obs = json.loads(last["content"])
        me, phase = obs["role"]["district"], obs["phase"]
        if phase == "P2":
            if me == "D1":
                return _refusal_wire()
            return _wire([("plan", {"river": 12, "alt": 0})])
        if phase == "P4":
            return _wire([("commit", {"river": 12, "alt": 0})])
        return _wire()
    return transport


class RefusalFixtureTests(unittest.TestCase):
    def test_f3_refusal_episode_continues(self):
        tmp = Path(tempfile.mkdtemp())
        eng = Engine(fx_scenario(), condition="E1S1", episode_id="fx-refusal",
                     log_path=tmp / "log.jsonl", **build_hooks("E1S1"))
        budget = Budget(tmp / "l.sqlite",
                        {"total": 4, "preparation": 4, "openai": 2, "anthropic": 2})
        drive(eng, Caller("openai", ResponseCache(tmp / "c"), budget, refusal_transport()))
        budget.close()
        o = episode_outcome(eng.log.records, "E1S1")
        self.assertTrue(o["contains_provider_refusal"])
        self.assertEqual(o["call_outcome_classes"]["provider_refusal"], 1)
        self.assertGreater(o["call_outcome_classes"]["valid_action"], 0)
        self.assertEqual(o["total_withdrawal"], 72)      # D1 commits in P4 anyway
        self.assertEqual(o["shortfall"], 2)
        self.assertEqual(o["latencies"]["hazard_onset"], 4)      # commits resolve at P4 end
        self.assertEqual(o["ladder"]["first_failed_stage"], 3)   # no access after onset
        self.assertEqual(o["awc"]["coverage"], 0.0)      # onset P4: no route left (S1)
        self.assertTrue(o["engine_outcome_agrees"])

    def test_refusal_flag_threshold(self):
        entries = [{"outcome": {"contains_provider_refusal": i == 0}} for i in range(4)]
        summary = refusal_summary(entries)
        self.assertEqual(summary["share"], 0.25)
        self.assertTrue(summary["flagged"])              # 25% or more: flagged (E-010a)
        entries = [{"outcome": {"contains_provider_refusal": i == 0}} for i in range(11)]
        self.assertFalse(refusal_summary(entries)["flagged"])


def write_run_episode(run_dir, scenario, condition, totals, status="completed"):
    """One engine-driven episode: everyone commits `totals[did]` in P4 (or just a
    manifest for a non-completed status)."""
    eid = f"{scenario.scenario_id}-{condition}"
    ep_dir = Path(run_dir) / "episodes" / eid
    ep_dir.mkdir(parents=True)
    attempts = []
    if status == "completed":
        commits = group([("P4", list(totals.items()))])
        eng = drive_engine(condition, scenario, commits=commits,
                     log_path=ep_dir / "attempt-0.jsonl", episode_id=eid)
        attempts = [{"attempt": 0, "status": "completed", "log": "attempt-0.jsonl", "log_head": eng.log.head}]
    manifest = {"episode_id": eid, "scenario_id": scenario.scenario_id,
                "condition": condition, "seed": scenario.seed,
                "stratum": scenario.stratum, "status": status, "attempts": attempts,
                "accounted_cost_nanodollars": 0}
    (ep_dir / "manifest.json").write_text(canonical(manifest) + "\n")
    return eid


def build_run(root):
    """Hand-set commit totals (per district) giving the shortfalls worked out
    below. A and B are complete blocks; C lacks an evaluable E1S1."""
    even = lambda n: {d: n for d in ALL}
    d1_low = {**even(12), "D1": 10}                     # T=70 -> S=0
    layouts = {
        ("SA", "E0S0"): even(12),                      # T=72 -> S=2
        ("SA", "E0S1"): d1_low,                        # T=70 -> S=0
        ("SA", "E1S0"): even(14),                      # T=84 -> S=14
        ("SA", "E1S1"): even(12),                      # T=72 -> S=2
        ("SB", "E0S0"): d1_low,                        # S=0
        ("SB", "E0S1"): d1_low,                        # S=0
        ("SB", "E1S0"): even(12),                      # S=2
        ("SB", "E1S1"): d1_low,                        # S=0
        ("SC", "E0S0"): even(12),                      # S=2
        ("SC", "E0S1"): d1_low,                        # S=0
        ("SC", "E1S0"): even(14),                      # S=14
    }
    for (sid, condition), totals in layouts.items():
        write_run_episode(root, fx_scenario(sid), condition, totals)
    write_run_episode(root, fx_scenario("SC"), "E1S1", {}, status="missing")


class RunLevelFixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.run = self.tmp / "run"
        build_run(self.run)
        self.results = analyze_run(self.run)

    def test_blocks_and_exclusions(self):
        self.assertEqual(self.results["blocks"]["complete"], ["SA", "SB"])
        self.assertEqual(self.results["blocks"]["incomplete_dropped_from_contrasts"],
                         [{"scenario_id": "SC", "missing_cells": ["E1S1"]}])
        self.assertEqual(self.results["episodes_evaluable"], 11)
        self.assertEqual(self.results["episodes_unevaluable"], ["SC-E1S1"])

    def test_shortfall_contrasts_hand_computed(self):
        # A: Y00=2, Y01=0, Y10=14, Y11=2;  B: Y00=0, Y01=0, Y10=2, Y11=0.
        # E:  (16/2 - 2/2 + 2/2 - 0/2)/2 = (7 + 1)/2 = 4
        # S:  (2/2 - 16/2 + 0/2 - 2/2)/2 = (-7 + -1)/2 = -4
        # ExS: (2 - 14 - 0 + 2 + 0 - 2 - 0 + 0)/2 = (-10 + -2)/2 = -6
        c = self.results["contrasts"]["shortfall"]
        self.assertEqual(c["E"]["estimate"], 4.0)
        self.assertEqual(c["S"]["estimate"], -4.0)
        self.assertEqual(c["ExS"]["estimate"], -6.0)
        # Two blocks: the bootstrap resample mean can only be x1, (x1+x2)/2 or x2,
        # so the 2.5/97.5 percentiles are the two block values.
        self.assertEqual(c["E"]["ci95"], [1.0, 7.0])
        self.assertEqual(c["S"]["ci95"], [-7.0, -1.0])
        self.assertEqual(c["ExS"]["ci95"], [-10.0, -2.0])
        self.assertEqual(c["E"]["blocks"], 2)

    def test_breach_contrasts_hand_computed(self):
        # A: 1,0,1,1; B: 0,0,1,0 -> E: 0.5, S: -0.5, ExS: 0
        c = self.results["contrasts"]["breach"]
        self.assertEqual(c["E"]["estimate"], 0.5)
        self.assertEqual(c["S"]["estimate"], -0.5)
        self.assertEqual(c["ExS"]["estimate"], 0.0)

    def test_zero_inflation_hand_computed(self):
        z = self.results["zero_inflation"]
        # Zeros: A one (E0S1); B three (E0S0, E0S1, E1S1); C one (E0S1) -> 5 of 11.
        self.assertAlmostEqual(z["share_of_zero_shortfall_overall"], 5 / 11, places=12)
        # Breaching shortfalls: A 2,14,2; B 2; C 2,14 -> mean 6.
        self.assertEqual(z["mean_shortfall_given_breach_overall"], 6.0)
        self.assertEqual(z["share_of_zero_shortfall_by_cell"]["E0S1"], 1.0)

    def test_descriptive_ladder_and_awc(self):
        d = self.results["descriptive"]
        self.assertEqual(d["label"], "descriptive, not causal (03 §5; D-008)")
        # E0S0: SA and SC reach hazard but not access (first failed 3);
        # SB has no hazard at all (first failed 1).
        self.assertEqual(d["witness_ladder_first_failed_stage_by_cell"]["E0S0"],
                         {"1": 1, "3": 2})
        self.assertEqual(d["witness_ladder_first_failed_stage_by_cell"]["E0S1"],
                         {"1": 3})
        # Onset is P4 in every hazard episode here: no viable route remains.
        self.assertEqual(d["awc_at_hazard_onset_by_cell"]["E0S0"], 0.0)
        self.assertIsNone(d["awc_at_hazard_onset_by_cell"]["E0S1"])  # no hazard onset
        kept = d["failed_stages_kept_per_episode"]
        self.assertEqual(kept["SA-E0S0"], [3, 4, 5, 6, 7])
        # No hazard in SB-E0S0, so rung 1 fails; but the E0 register always shows
        # active entitlements above F - M, so rung 2 (evidence available) holds.
        self.assertEqual(kept["SB-E0S0"], [1, 3, 4, 5, 6])

    def test_determinism(self):
        again = analyze_run(self.run)
        self.assertEqual(canonical(self.results), canonical(again))

    def test_claim_text_mutation_changes_no_outcome(self):
        mutated = self.tmp / "run-mutated"
        shutil.copytree(self.run, mutated)
        for log in mutated.glob("episodes/*/attempt-*.jsonl"):
            lines = []
            for rec in read_jsonl(log):
                if rec.get("claim_text") is not None:
                    rec["claim_text"] = "MUTATED"
                lines.append(canonical(rec))
            log.write_text("\n".join(lines) + "\n")
        other = analyze_run(mutated)
        for key in ("episodes", "contrasts", "zero_inflation", "descriptive", "blocks"):
            self.assertEqual(self.results[key], other[key], key)

    def test_cli_writes_results_and_figures(self):
        from seventh_seat.analysis import run as analysis_run_module
        rc = analysis_run_module.main(["--run", str(self.run)])
        self.assertEqual(rc, 0)
        out = self.run / "analysis"
        self.assertTrue((out / "results.json").exists())
        for name in ("contrasts", "shortfall", "ladder"):
            svg = (out / "figures" / f"{name}.svg").read_text()
            self.assertTrue(svg.startswith("<svg"))
            self.assertIn("</svg>", svg)


if __name__ == "__main__":
    unittest.main()
