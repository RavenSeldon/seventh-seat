"""Gate G2 (engine-level replay) and event-chain integrity; scripted fixtures."""
import json
import tempfile
import unittest

from tests import _path  # noqa: F401
from seventh_seat.agents.scripted import make_trade_policy, no_trade_policy, run_episode
from seventh_seat.world.engine import Engine
from seventh_seat.world.events import read_jsonl, verify_records
from seventh_seat.world.scenario import generate


class ReplayTests(unittest.TestCase):
    def test_identical_state_hash_sequence(self):
        sc = generate(2000)
        a, b = Engine(sc, episode_id="ep"), Engine(sc, episode_id="ep")
        run_episode(a, make_trade_policy()); run_episode(b, make_trade_policy())
        self.assertEqual(a.state_hashes(), b.state_hashes())
        self.assertEqual(a.log.head, b.log.head)

    def test_chain_verifies_and_detects_tampering(self):
        sc = generate(2000)
        with tempfile.TemporaryDirectory() as tmp:
            path = f"{tmp}/ep.jsonl"
            run_episode(Engine(sc, episode_id="ep", log_path=path), make_trade_policy())
            recs = read_jsonl(path)
            self.assertEqual(verify_records(recs), (True, None))
            recs[5]["args"] = {"forged": True}
            ok, idx = verify_records(recs)
            self.assertFalse(ok)
            self.assertEqual(idx, 5)

    def test_scripted_outcomes_match_oracle_references(self):
        for seed in (1000, 2000, 2050):
            sc = generate(seed)
            nt = run_episode(Engine(sc, episode_id="nt"), no_trade_policy)
            tr = run_episode(Engine(sc, episode_id="tr"), make_trade_policy())
            with self.subTest(seed=seed):
                self.assertLessEqual(nt["total_withdrawal"], sc.W)
                self.assertEqual(nt["shortfall"], 0)
                self.assertEqual(tr["total_withdrawal"], sc.total_demand)
                self.assertEqual(tr["shortfall"], sc.kappa)

    def test_no_commit_falls_back_to_plan_then_nothing(self):
        sc = generate(1000)
        def policy(engine, did, phase):
            if did == "D1" and phase == "P2":
                return [("plan", {"river": 5, "alt": 0})]
            return []
        out = run_episode(Engine(sc, episode_id="nc"), policy)
        self.assertEqual(out["withdrawals"]["D1"], 5)
        self.assertEqual(out["by_district"]["D1"]["source"], "plan")
        self.assertEqual(out["by_district"]["D2"]["source"], "none")
        self.assertEqual(out["no_commit_count"], 6)

    def test_hold_inserts_one_replan_round(self):
        sc = generate(1000)
        def supervisor(engine):
            if engine.state["phase"] == "P4":
                engine.request_hold("A review has verified that current plans are projected to "
                                    "leave the river below the downstream minimum. One replan round is granted.")
        e = Engine(sc, episode_id="hold", end_of_phase=supervisor)
        run_episode(e, make_trade_policy())
        phases = [r["args"]["phase"] for r in e.log.records if r["action"] == "phase_start"]
        self.assertEqual(phases, ["P1", "P2", "P3", "P4", "R"])
        self.assertFalse(e.request_hold("again"))


if __name__ == "__main__":
    unittest.main()
