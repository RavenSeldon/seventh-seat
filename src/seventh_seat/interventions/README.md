# interventions (WEEKEND, judged)

Verified ledger (E1), direct report route (S1), peer-mediated endorsement path (S0), scripted supervisor. Built Fri 6 Nov.

- `ledger.py` — `read_ledger` content per E-004: E0 register; E1 register plus the VERIFIED projection, phase-stamped, "no plan yet" listed; every result carries its own citable event ID (E-002).
- `routing.py` — `ReportRouter`: S1 direct to the supervisor queue; S0 board proposal, routed on k = 2 other-district endorsements before the commit deadline; self/duplicate endorsements rejected; unrouted proposals logged at the deadline.
- `supervisor.py` — one shared policy (G8): arrival-order processing, verification against the engine's current projection, the qualitative E-001 hold, false alerts with "not verified at this time"; E-001 per-agent information-state log.
- `cells.py` — `build_hooks(condition)`: wires the four cells through the engine's three weekend hooks; only ledger content (E) and routing mode (S) differ.
