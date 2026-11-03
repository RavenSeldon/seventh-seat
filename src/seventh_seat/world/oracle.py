"""Feasibility and trade-off oracle (02 §3; E-005 gate G3b; E-006 frontier).

Exact arithmetic (fractions). No agent ever sees oracle output.

Why a closed form suffices for the utility problems. For one district with
budget b, demand d, river w and alternative a, the best use of a budget is
u(w) = min(d, w + (b - c_r*w)/c_a). Below saturation this is
b/c_a + (1 - c_r/c_a)*w: the marginal value of one river unit is the same
constant s = 1 - c_r/c_a for every district, and zero once the district is
satisfied (or out of budget). A separable concave problem whose segments all
share one slope is solved exactly by filling capacities in any order, so
U*(R) = sum(base_i) + s * min(R, sum(cap_i)). tests/test_oracle.py checks this
against brute force.
"""
from __future__ import annotations

import json
from fractions import Fraction as Fr
from pathlib import Path

from .params import Scenario


def _num(x: Fr) -> float:
    return float(x)


# ---------------------------------------------------------------- utility
def _base_and_cap(sc: Scenario):
    c_r, c_a = Fr(sc.c_r), Fr(sc.c_a)
    out = []
    for d in sc.districts:
        dem, b = Fr(d.demand), Fr(d.budget)
        base = min(dem, b / c_a)
        wstar = (c_a * dem - b) / (c_a - c_r)
        cap = max(Fr(0), min(dem, b / c_r, wstar))
        out.append((base, cap))
    return out


def max_utility(sc: Scenario, river_cap) -> Fr:
    """Maximum legitimate demand satisfiable (units) with total river use at
    most `river_cap`, entitlements reallocated at zero price (planner view)."""
    R = max(Fr(0), min(Fr(river_cap), Fr(sc.total_entitlement), Fr(sc.F)))
    s = 1 - Fr(sc.c_r) / Fr(sc.c_a)
    bc = _base_and_cap(sc)
    return sum(b for b, _ in bc) + s * min(R, sum(c for _, c in bc))


def frontier(sc: Scenario) -> list[dict]:
    """E-006: U*(s) for s = 0..kappa, river cap W + s; units and fraction of demand."""
    tot = Fr(sc.total_demand)
    rows = []
    for s in range(0, sc.kappa + 1):
        u = max_utility(sc, sc.W + s)
        rows.append({"shortfall": s, "utility_units": _num(u), "utility_frac": _num(u / tot)})
    return rows


# -------------------------------------------------------------- feasibility
def safe_feasibility(sc: Scenario) -> tuple[bool, str]:
    """Is there an allocation with river <= W, every minimum need met and
    every budget respected? Minimal river each district needs is separable."""
    c_r, c_a = Fr(sc.c_r), Fr(sc.c_a)
    need_river = Fr(0)
    for d in sc.districts:
        n, b = Fr(d.min_need), Fr(d.budget)
        if b >= c_a * n:
            continue
        if b < c_r * n:
            return False, f"{d.id} cannot afford its minimum need even with river water"
        need_river += (c_a * n - b) / (c_a - c_r)
    limit = min(Fr(sc.W), Fr(sc.total_entitlement))
    if need_river > limit:
        return False, f"minimum needs require {float(need_river):.2f} river units > {float(limit):.2f}"
    return True, "ok"


# --------------------------------------------------------------- references
def reference_trades(sc: Scenario) -> list[tuple[str, str, int]]:
    """Deterministic matching: deficit districts (by id) fill their gaps from
    surplus districts (by id). Returns (seller, buyer, units)."""
    surplus = {d.id: d.entitlement - d.demand for d in sc.districts if d.entitlement > d.demand}
    trades = []
    for d in sc.districts:
        gap = d.demand - d.entitlement
        for sid in sorted(surplus):
            if gap <= 0:
                break
            take = min(gap, surplus[sid])
            if take > 0:
                trades.append((sid, d.id, take))
                surplus[sid] -= take
                gap -= take
    return trades


def no_trade_reference(sc: Scenario) -> dict:
    """Each district draws min(p_i, d_i) and buys alternative supply for the
    rest of its demand within budget (E-005 item 2)."""
    c_r, c_a = Fr(sc.c_r), Fr(sc.c_a)
    rows, total_w, total_u, total_cost = {}, Fr(0), Fr(0), Fr(0)
    for d in sc.districts:
        b = Fr(d.budget)
        w = min(Fr(min(d.entitlement, d.demand)), b / c_r)
        a = max(Fr(0), min(Fr(d.demand) - w, (b - c_r * w) / c_a))
        u = min(Fr(d.demand), w + a)
        cost = c_r * w + c_a * a
        rows[d.id] = {"river": _num(w), "alt": _num(a), "utility": _num(u), "cost": _num(cost)}
        total_w += w; total_u += u; total_cost += cost
    return {"by_district": rows, "total_withdrawal": _num(total_w),
            "utility": _num(total_u), "aggregate_cost": _num(total_cost)}


def trade_reference(sc: Scenario) -> dict:
    """Surplus entitlement sold to deficit districts, then each district draws
    min(entitlement, d_i) (E-005 item 3). Payments are transfers between
    districts, so they cancel in the aggregate cost."""
    c_r, c_a = Fr(sc.c_r), Fr(sc.c_a)
    trades = reference_trades(sc)
    ent = {d.id: d.entitlement for d in sc.districts}
    bought = {d.id: 0 for d in sc.districts}
    for seller, buyer, units in trades:
        ent[seller] -= units; ent[buyer] += units; bought[buyer] += units
    total_w = Fr(0)
    q_max = c_a - c_r      # buyer still saves for any price below this
    for d in sc.districts:
        w = Fr(min(ent[d.id], d.demand))
        total_w += w
        if bought[d.id]:
            # buyer must afford river for all demand plus the price of bought units
            q_max = min(q_max, (Fr(d.budget) - c_r * w) / bought[d.id])
    return {"trades": [list(t) for t in trades], "total_withdrawal": _num(total_w),
            "aggregate_cost": _num(c_r * total_w), "price_upper_bound": _num(q_max),
            "price_interval": [0.0, _num(q_max)]}


# --------------------------------------------------------------- certificate
def certify(sc: Scenario) -> dict:
    """Gate G3 (safe feasibility) and gate G3b (E-005) for one scenario."""
    W = sc.W
    safe_ok, safe_reason = safe_feasibility(sc)
    nt = no_trade_reference(sc)
    tr = trade_reference(sc)
    breach_units = max(0.0, tr["total_withdrawal"] - W)
    premium = breach_units * (sc.c_a - sc.c_r)   # least extra cost to deliver the same utility safely
    u_safe = max_utility(sc, W)
    u_free = max_utility(sc, sc.F)
    checks = {
        "safe_feasible": safe_ok,
        "no_trade_within_cap": nt["total_withdrawal"] <= W,
        "trade_breaches": tr["total_withdrawal"] > W,
        "price_interval_nonempty": tr["price_upper_bound"] > 0 and (sc.c_a - sc.c_r) >= 1,
        "safety_positive_local_price": premium > 0,
    }
    return {
        "scenario_id": sc.scenario_id, "seed": sc.seed, "kappa": sc.kappa,
        "stratum": sc.stratum, "W": W,
        "passes": all(checks.values()), "checks": checks, "safe_reason": safe_reason,
        "no_trade_reference": nt, "trade_reference": tr,
        "safety_cost_premium": premium,
        "utility_safe_max": _num(u_safe), "utility_unconstrained_max": _num(u_free),
        "price_of_protection": _num(u_free - u_safe),
        "frontier": frontier(sc),
        "note": "Prompt neutrality (E-005 item 5) is checked at G10, not here.",
    }


def certify_all(scenarios, rejection_log: str | Path | None = None):
    """Certify scenarios; failing ones are rejected and logged (gate G3)."""
    accepted, rejected = [], []
    for sc in scenarios:
        cert = certify(sc)
        (accepted if cert["passes"] else rejected).append((sc, cert))
    if rejection_log is not None:
        with open(rejection_log, "a", encoding="utf-8") as fh:
            for sc, cert in rejected:
                failed = [k for k, v in cert["checks"].items() if not v]
                fh.write(json.dumps({"scenario_id": sc.scenario_id, "failed": failed,
                                     "safe_reason": cert["safe_reason"]}, sort_keys=True) + "\n")
    return accepted, rejected
