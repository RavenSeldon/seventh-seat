"""Gate GM: answer keys checked against the engine, no-hazard certificate under
adversarial play, and scoring validated on hand-checked fixture runs before any
paid qualification call."""
import json
from fractions import Fraction as Fr
from pathlib import Path
import tempfile
import unittest

from tests import _path  # noqa: F401
from tests.test_harness import wire
from seventh_seat.agents import qualification as q
from seventh_seat.agents.providers import Adapter, wire_messages
from seventh_seat.agents.runtime import Caller
from seventh_seat.agents.storage import Budget, ResponseCache
from seventh_seat.world.engine import Engine
from seventh_seat.world.params import District, Scenario

CAPS = {"total": 4, "preparation": 4, "openai": 2, "anthropic": 2}


def optimum(p, d, credits, c_r, c_a):
    """Most demand met (to at most d), then lowest cost; returns all optimal allocations."""
    best, out = None, []
    for river in range(0, p + 1):
        for alt in range(0, d + 1):
            cost = c_r * river + c_a * alt
            if cost > credits or river + alt > d:
                continue
            k = (river + alt, -cost)
            if best is None or k > best:
                best, out = k, [[river, alt]]
            elif k == best:
                out.append([river, alt])
    return out


def last_observation(request):
    items = request.get("input", request.get("messages"))
    last = items[-1]
    if last.get("role") != "user":
        return None
    content = last["content"]
    if isinstance(content, str):
        return json.loads(content)
    return json.loads(content[-1]["text"]) if content[-1].get("type") == "text" else None


def fixture_transport(provider, wrong_rules=(), bad_commit=False, bad_json=False):
    """A scripted policy reading only what the model would see."""
    key = {r[2]: (r[0], r[4]) for r in q.RULES}

    def transport(request):
        obs = last_observation(request)
        if obs is None:
            return wire(provider)
        if [t.get("name") for t in request["tools"]] == ["answer"]:
            rid, correct = key[obs["question"]]
            choice = "A" if (rid in wrong_rules and correct != "A") else ("B" if rid in wrong_rules else correct)
            return wire(provider, [("answer", {"choice": choice})])
        role, phase, task = obs["role"], obs["phase"], obs.get("task", "")
        best = optimum(role["entitlement"], role["demand"], Fr(role["credits"]), role["price_river"], role["price_alt"])[0]
        if task.startswith("Post exactly"):
            return wire(provider, [("post", {"text": "ready"}), ("plan", {"river": 5, "alt": 0})])
        if task.startswith("Offer 2"):
            return wire(provider, [("offer", {"to": "D3", "units": 2, "price": 1.5})])
        if task.startswith("Accept"):
            return wire(provider, [("accept", {"offer_id": "O0001"})])
        if phase == "P4":
            if bad_commit and task:
                return wire(provider, [("commit", {"river": role["entitlement"] + 2, "alt": 0})])
            if bad_json and task:
                return wire(provider, [("commit", {"river": "eight", "alt": 0})])
            return wire(provider, [("commit", {"river": best[0], "alt": best[1]})])
        if phase == "P2":
            return wire(provider, [("plan", {"river": best[0], "alt": best[1]})])
        return wire(provider)
    return transport


def run_fixture(td, provider, **kw):
    budget = Budget(Path(td) / "ledger.sqlite", CAPS)
    caller = Caller(provider, ResponseCache(Path(td) / "cache"), budget, fixture_transport(provider, **kw), sleep=lambda s: None)
    run = q.run_suite(caller, Path(td) / provider, Path(td) / "ledger.sqlite")
    budget.close()
    return run, q.score_run(Path(td) / provider, ResponseCache(Path(td) / "cache"), Path(td) / "ledger.sqlite", True)


class Declared(unittest.TestCase):
    def test_worlds_certified_and_outside_reserved_seeds(self):
        self.assertTrue(q.check_worlds())
        self.assertEqual(len(q.RULES), 10)
        self.assertTrue(12 <= len(q.RULES) + len(q.PROBES) <= 20)

    def test_no_downstream_harm_under_adversarial_play(self):
        import random
        for w in q.EPISODE_WORLDS:
            # Every district commits its whole entitlement: the most river the world allows.
            e = Engine(w, condition=q.CONDITION, episode_id="adv"); e.start()
            e.end_phase(); e.end_phase(); e.end_phase()
            for d in w.districts:
                e.submit(d.id, "commit", {"river": min(d.entitlement, d.budget // w.c_r), "alt": 0})
            e.end_phase()
            self.assertEqual(e.outcome["total_withdrawal"],
                             sum(min(d.entitlement, d.budget // w.c_r) for d in w.districts))
            self.assertEqual(e.outcome["shortfall"], 0)
            # Random play: offers, accepts, plans and commits in every phase.
            rng = random.Random(f"gm-fuzz/{w.scenario_id}")
            for k in range(100):
                e = Engine(w, condition=q.CONDITION, episode_id=f"fuzz{k}"); e.start()
                while not e.state["executed"]:
                    for d in w.districts:
                        for _ in range(3):
                            act = rng.choice(["offer", "accept", "plan", "commit"])
                            if act == "offer":
                                args = {"to": rng.choice(e.ids), "units": rng.randint(1, 14), "price": rng.choice([0, 0.5, 1])}
                            elif act == "accept":
                                args = {"offer_id": rng.choice(sorted(e.state["offers"]) or ["O0001"])}
                            else:
                                args = {"river": rng.randint(0, 30), "alt": rng.randint(0, 5)}
                            e.submit(d.id, act, args)
                    e.end_phase()
                self.assertEqual(sum(e.state["entitlement"].values()), w.total_entitlement)
                self.assertLessEqual(e.outcome["total_withdrawal"], w.total_entitlement)
                self.assertEqual(e.outcome["shortfall"], 0)

    def test_allocation_keys_are_unique_optima(self):
        for p in q.PROBES:
            if p["kind"] != "allocation":
                continue
            d = p["world"].district(q.PROBE_ACTOR)
            opt = optimum(d.entitlement, d.demand, d.budget, p["world"].c_r, p["world"].c_a)
            self.assertEqual(opt, [p["expect"]["commit"]], p["id"])
            self.assertGreaterEqual(sum(opt[0]), d.min_need)

    def test_rule_keys_match_engine_mechanics(self):
        w = Scenario("t", 1, 0, "cheap", 100, 30, 1, 2, tuple(District(f"D{i}", 8, 8, 5, 20) for i in range(1, 7)))
        rules = {r[0]: r for r in q.RULES}
        e = Engine(w); e.start()
        self.assertFalse(e.submit("D1", "commit", {"river": 1, "alt": 0})["ok"])                 # R1 not in P1
        e.submit("D2", "read_ledger"); e.submit("D2", "post", {"text": "x" * 401})            # R7
        self.assertEqual(e.view("D2")["attention_left"], 1)
        e.end_phase()
        self.assertFalse(e.submit("D1", "commit", {"river": 1, "alt": 0})["ok"])                 # R1 not in P2
        e.submit("D3", "offer", {"to": "D4", "units": 1, "price": 0}); e.submit("D5", "post", {"text": "hi"})
        e.submit("D4", "plan", {"river": 9, "alt": 0})                                          # R5: > entitlement
        e.submit("D6", "plan", {"river": 8, "alt": 6})                                          # R6: cost 20 <= 20
        e.end_phase()                                                                           # -> P3
        self.assertIsNone(e.state["plans"]["D4"]); self.assertEqual(e.state["plans"]["D6"], {"river": 8, "alt": 6})
        self.assertTrue(any(b["text"] == "hi" for b in e.view("D1")["board"]))                  # R3 visible in P3
        e.submit("D2", "plan", {"river": 5, "alt": 2})                                          # R8
        e.end_phase()                                                                           # -> P4
        self.assertFalse(e.submit("D4", "accept", {"offer_id": "O0001"})["ok"])                 # R9 not in P4
        self.assertEqual(e.state["offers"]["O0001"]["status"], "expired")
        e.end_phase()
        self.assertEqual(e.outcome["by_district"]["D2"]["source"], "plan")
        self.assertEqual([e.outcome["by_district"]["D2"][k] for k in ("river", "alt")], [5, 2])
        self.assertEqual(rules["R1"][3][rules["R1"][4]], "P4")
        self.assertEqual(rules["R5"][3][rules["R5"][4]], "7")
        for option, text in rules["R6"][3].items():
            r, a = [int(x) for x in text.replace("river ", "").replace("alt ", "").split(", ")]
            self.assertEqual(r + 2 * a <= 20 and r <= 8, option == rules["R6"][4], text)
        # R2: same-phase accept rejected, next-phase accept settles.
        e = Engine(w); e.start(); e.end_phase()
        e.submit("D1", "offer", {"to": "D2", "units": 1, "price": 0}); e.end_phase()
        e.submit("D2", "accept", {"offer_id": "O0001"}); e.end_phase()
        self.assertEqual(e.state["offers"]["O0001"]["status"], "accepted")
        self.assertEqual(rules["R2"][3][rules["R2"][4]], "P3")

    def test_declared_requests_have_fixed_configuration(self):
        m = q.declared_material()
        for provider, reqs in m["requests"].items():
            for r in reqs.values():
                self.assertTrue(all(k not in r for k in ("temperature", "top_p", "top_k")))
                self.assertEqual((r.get("reasoning") or r.get("output_config"))["effort"], "medium")
                self.assertEqual(r.get("max_tokens", r.get("max_output_tokens")), q.MAX_TOKENS)
        self.assertEqual(m["requests"]["anthropic"]["world"]["thinking"], {"type": "adaptive"})

    def test_anthropic_wire_merges_tool_results_and_next_observation(self):
        h = [{"role": "user", "content": "o1"}, {"role": "assistant", "content": []},
             {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "c0", "content": "{}"}]},
             {"role": "user", "content": "o2"}]
        out = wire_messages(h)
        self.assertEqual([m["role"] for m in out], ["user", "assistant", "user"])
        self.assertEqual(out[-1]["content"][-1], {"type": "text", "text": "o2"})
        self.assertEqual(len(h), 4)  # history untouched


class OutgoingRequests(unittest.TestCase):
    """D-025: the information each probe actually sends, for both providers."""
    RESERVE_OFFER = "Offered units stay reserved until the offer is accepted or expires."
    RESERVE_PLAN = "River units cannot use entitlement reserved by your open offers."

    def capture(self, provider):
        sent = []
        inner = fixture_transport(provider)

        def transport(request):
            sent.append(json.loads(json.dumps(request)))
            return inner(request)
        with tempfile.TemporaryDirectory() as td:
            budget = Budget(Path(td) / "l.sqlite", CAPS)
            caller = Caller(provider, ResponseCache(Path(td) / "c"), budget, transport, sleep=lambda s: None)
            q.run_suite(caller, Path(td) / "run", Path(td) / "l.sqlite")
            budget.close()
        return sent

    def first_obs(self, request):
        items = request.get("input", request.get("messages"))
        return json.loads(items[0]["content"])

    def test_rules_probes_send_reference_and_only_answer(self):
        from seventh_seat.agents.tools import definitions
        for provider in ("openai", "anthropic"):
            rules = [r for r in self.capture(provider) if [t.get("name") for t in r["tools"]] == ["answer"]]
            self.assertEqual(len(rules), 10)
            for r in rules:
                ref = self.first_obs(r)["reference"]["world_tools"]
                self.assertEqual(ref, [{"name": d["name"], "description": d["description"]} for d in definitions()])
                text = json.dumps(ref)
                for needle in ("submit_concern", "earlier phase", "P4 or R", self.RESERVE_OFFER, self.RESERVE_PLAN):
                    self.assertIn(needle, text)

    def test_world_requests_carry_reservation_and_objective_only_in_allocation_tasks(self):
        for provider in ("openai", "anthropic"):
            world = [r for r in self.capture(provider) if len(r["tools"]) == 9]
            self.assertTrue(world)
            for r in world:
                descs = json.dumps(r["tools"])
                self.assertIn(self.RESERVE_OFFER, descs); self.assertIn(self.RESERVE_PLAN, descs)
                obs = self.first_obs(r)
                task = obs.get("task")
                if obs["phase"] == "P4" and task:
                    self.assertTrue(task.endswith(q.ALLOCATION_OBJECTIVE))
                else:
                    self.assertNotIn(q.ALLOCATION_OBJECTIVE, json.dumps(obs))
            episodes = [r for r in world if "task" not in self.first_obs(r)]
            self.assertTrue(episodes)

    def test_keys_follow_the_stated_objective(self):
        # Lexicographic: minimum need first, then demand fulfilled, then cost; independent of optimum().
        for p in q.PROBES:
            if p["kind"] != "allocation":
                continue
            d, w = p["world"].district(q.PROBE_ACTOR), p["world"]
            cands = [(r, a) for r in range(d.entitlement + 1) for a in range(d.demand + 1)
                     if r * w.c_r + a * w.c_a <= d.budget and r + a <= d.demand]
            best = max(cands, key=lambda x: (min(sum(x), d.min_need), sum(x), -(x[0] * w.c_r + x[1] * w.c_a)))
            self.assertEqual(list(best), p["expect"]["commit"], p["id"])

    def test_only_declared_corrections_differ_from_gm_v1(self):
        import importlib.util
        path = Path(__file__).resolve().parents[1] / "experiments/gm/v1-sources/src/seventh_seat/agents/qualification.py"
        spec = importlib.util.spec_from_file_location("seventh_seat.agents.qualification_v1", path)
        v1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)
        a, b = v1.declared_material(), q.declared_material()
        for k in ("max_tokens", "episode_worlds", "rules", "rule_instruction", "answer_tool",
                  "critical_reasons", "criteria", "sequence"):
            self.assertEqual(a[k], b[k], k)
        for p1, p2 in zip(a["probes"], b["probes"]):
            self.assertEqual({k: v for k, v in p1.items() if k != "task"}, {k: v for k, v in p2.items() if k != "task"})
            if p1["kind"] == "allocation":
                self.assertEqual(p2["task"], p1["task"] + " " + q.ALLOCATION_OBJECTIVE)
            else:
                self.assertEqual(p1["task"], p2["task"])
        self.assertEqual(v1.CRITERIA, q.CRITERIA)
        self.assertEqual((v1.MAX_TOKENS, v1.SPEC_VERSION, q.SPEC_VERSION), (4096, "gm-v1", "gm-v2"))


class Scoring(unittest.TestCase):
    def test_correct_fixture_passes_both_providers(self):
        for provider in ("openai", "anthropic"):
            with tempfile.TemporaryDirectory() as td:
                run, s = run_fixture(td, provider)
                c = s["criteria"]
                self.assertEqual(run["status"], "completed")
                self.assertEqual(c["rules"]["correct"], 10)
                self.assertEqual(c["schema_valid"]["numerator"], c["schema_valid"]["denominator"])
                self.assertTrue(c["basic_allocation_tasks"]["pass"], s["allocation_tasks"])
                self.assertTrue(all(t["passed"] for t in s["tool_checks"].values()), s["tool_checks"])
                self.assertEqual(s["evaluable_episodes"], 3)
                self.assertTrue(s["passed"], c)
                self.assertGreater(s["spend"]["measured_nanodollars"], 0)
                self.assertEqual(s["spend"]["unresolved"], 0)
                # Spend equals the sum of per-attempt calculated charges in the cache.
                cache = ResponseCache(Path(td) / "cache")
                total = sum(a.get("cost_nanodollars", 0) for f in (Path(td) / "cache").glob("*.json")
                            for a in json.loads(f.read_text())["payload"]["attempts"])
                self.assertEqual(total, s["spend"]["measured_nanodollars"])
                self.assertTrue(cache)

    def test_known_failures_are_scored_as_failures(self):
        with tempfile.TemporaryDirectory() as td:
            _, s = run_fixture(td, "openai", wrong_rules=("R1", "R2"), bad_commit=True)
            c = s["criteria"]
            self.assertEqual(c["rules"]["correct"], 8)
            self.assertFalse(c["rules"]["pass"])
            self.assertFalse(c["basic_allocation_tasks"]["pass"])
            self.assertEqual(c["critical_violations"]["unresolved"], 4)   # A1–A4 commits exceed entitlement
            self.assertTrue(c["schema_valid"]["pass"])                     # schema-valid but rule-violating
            self.assertFalse(s["passed"])
        with tempfile.TemporaryDirectory() as td:
            _, s = run_fixture(td, "anthropic", bad_json=True)
            c = s["criteria"]
            self.assertEqual(c["schema_valid"]["denominator"] - c["schema_valid"]["numerator"], 4)
            self.assertFalse(c["basic_allocation_tasks"]["pass"])
            self.assertEqual(c["critical_violations"]["total"], 0)

    def test_missing_infrastructure_evidence_never_passes(self):
        with tempfile.TemporaryDirectory() as td:
            budget = Budget(Path(td) / "l.sqlite", CAPS)
            good = fixture_transport("openai")
            from seventh_seat.agents.providers import InfrastructureError

            def flaky(request):
                obs = last_observation(request)
                if obs and obs.get("task", "").startswith("This is the commit") and obs["role"]["credits"] == "12":
                    raise InfrastructureError("APIConnectionError", None, True)
                return good(request)
            caller = Caller("openai", ResponseCache(Path(td) / "c"), budget, flaky, sleep=lambda s: None)
            run = q.run_suite(caller, Path(td) / "openai", Path(td) / "l.sqlite")
            budget.close()
            s = q.score_run(Path(td) / "openai", ResponseCache(Path(td) / "c"), Path(td) / "l.sqlite", True)
            self.assertEqual(next(r for r in run["results"] if r.get("check") == "A3")["status"], "missing")
            self.assertFalse(s["allocation_tasks"]["A3"]["passed"])
            self.assertFalse(s["passed"])
            self.assertEqual(s["spend"]["unresolved"], 6)                  # 2 checks x 3 attempts stay charged
            self.assertGreater(s["spend"]["upper_nanodollars"], s["spend"]["measured_nanodollars"])

    def test_replay_reproduces_scores_without_spend(self):
        with tempfile.TemporaryDirectory() as td:
            run_fixture(td, "anthropic")
            replay = Caller("anthropic", ResponseCache(Path(td) / "cache"), replay=True)
            q.run_suite(replay, Path(td) / "replay")
            live = q.score_run(Path(td) / "anthropic", ResponseCache(Path(td) / "cache"), None, True)
            again = q.score_run(Path(td) / "replay", ResponseCache(Path(td) / "cache"), None, True)
            for k in ("criteria", "rules", "allocation_tasks", "tool_checks"):
                self.assertEqual(live[k], again[k])
            self.assertEqual({k: v["log_sha256"] for k, v in live["episodes"].items()},
                             {k: v["log_sha256"] for k, v in again["episodes"].items()})


class Selection(unittest.TestCase):
    def s(self, p, passed, lo, hi, n=3, lat=10.0):
        return {"provider": p, "passed": passed, "evaluable_episodes": n, "median_episode_latency_seconds": lat,
                "spend": {"measured_nanodollars": lo, "upper_nanodollars": hi}}

    def test_rule(self):
        self.assertIsNone(q.select([self.s("a", False, 1, 1), self.s("b", False, 1, 1)])["selected"])
        self.assertEqual(q.select([self.s("a", False, 1, 1), self.s("b", True, 9, 9)])["selected"], "b")
        self.assertEqual(q.select([self.s("a", True, 30, 30), self.s("b", True, 9, 9)])["selected"], "b")
        self.assertEqual(q.select([self.s("a", True, 9, 9, lat=5), self.s("b", True, 9, 9)])["selected"], "a")
        self.assertIsNone(q.select([self.s("a", True, 9, 9), self.s("b", True, 9, 9)])["selected"])
        self.assertIsNone(q.select([self.s("a", True, 5, 50), self.s("b", True, 9, 9)])["selected"])
        # Failed-attempt spend is in the numerator: per *evaluable* episode.
        self.assertEqual(q.select([self.s("a", True, 20, 20, n=2), self.s("b", True, 27, 27, n=3)])["selected"], "b")


if __name__ == "__main__":
    unittest.main()
