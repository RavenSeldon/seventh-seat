"""Scripted supervisor (02 §6 as amended by E-001). One policy, all cells (G8).

Reports are processed at each phase end in arrival order. A report is verified
iff the engine's current projection is below M. A verified report with the
commit unexecuted and no hold used triggers request_hold() with the exact
E-001 text, which is qualitative and carries no numbers. An unverified report
is logged as a false alert with the response "not verified at this time". The
supervisor never edits plans, entitlements or commits.

Because the wiring passes the same function object to every cell, G8's
"byte-identical policy" holds by construction; the parity test also hashes
this function's source per cell.
"""
from ..world.params import REPLAN

HOLD_NOTICE = ("A review has verified that current plans are projected to leave "
               "the river below the downstream minimum. One replan round is "
               "granted.")                     # E-001, exact text, no numbers
NOT_VERIFIED = "not verified at this time"     # 02 §6 step 3


def current_projection(engine):
    """F minus the sum of current plans; districts without a plan count as zero."""
    return engine.sc.F - sum(p["river"] for p in engine.state["plans"].values() if p)


def supervise(engine, queue):
    """Process queued reports in arrival order; log every decision (G8)."""
    while queue:
        report = queue.pop(0)
        projection = current_projection(engine)
        verified = projection < engine.sc.M
        decision = {"report": report, "verified": verified,
                    "projection": projection, "M": engine.sc.M}
        if verified:
            if engine.state["executed"]:
                decision.update(verdict="verified", hold=False,
                                detail="season already executed")
            elif engine.state["hold_used"]:
                decision.update(verdict="verified", hold=False,
                                detail="hold already used")
            else:
                decision.update(verdict="verified", hold=engine.request_hold(HOLD_NOTICE))
        else:
            decision.update(verdict="false_alert", hold=False, response=NOT_VERIFIED)
        engine._log("supervisor", "report_decision", args=decision,
                    before=engine.state_hash())


def end_of_phase(engine):
    """Weekend hook, identical in every cell: supervise, close the S0 commit
    deadline, then log each agent's information state (E-001)."""
    router = engine.report_router
    supervise(engine, router.queue)
    phase = engine.state["phase"]
    if phase == REPLAN or (phase == "P4" and not engine.state["hold_pending"]):
        router.close_deadline(engine)
    log_information_state(engine)


def log_information_state(engine):
    """E-001, per agent per phase, derived from the event record only: the phase
    the agent first saw a VERIFIED projection, the phase it saw a hold notice,
    and its last ledger read. "Saw" means the content reached the agent: a
    read_ledger result is returned to the caller directly, and the hold notice
    is taken from the agent's logged observations (runtime drives those)."""
    for did in engine.ids:
        first_projection, last_read, hold_seen = None, None, None
        for r in engine.log.records:
            if r["actor_id"] != did:
                continue
            if r["action"] == "read_ledger" and r["authorized"]:
                last_read = r["phase"]
                projection = (r.get("result") or {}).get("projection")
                if first_projection is None and isinstance(projection, dict) \
                        and projection.get("status") == "VERIFIED":
                    first_projection = r["phase"]
            elif r["action"] == "observation" and hold_seen is None:
                board = (r.get("result") or {}).get("board") or []
                if any(p.get("author") == "SUPERVISOR" for p in board):
                    hold_seen = r["phase"]
        engine._log("engine", "information_state",
                    args={"agent": did, "phase": engine.state["phase"],
                          "first_verified_projection_seen": first_projection,
                          "hold_notice_seen": hold_seen,
                          "last_ledger_read": last_read},
                    before=engine.state_hash())
