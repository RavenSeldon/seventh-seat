"""Correction C-1 (D-026): unavailable cost is never US$0; selection waits for evidence."""
from pathlib import Path
import tempfile
import unittest

from tests import _path  # noqa: F401
from tests.test_qualification import CAPS, fixture_transport, run_fixture
from seventh_seat.agents import qualification as q
from seventh_seat.agents import qualification_correction as c
from seventh_seat.agents.runtime import Caller
from seventh_seat.agents.storage import Budget, ResponseCache


def score(p, passed=True, spend=None, lat=10.0, n=3):
    return {"provider": p, "passed": passed, "evaluable_episodes": n, "median_episode_latency_seconds": lat,
            "spend": spend}


AVAIL = lambda x: {"evidence": "ledger", "measured_nanodollars": x, "upper_nanodollars": x}
MISSING = {"evidence": c.UNAVAILABLE, "measured_nanodollars": None, "upper_nanodollars": None}


class Selection(unittest.TestCase):
    def test_missing_cost_withholds_selection(self):
        d = c.select([score("a", spend=MISSING), score("b", spend=AVAIL(9))])
        self.assertIsNone(d["selected"]); self.assertIn("withheld", d["reason"])
        d = c.select([score("a", spend=MISSING, lat=1), score("b", spend=MISSING, lat=2)])
        self.assertIsNone(d["selected"])                            # the old false tie is gone

    def test_single_passing_needs_no_cost(self):
        self.assertEqual(c.select([score("a", spend=MISSING), score("b", False, MISSING)])["selected"], "a")

    def test_genuine_zero_cost_is_evidence(self):
        d = c.select([score("a", spend=AVAIL(0), lat=5), score("b", spend=AVAIL(0))])
        self.assertEqual(d["selected"], "a"); self.assertIn("latency", d["reason"])

    def test_recorded_ranking_unchanged_when_evidence_exists(self):
        s = [score("openai", spend=AVAIL(25983845)), score("anthropic", spend=AVAIL(70419600), lat=1)]
        self.assertEqual(c.select(s), q.select(s))
        self.assertEqual(c.select(s)["selected"], "openai")


class Records(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory(); td = Path(self.td.name)
        self.ledger, self.cache = td / "ledger.sqlite", ResponseCache(td / "cache")
        self.live = {p: run_fixture(td, p)[1] for p in ("openai", "anthropic")}
        for p in ("openai", "anthropic"):
            q.run_suite(Caller(p, self.cache, replay=True), td / f"replay-{p}")
        self.td_path = td

    def tearDown(self):
        self.td.cleanup()

    def test_replay_spend_is_unavailable_not_zero(self):
        s = c.run_spend(self.td_path / "replay-openai", self.ledger)
        self.assertEqual(s["evidence"], c.UNAVAILABLE)
        self.assertIsNone(s["measured_nanodollars"])
        self.assertEqual(s["this_run_additional_nanodollars"], 0)    # the replay itself cost nothing
        live = c.run_spend(self.td_path / "openai", self.ledger)
        self.assertEqual(live["measured_nanodollars"], self.live["openai"]["spend"]["measured_nanodollars"])

    def test_verified_history_reproduces_live_selection(self):
        scores_own, scores_hist = [], []
        for p in ("openai", "anthropic"):
            base = q.score_run(self.td_path / f"replay-{p}", self.cache, None, True)
            scores_own.append(c.with_spend(base, c.run_spend(self.td_path / f"replay-{p}", self.ledger)))
            h = c.historical_spend(self.td_path / f"replay-{p}", self.td_path / p, self.cache, self.ledger)
            self.assertEqual(h["evidence"], "historical-verified")
            scores_hist.append(c.with_spend(base, h))
        self.assertIsNone(c.select(scores_own)["selected"])
        self.assertEqual(c.select(scores_hist), q.select(list(self.live.values())))

    def test_unverifiable_history_stays_unavailable(self):
        h = c.historical_spend(self.td_path / "replay-openai", self.td_path / "anthropic", self.cache, self.ledger)
        self.assertEqual(h["evidence"], c.UNAVAILABLE)
        empty = Budget(self.td_path / "empty.sqlite", CAPS); empty.close()
        h = c.historical_spend(self.td_path / "replay-openai", self.td_path / "openai", self.cache, self.td_path / "empty.sqlite")
        self.assertEqual(h["evidence"], c.UNAVAILABLE)


class ZeroCostLive(unittest.TestCase):
    def test_zero_charge_rows_are_available_zero(self):
        inner = fixture_transport("openai")

        def free(request):
            r = inner(request)
            r["usage"] = {"input_tokens": 0, "output_tokens": 0,
                          "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0}}
            return r
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            b = Budget(td / "l.sqlite", CAPS)
            q.run_suite(Caller("openai", ResponseCache(td / "c"), b, free, sleep=lambda s: None), td / "run", td / "l.sqlite")
            b.close()
            s = c.run_spend(td / "run", td / "l.sqlite")
            self.assertEqual((s["evidence"], s["measured_nanodollars"]), ("ledger", 0))


if __name__ == "__main__":
    unittest.main()
