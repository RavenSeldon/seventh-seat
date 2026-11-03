"""Scripted agents for gate tests. These are FIXTURES (data_status:
scripted-fixture under E-011), never experimental subjects."""
from __future__ import annotations

from ..world.engine import Engine
from ..world.oracle import reference_trades


def run_episode(engine: Engine, policy) -> dict:
    """Drive every phase: policy(engine, district_id, phase) -> list of (action, args)."""
    engine.start()
    while not engine.state["executed"]:
        phase = engine.state["phase"]
        for did in engine.ids:
            for action, args in policy(engine, did, phase):
                engine.submit(did, action, args)
        engine.end_phase()
    return engine.outcome


def no_trade_policy(engine: Engine, did: str, phase: str):
    """Draw min(entitlement, demand); buy alternative supply for the rest within credits."""
    if phase not in ("P2", "P4"):
        return []
    sc = engine.sc
    d = sc.district(did)
    w = min(engine.state["entitlement"][did], d.demand)
    credits = engine._credits(did)
    a = int(min(d.demand - w, (credits - sc.c_r * w) // sc.c_a))
    return [("plan" if phase == "P2" else "commit", {"river": w, "alt": max(0, a)})]


def make_trade_policy(price: str = "0.5"):
    """The E-005 trade reference, played out through the engine."""
    def policy(engine: Engine, did: str, phase: str):
        trades = reference_trades(engine.sc)
        d = engine.sc.district(did)
        if phase == "P1":
            return [("offer", {"to": b, "units": u, "price": price}) for s, b, u in trades if s == did]
        if phase == "P2":
            return [("accept", {"offer_id": o["offer_id"]}) for o in engine.view(did)["offers_to_me"]]
        if phase in ("P3", "P4"):
            w = min(engine.state["entitlement"][did], d.demand)
            return [("plan" if phase == "P3" else "commit", {"river": w, "alt": 0})]
        return []
    return policy
