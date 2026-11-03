"""Scenario generator invariants (02 §2; E-005; E-006)."""
import unittest

from tests import _path  # noqa: F401
from seventh_seat.world.params import (CALIBRATION_SEEDS, EVALUATION_SEEDS, KAPPA_STEPS,
                                       STRATA, SURPLUS_MARGIN)
from seventh_seat.world.scenario import assign_strata, generate


class ScenarioTests(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(generate(2042), generate(2042))
        self.assertEqual(generate(2042, stratum="costly"), generate(2042, stratum="costly"))

    def test_seed_sets_disjoint(self):
        self.assertFalse(set(CALIBRATION_SEEDS) & set(EVALUATION_SEEDS))

    def test_invariants_all_seeds_kappas_strata(self):
        for kappa in KAPPA_STEPS:
            for stratum in STRATA:
                for seed in list(CALIBRATION_SEEDS) + list(EVALUATION_SEEDS):
                    sc = generate(seed, kappa=kappa, stratum=stratum)
                    with self.subTest(seed=seed, kappa=kappa, stratum=stratum):
                        self.assertEqual(sc.total_demand, sc.W + kappa)
                        self.assertEqual(sc.total_entitlement, sc.total_demand + SURPLUS_MARGIN)
                        self.assertGreaterEqual(sc.deficit_gap, kappa)
                        self.assertLess(sum(d.min_need for d in sc.districts), sc.W)
                        n_def = sum(d.entitlement < d.demand for d in sc.districts)
                        n_sur = sum(d.entitlement > d.demand for d in sc.districts)
                        self.assertEqual((n_def, n_sur), (3, 3))
                        for d in sc.districts:
                            self.assertLessEqual(d.min_need, d.demand)
                            self.assertGreaterEqual(d.budget, sc.c_a * d.min_need)
                            self.assertGreaterEqual(d.entitlement, 4)

    def test_strata_only_change_costs(self):
        a, b = generate(1000, stratum="cheap"), generate(1000, stratum="costly")
        self.assertEqual([(d.entitlement, d.demand, d.min_need) for d in a.districts],
                         [(d.entitlement, d.demand, d.min_need) for d in b.districts])
        self.assertEqual((a.c_a, b.c_a), (2, 5))

    def test_strata_balanced(self):
        seeds = list(range(2000, 2020))
        m = assign_strata(seeds)
        self.assertEqual(sum(v == "cheap" for v in m.values()), 10)
        self.assertEqual(m, assign_strata(seeds))


if __name__ == "__main__":
    unittest.main()
