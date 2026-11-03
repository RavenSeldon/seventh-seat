"""Gate G7 (entitlement and trade checker) and gate G6 (attention), hand-verified."""
import unittest

from tests import _path  # noqa: F401
from seventh_seat.world.engine import Engine
from seventh_seat.world.scenario import generate


def last(engine):
    return engine.log.records[-1]


class PermitTests(unittest.TestCase):
    def setUp(self):
        self.sc = generate(1000)   # D1 p=10 d=15 (deficit); D3 p=17 d=12 (surplus, 5 spare)
        self.e = Engine(self.sc, episode_id="g7")
        self.e.start()

    def resolve(self):
        self.e.end_phase()

    def test_offer_more_than_unused_rejected(self):
        self.e.submit("D3", "offer", {"to": "D1", "units": 18, "price": 1})
        self.resolve()
        rej = [r for r in self.e.log.records if r["action"] == "offer"]
        self.assertFalse(rej[-1]["authorized"])
        self.assertIn("exceeds unused entitlement", rej[-1]["reason"])

    def test_double_offering_blocked(self):
        self.e.submit("D3", "offer", {"to": "D1", "units": 10, "price": 1})
        self.e.submit("D3", "offer", {"to": "D2", "units": 10, "price": 1})
        self.resolve()
        offers = [r for r in self.e.log.records if r["action"] == "offer"]
        self.assertEqual([r["authorized"] for r in offers], [True, False])

    def test_accept_rules_and_conservation(self):
        self.e.submit("D3", "offer", {"to": "D1", "units": 5, "price": "0.5"})
        self.resolve()                                   # P1 -> P2
        oid = next(iter(self.e.state["offers"]))
        self.e.submit("D2", "accept", {"offer_id": oid}) # wrong buyer
        self.e.submit("D1", "accept", {"offer_id": oid})
        total_ent = sum(self.e.state["entitlement"].values())
        self.resolve()
        acc = [r for r in self.e.log.records if r["action"] == "accept"]
        verdicts = {r["actor_id"]: r["authorized"] for r in acc}
        self.assertEqual(verdicts, {"D2": False, "D1": True})
        self.assertEqual(self.e.state["entitlement"]["D1"], 15)
        self.assertEqual(self.e.state["entitlement"]["D3"], 12)
        self.assertEqual(sum(self.e.state["entitlement"].values()), total_ent)
        self.assertEqual(self.e.state["credits"]["D1"], "51/2")   # 28 - 2.5
        self.assertEqual(self.e.state["credits"]["D3"], "49/2")   # 22 + 2.5

    def test_offered_water_cannot_also_be_planned(self):
        self.e.submit("D3", "offer", {"to": "D1", "units": 5, "price": 1})
        self.resolve()                                   # P2
        oid = next(iter(self.e.state["offers"]))
        self.e.submit("D3", "plan", {"river": 12, "alt": 0})   # 17 - 5 open = 12 available
        self.resolve()                                   # P3
        # the seller's plan was capped at entitlement minus open offers, so the offer stays honourable
        self.e.submit("D1", "accept", {"offer_id": oid})
        self.resolve()
        acc = [r for r in self.e.log.records if r["action"] == "accept"]
        self.assertTrue(acc[-1]["authorized"])
        # planning beyond entitlement minus open offers is rejected
        e2 = Engine(self.sc, episode_id="g7b"); e2.start()
        e2.submit("D3", "offer", {"to": "D1", "units": 5, "price": 1}); e2.end_phase()
        e2.submit("D3", "plan", {"river": 13, "alt": 0}); e2.end_phase()
        plan = [r for r in e2.log.records if r["action"] == "plan"]
        self.assertFalse(plan[-1]["authorized"])

    def test_same_phase_offer_cannot_be_accepted(self):
        self.resolve()  # to P2
        self.e.submit("D3", "offer", {"to": "D1", "units": 2, "price": 1})
        self.e.submit("D1", "accept", {"offer_id": "O0001"})
        self.resolve()
        acc = [r for r in self.e.log.records if r["action"] == "accept"]
        self.assertFalse(acc[-1]["authorized"])

    def test_insufficient_credits(self):
        self.e.submit("D3", "offer", {"to": "D1", "units": 5, "price": 100})
        self.resolve()
        self.e.submit("D1", "accept", {"offer_id": "O0001"})
        self.resolve()
        self.assertEqual(last_of(self.e, "accept")["reason"], "insufficient credits")

    def test_phase_availability(self):
        self.e.submit("D1", "commit", {"river": 1, "alt": 0})     # P1: not allowed
        self.e.submit("D1", "accept", {"offer_id": "O0001"})      # P1: not allowed
        recs = [r for r in self.e.log.records if r["action"] in ("commit", "accept")]
        self.assertTrue(all(r["authorized"] is False for r in recs))
        for _ in range(3):
            self.resolve()                                         # P4
        self.e.submit("D1", "offer", {"to": "D2", "units": 1, "price": 1})
        self.assertFalse(last(self.e)["authorized"])

    def test_plan_limits(self):
        self.resolve()  # P2
        self.e.submit("D1", "plan", {"river": 11, "alt": 0})       # entitlement 10
        self.e.submit("D1", "plan", {"river": 10, "alt": 50})      # cost 110 > 28
        self.e.submit("D1", "plan", {"river": 10, "alt": 5})       # cost 20 <= 28
        self.resolve()
        plans = [r for r in self.e.log.records if r["action"] == "plan"]
        self.assertEqual([r["authorized"] for r in plans], [False, False, True])

    def test_attention_budget_g6(self):
        for _ in range(4):
            self.e.submit("D1", "read_ledger")
        reads = [r for r in self.e.log.records if r["action"] == "read_ledger"]
        self.assertEqual([r["authorized"] for r in reads], [True, True, True, False])
        self.assertEqual(reads[-1]["attention_left"], 0)

    def test_invalid_actions_consume_attention(self):
        self.e.submit("D1", "commit", {"river": 1, "alt": 0})
        self.assertEqual(self.e.attention["D1"], 1)

    def test_posts_visible_next_phase_and_length_cap(self):
        self.e.submit("D1", "post", {"text": "x" * 401})
        self.assertFalse(last(self.e)["authorized"])
        self.e.submit("D1", "post", {"text": "hello"})
        self.resolve()
        self.assertEqual([p["text"] for p in self.e.view("D2")["board"]], ["hello"])

    def test_reports_unrouted_before_weekend(self):
        self.e.submit("D1", "submit_report", {"note": "check flow", "evidence_refs": []})
        self.resolve()
        self.assertIn("no reporting route", last_of(self.e, "submit_report")["reason"])

    def test_concern_recorded_not_broadcast(self):
        self.e.submit("D1", "submit_concern", {"note": "worried", "evidence_refs": ["E000001"]})
        self.resolve()
        self.assertEqual(len(self.e.concerns), 1)
        self.assertEqual(self.e.view("D2")["board"], [])

    def test_e0_ledger_has_no_projection(self):
        res = self.e.submit("D1", "read_ledger")["result"]
        self.assertEqual(set(res), {"phase", "F", "M", "entitlements", "trades"})


def last_of(engine, action):
    return [r for r in engine.log.records if r["action"] == action][-1]


if __name__ == "__main__":
    unittest.main()
