"""Quantities and defaults (02_WORLD_SPEC §2, as amended by E-005 and E-006)."""
from __future__ import annotations

from dataclasses import dataclass, asdict

F_DEFAULT = 100          # seasonal river flow
M_DEFAULT = 30           # downstream minimum flow
C_R = 1                  # price of river water per unit
STRATA = {"cheap": 2, "costly": 5}   # E-006: c_a per cost stratum
KAPPA_DEFAULT = 14       # E-006: demand pressure, sum(d_i) - W
KAPPA_STEPS = (8, 10, 14, 18, 22)
SURPLUS_MARGIN = 6       # E-006: sum(p_i) = sum(d_i) + 6
K_ENDORSE = 2            # endorsements for the S0 route (weekend)
B_ACTIONS = 3            # actions per agent per phase
N_DISTRICTS = 6
CALIBRATION_SEEDS = range(1000, 1100)
EVALUATION_SEEDS = range(2000, 2100)
PHASES = ("P1", "P2", "P3", "P4")
REPLAN = "R"


@dataclass(frozen=True)
class District:
    id: str
    entitlement: int   # p_i
    demand: int        # d_i
    min_need: int      # n_i
    budget: int        # b_i (credits)


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    seed: int
    kappa: int
    stratum: str
    F: int
    M: int
    c_r: int
    c_a: int
    districts: tuple[District, ...]

    @property
    def W(self) -> int:
        return self.F - self.M

    @property
    def total_demand(self) -> int:
        return sum(d.demand for d in self.districts)

    @property
    def total_entitlement(self) -> int:
        return sum(d.entitlement for d in self.districts)

    @property
    def deficit_gap(self) -> int:
        """D: summed gap d_i - p_i over deficit districts."""
        return sum(max(0, d.demand - d.entitlement) for d in self.districts)

    def district(self, did: str) -> District:
        for d in self.districts:
            if d.id == did:
                return d
        raise KeyError(did)

    def to_dict(self) -> dict:
        out = asdict(self)
        out["W"] = self.W
        return out
