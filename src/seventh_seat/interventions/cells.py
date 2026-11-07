"""Wire the four E×S cells through the engine's weekend hooks (E-004).

The four cells differ only in ledger content (E) and report routing (S).
The supervisor policy is one shared function in every cell (G8).
"""
from ..world.params import CELLS
from . import ledger, supervisor
from .routing import ReportRouter


def build_hooks(condition):
    """Hook kwargs for Engine(..., **build_hooks(condition))."""
    if condition not in CELLS:
        raise ValueError(f"unknown cell: {condition}")
    evidence, route = condition[:2], condition[2:]
    return {
        "ledger_view": ledger.e1_view if evidence == "E1" else ledger.e0_view,
        "report_router": ReportRouter("direct" if route == "S1" else "endorsed"),
        "end_of_phase": supervisor.end_of_phase,
    }
