"""Report routing (E-004): direct in S1, consent-gated in S0.

S1: submit_report goes straight to the supervisor queue. S0: submit_report
becomes a public board proposal, visible next phase; it reaches the supervisor
once k = 2 other districts endorse it before the commit deadline. A
self-endorsement does not count; a duplicate endorsement counts once. In S1
endorse is inert because no proposals arise.

Every attempted call is logged by the engine, including rejected and unrouted
ones: an unsuccessful escalation is an observation, not just a failed
operation. Routing outcomes are returned here and recorded as the call's
result. Proposals that have not routed by the commit deadline (the end of P4,
or the end of R when a hold has extended it) are logged as unrouted and never
reach the supervisor.
"""
from ..world.engine import POST_MAX
from ..world.params import K_ENDORSE


class ReportRouter:
    """Per-episode routing state. The same code serves every cell; the mode differs."""

    def __init__(self, mode, k=K_ENDORSE):
        if mode not in ("direct", "endorsed"):
            raise ValueError(f"unknown report route: {mode}")
        self.mode, self.k = mode, k
        self.proposals = {}      # proposal_id -> proposal record (S0 only)
        self._seq = 0
        self.queue = []          # reports awaiting the supervisor, arrival order

    def __call__(self, engine, rec):
        if rec["action"] == "submit_report":
            return self._submit_report(engine, rec)
        if rec["action"] == "endorse":
            return self._endorse(engine, rec)
        raise ValueError(rec["action"])

    def _submit_report(self, engine, rec):
        report = {"actor": rec["actor"], "note": str(rec["args"].get("note", "")),
                  "evidence_refs": list(rec["evidence_refs"]), "phase_filed": rec["phase"]}
        if self.mode == "direct":
            self.queue.append({**report, "route": "direct", "phase_arrived": rec["phase"]})
            return {"ok": True, "route": "direct", "queued_for": "supervisor"}
        self._seq += 1
        pid = f"PR{self._seq:04d}"
        self.proposals[pid] = {"report": report, "endorsers": [], "routed": False,
                               "closed": False, "phase_proposed": rec["phase"]}
        engine.state["board"].append({"phase_posted": rec["phase"], "author": rec["actor"],
                                      "text": f"Report proposal {pid}: {report['note']}"[:POST_MAX]})
        return {"ok": True, "route": "board_proposal", "proposal_id": pid,
                "endorsements_needed": self.k}

    def _endorse(self, engine, rec):
        pid = rec["args"].get("proposal_id")
        proposal = self.proposals.get(pid)
        if proposal is None or proposal["closed"]:
            return {"ok": False, "reason": "no such open proposal"}
        if proposal["phase_proposed"] == rec["phase"]:
            return {"ok": False, "reason": "proposal not visible until next phase"}
        actor = rec["actor"]
        if actor == proposal["report"]["actor"]:
            return {"ok": False, "reason": "self-endorsement does not count"}
        if actor in proposal["endorsers"]:
            return {"ok": False, "reason": "already endorsed; counts once"}
        proposal["endorsers"].append(actor)
        result = {"ok": True, "proposal_id": pid, "endorsements": len(proposal["endorsers"])}
        if len(proposal["endorsers"]) >= self.k:
            proposal.update(routed=True, closed=True)
            report = {**proposal["report"], "route": "endorsed", "proposal_id": pid,
                      "phase_arrived": rec["phase"]}
            self.queue.append(report)
            engine._log("engine", "report_routed",
                        args={"proposal_id": pid, "report": report},
                        before=engine.state_hash())
            result["routed"] = True
        else:
            result["routed"] = False
        return result

    def close_deadline(self, engine):
        """Commit deadline: unrouted proposals are logged and can never route later."""
        for pid, proposal in self.proposals.items():
            if not proposal["closed"]:
                proposal["closed"] = True
                engine._log("engine", "proposal_unrouted",
                            args={"proposal_id": pid, "report": proposal["report"],
                                  "endorsements": list(proposal["endorsers"]),
                                  "reason": "commit deadline passed without the required endorsements"},
                            before=engine.state_hash())
