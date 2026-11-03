"""Seeded scenario generator (02 §2; E-005 D >= kappa; E-006 strata and kappa).

Draws of entitlements, demands and needs depend only on (seed, kappa); the
cost stratum changes c_a and therefore budgets. Seeding uses string seeds,
which Python hashes with SHA-512 (deterministic across platforms and runs).
"""
from __future__ import annotations

import math
import random
from fractions import Fraction

from .params import (C_R, F_DEFAULT, KAPPA_DEFAULT, M_DEFAULT, N_DISTRICTS,
                     STRATA, SURPLUS_MARGIN, District, Scenario)


def _split(total: int, weights: list[float], minimum: int) -> list[int]:
    """Integer split of `total` proportional to weights, each >= minimum
    (largest-remainder method, ties broken by index)."""
    n = len(weights)
    free = total - minimum * n
    if free < 0:
        raise ValueError("total too small for minimum")
    s = sum(weights)
    raw = [free * w / s for w in weights]
    base = [math.floor(r) for r in raw]
    rem = free - sum(base)
    order = sorted(range(n), key=lambda i: (-(raw[i] - base[i]), i))
    for i in order[:rem]:
        base[i] += 1
    return [b + minimum for b in base]


def generate(seed: int, kappa: int = KAPPA_DEFAULT, stratum: str = "cheap",
             F: int = F_DEFAULT, M: int = M_DEFAULT) -> Scenario:
    if stratum not in STRATA:
        raise ValueError(f"unknown stratum {stratum!r}")
    c_a = STRATA[stratum]
    W = F - M
    total_d = W + kappa
    rng = random.Random(f"seventh-seat/scenario/v1/{seed}/{kappa}")
    for _attempt in range(1000):
        demands = _split(total_d, [rng.uniform(0.7, 1.3) for _ in range(N_DISTRICTS)], 8)
        deficit = sorted(rng.sample(range(N_DISTRICTS), N_DISTRICTS // 2))
        surplus = [i for i in range(N_DISTRICTS) if i not in deficit]
        D = kappa + rng.randint(0, 4)
        gaps = _split(D, [rng.uniform(0.5, 1.5) for _ in deficit], 1)
        extras = _split(D + SURPLUS_MARGIN, [rng.uniform(0.5, 1.5) for _ in surplus], 1)
        if any(g > demands[i] - 4 for g, i in zip(gaps, deficit)):
            continue  # keep every deficit district's entitlement >= 4
        ent = list(demands)
        for g, i in zip(gaps, deficit):
            ent[i] = demands[i] - g
        for e, i in zip(extras, surplus):
            ent[i] = demands[i] + e
        needs = [max(1, min(d, round(d * rng.uniform(0.55, 0.70)))) for d in demands]
        betas = [Fraction(rng.randint(20, 60), 100) for _ in range(N_DISTRICTS)]
        districts = []
        for i in range(N_DISTRICTS):
            d, n = demands[i], needs[i]
            b = c_a * n + (d - n) * (C_R + betas[i] * (c_a - C_R))
            districts.append(District(id=f"D{i + 1}", entitlement=ent[i], demand=d,
                                      min_need=n, budget=math.ceil(b)))
        return Scenario(scenario_id=f"S{seed}-k{kappa}-{stratum}", seed=seed, kappa=kappa,
                        stratum=stratum, F=F, M=M, c_r=C_R, c_a=c_a,
                        districts=tuple(districts))
    raise RuntimeError(f"generator failed for seed {seed}")


def assign_strata(seeds, salt: str = "seventh-seat/strata/v1") -> dict[int, str]:
    """Balanced, seeded assignment of cost strata (E-006): half cheap, half costly."""
    ordered = sorted(seeds)
    random.Random(salt).shuffle(ordered)
    half = (len(ordered) + 1) // 2
    return {s: ("cheap" if k < half else "costly") for k, s in enumerate(ordered)}
