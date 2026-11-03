"""Gates G3 (feasibility) and G3b (trade-off certification, E-005); E-006 frontier."""
import dataclasses
import itertools
import json
import random
import tempfile
import unittest
from fractions import Fraction as Fr

from tests import _path  # noqa: F401
from seventh_seat.world.oracle import certify, certify_all, max_utility
from seventh_seat.world.params import (CALIBRATION_SEEDS, EVALUATION_SEEDS, KAPPA_STEPS,
                                       District, Scenario)
from seventh_seat.world.scenario import generate


def brute_force_utility(sc, river_cap):
    """Integer grid search over river splits; exact because caps are integral here."""
    best = Fr(0)
    ranges = [range(0, d.demand + 1) for d in sc.districts]
    for ws in itertools.product(*ranges):
        if sum(ws) > river_cap or sum(ws) > sc.total_entitlement:
            continue
        total = Fr(0)
        ok = True
        for d, w in zip(sc.districts, ws):
            if sc.c_r * w > d.budget:
                ok = False
                break
            total += min(Fr(d.demand), w + Fr(d.budget - sc.c_r * w, sc.c_a))
        if ok:
            best = max(best, total)
    return best


class OracleTests(unittest.TestCase):
    def test_g3_g3b_every_seed_default_kappa_both_strata(self):
        for stratum in ("cheap", "costly"):
            for seed in list(CALIBRATION_SEEDS) + list(EVALUATION_SEEDS):
                cert = certify(generate(seed, stratum=stratum))
                with self.subTest(seed=seed, stratum=stratum):
                    self.assertTrue(cert["passes"], cert["checks"])

    def test_g3b_holds_at_every_calibration_step(self):
        for kappa in KAPPA_STEPS:
            for seed in (1000, 1050, 2000, 2099):
                with self.subTest(kappa=kappa, seed=seed):
                    self.assertTrue(certify(generate(seed, kappa=kappa))["passes"])

    def test_trade_reference_deficit_equals_kappa(self):
        sc = generate(1000)
        cert = certify(sc)
        self.assertEqual(cert["trade_reference"]["total_withdrawal"], 84)
        self.assertEqual(cert["trade_reference"]["total_withdrawal"] - sc.W, sc.kappa)

    def test_frontier_monotone_and_consistent(self):
        sc = generate(2000, stratum="costly")
        cert = certify(sc)
        u = [r["utility_units"] for r in cert["frontier"]]
        self.assertEqual(len(u), sc.kappa + 1)
        self.assertTrue(all(b >= a for a, b in zip(u, u[1:])))
        self.assertAlmostEqual(u[0], cert["utility_safe_max"])
        self.assertGreaterEqual(cert["price_of_protection"], 0)

    def test_closed_form_matches_brute_force(self):
        rng = random.Random("oracle-bruteforce")
        for trial in range(40):
            ds = []
            for i in range(2):
                dem = rng.randint(3, 9)
                ds.append(District(f"D{i+1}", entitlement=rng.randint(1, 10), demand=dem,
                                   min_need=1, budget=rng.randint(dem, 2 * dem + 4)))
            sc = Scenario("bf", 0, 0, "cheap", 100, 30, 1, 2, tuple(ds))
            for cap in range(0, 14):
                with self.subTest(trial=trial, cap=cap):
                    self.assertEqual(max_utility(sc, cap), brute_force_utility(sc, cap))

    def test_infeasible_scenario_rejected_and_logged(self):
        sc = generate(1000)
        poor = dataclasses.replace(sc, scenario_id="poor", districts=tuple(
            dataclasses.replace(d, budget=0) for d in sc.districts))
        with tempfile.NamedTemporaryFile("r", suffix=".jsonl", delete=False) as fh:
            accepted, rejected = certify_all([sc, poor], rejection_log=fh.name)
            self.assertEqual([s.scenario_id for s, _ in accepted], [sc.scenario_id])
            with open(fh.name, encoding="utf-8") as log_fh:
                logged = [json.loads(line) for line in log_fh]
        self.assertEqual(logged[0]["scenario_id"], "poor")
        self.assertIn("safe_feasible", logged[0]["failed"])


if __name__ == "__main__":
    unittest.main()
