"""Factorial contrasts and the scenario-level cluster bootstrap (03 §3).

The unit of analysis is the episode, clustered by scenario; scenarios are the
resampling unit. A contrast is computed only over complete blocks (all four
cells evaluable); incomplete blocks are dropped and listed (03 §7). The
bootstrap uses 10,000 resamples, percentile 95% intervals and a fixed seed,
so one command reproduces every number exactly.
"""
from __future__ import annotations

import random

from ..world.events import sha256_hex
from ..world.params import CELLS

# Default until the evaluation lock fixes it (decision P-7); either way the
# seed is derived from a fixed public string, visibly chosen before data.
DEFAULT_BOOTSTRAP_SEED = int(sha256_hex("seventh-seat/bootstrap/v1")[:16], 16)
RESAMPLES = 10_000


def effect_E(y):
    return (y["E1S0"] + y["E1S1"]) / 2 - (y["E0S0"] + y["E0S1"]) / 2


def effect_S(y):
    return (y["E0S1"] + y["E1S1"]) / 2 - (y["E0S0"] + y["E1S0"]) / 2


def effect_ExS(y):
    return y["E1S1"] - y["E1S0"] - y["E0S1"] + y["E0S0"]


CONTRASTS = {"E": effect_E, "S": effect_S, "ExS": effect_ExS}


def point_estimate(blocks, fn):
    """Mean within-scenario contrast over complete blocks."""
    return sum(fn(b) for b in blocks) / len(blocks) if blocks else None


def _percentile(sorted_values, p):
    """Linear-interpolation percentile (the common default method)."""
    if not sorted_values:
        return None
    rank = p / 100 * (len(sorted_values) - 1)
    low = int(rank)
    if low + 1 >= len(sorted_values):
        return sorted_values[-1]
    frac = rank - low
    return sorted_values[low] + frac * (sorted_values[low + 1] - sorted_values[low])


def bootstrap(scenario_outcomes, resamples=RESAMPLES, seed=DEFAULT_BOOTSTRAP_SEED):
    """Cluster bootstrap over scenarios for every contrast.

    scenario_outcomes: list of dicts {cell: value} for complete blocks.
    Returns {contrast: {"estimate", "ci95": [lo, hi], "blocks": n}}."""
    if type(resamples) is not int or resamples < 1:
        raise ValueError("resamples must be a positive integer")
    if not scenario_outcomes:
        return {name: {"estimate": None, "ci95": [None, None], "blocks": 0}
                for name in CONTRASTS}
    rng = random.Random(seed)
    out = {}
    n = len(scenario_outcomes)
    for name, fn in CONTRASTS.items():
        estimate = point_estimate(scenario_outcomes, fn)
        draws = []
        for _ in range(resamples):
            sample = [scenario_outcomes[rng.randrange(n)] for _ in range(n)]
            draws.append(point_estimate(sample, fn))
        draws.sort()
        out[name] = {"estimate": estimate,
                     "ci95": [_percentile(draws, 2.5), _percentile(draws, 97.5)],
                     "blocks": n}
    return out
