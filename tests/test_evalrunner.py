"""Stage 2 acceptance: the hazard-world runner.

G1 containment and G2 replay rechecked on hazard worlds with the scripted
transport; G6 attention limits; injected transient error recovers; injected
persistent error produces exactly one rerun and then a recorded missing
episode; a budget stop exits cleanly with no unresolved reservations; resume
after an interrupted attempt; the fixed stop refuses new launches; bounded
concurrency; a restarted batch never duplicates a paid call.
"""
import json
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tests import _path  # noqa: F401
from seventh_seat.agents.evalrunner import run_batch, run_episode
from seventh_seat.agents.providers import MODELS, InfrastructureError
from seventh_seat.agents.runtime import Caller, drive
from seventh_seat.agents.storage import Budget, ResponseCache
from seventh_seat.agents.tools import definitions
from seventh_seat.interventions import build_hooks
from seventh_seat.world.engine import Engine
from seventh_seat.world.events import read_jsonl, verify_records
from seventh_seat.world.params import CELLS
from seventh_seat.world.scenario import generate

CAPS = {"total": 4, "preparation": 4, "openai": 2, "anthropic": 2}
TINY = {"total": "0.10", "preparation": "0.10", "openai": "0.10", "anthropic": "0.10"}


def _wire(calls=()):
    return {"id": "resp_r", "model": MODELS["openai"], "status": "completed",
            "output": [{"type": "reasoning", "id": "rs_r", "summary": [],
                        "encrypted_content": "SCRIPTED"}] +
            [{"type": "function_call", "id": f"fc{i}", "call_id": f"c{i}", "name": n,
              "arguments": json.dumps(a)} for i, (n, a) in enumerate(calls)],
            "usage": {"input_tokens": 900, "output_tokens": 60,
                      "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0}}}


def simple_transport(fail_first=0, counter=None):
    """Harmful baseline behaviour: plan and commit heavy river withdrawal."""
    state = {"calls": 0, "fail": fail_first}
    lock = threading.Lock()

    def transport(request):
        with lock:
            state["calls"] += 1
            if counter is not None:
                counter["calls"] += 1
            if state["fail"] > 0:
                state["fail"] -= 1
                raise InfrastructureError("APIConnectionError", None, True)
        last = request["input"][-1]
        if last.get("role") != "user":
            return _wire()
        obs = json.loads(last["content"])
        phase, role = obs["phase"], obs["role"]
        river = min(role["entitlement"], 12)
        if phase == "P2":
            return _wire([("plan", {"river": river, "alt": 0})])
        if phase == "P4":
            return _wire([("commit", {"river": river, "alt": 0})])
        return _wire()
    transport.state = state
    return transport


def g6_transport():
    """Two posts per response in P1, so the fourth action hits the attention cap."""
    def transport(request):
        inp = request["input"]
        user = next(m for m in reversed(inp) if m.get("role") == "user")
        obs = json.loads(user["content"])
        if obs["phase"] == "P1":
            return _wire([("post", {"text": "first"}), ("post", {"text": "second"})])
        return _wire()
    return transport


def dead_transport():
    def transport(request):
        raise InfrastructureError("APIConnectionError", None, True)
    return transport


class RunnerCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.ledger = self.tmp / "ledger.sqlite"

    def factory(self, cache, transport, replay=False):
        def make():
            return Caller("openai", cache, None if replay else Budget(self.ledger, CAPS),
                          None if replay else transport, replay=replay,
                          sleep=lambda x: None, stage="preparation")
        return make

    def run_one(self, ep_dir, seed=2000, condition="E0S0", transport=None, replay=False):
        cache = ResponseCache(self.tmp / "shared-cache")
        return run_episode(ep_dir, generate(seed), condition, "preparation", "openai",
                           self.factory(cache, transport or simple_transport(), replay))


class EpisodeRecoveryTests(RunnerCase):
    def test_completed_episode_manifest_and_breach(self):
        sc = generate(2000)
        manifest, ran = self.run_one(self.tmp / "episodes" / "ep-ok")
        self.assertTrue(ran)
        self.assertEqual(manifest["status"], "completed")
        self.assertEqual(manifest["stage"], "preparation")
        self.assertEqual(manifest["model_configuration"]["reasoning_effort"], "medium")
        self.assertEqual(manifest["model_configuration"]["max_output_tokens"], 4096)
        self.assertEqual(len(manifest["system_hash"]), 64)
        self.assertEqual(len(manifest["tools_hash"]), 64)
        # The scripted policy (river = min(entitlement, 12)) is recomputed here,
        # so the assertion checks the runner's mechanics, not a typed number.
        expected = sum(min(d.entitlement, 12) for d in sc.districts)
        self.assertEqual(manifest["outcome"]["total_withdrawal"], expected)
        self.assertEqual(manifest["outcome"]["breach"], sc.F - expected < sc.M)
        self.assertGreater(manifest["accounted_cost_nanodollars"], 0)
        attempt = manifest["attempts"][0]
        self.assertEqual(attempt["status"], "completed")
        self.assertGreater(attempt["wall_seconds"], 0)
        self.assertIn("valid_action", attempt["call_categories"])
        records = read_jsonl(self.tmp / "episodes" / "ep-ok" / "attempt-0.jsonl")
        self.assertTrue(verify_records(records)[0])

    def test_g1_containment_world_tools_only(self):
        requests = []

        def capture(request):
            requests.append(request)
            return simple_transport()(request)
        self.run_one(self.tmp / "episodes" / "ep-g1", transport=capture)
        world = [d["name"] for d in definitions("E0S0")]
        self.assertTrue(requests)
        for r in requests:
            self.assertEqual([t["name"] for t in r["tools"]], world)
            self.assertTrue(all(t["type"] == "function" for t in r["tools"]))

    def test_g2_cached_replay_byte_identical(self):
        first, _ = self.run_one(self.tmp / "a" / "ep-x")
        second, _ = self.run_one(self.tmp / "b" / "ep-x", replay=True)
        self.assertEqual(second["status"], "completed")
        self.assertEqual((self.tmp / "a" / "ep-x" / "attempt-0.jsonl").read_bytes(),
                         (self.tmp / "b" / "ep-x" / "attempt-0.jsonl").read_bytes())

    def test_g6_attention_limits_hold(self):
        manifest, _ = self.run_one(self.tmp / "episodes" / "ep-g6", transport=g6_transport())
        self.assertEqual(manifest["status"], "completed")
        records = read_jsonl(self.tmp / "episodes" / "ep-g6" / "attempt-0.jsonl")
        posts = [r for r in records if r["action"] == "post"]
        # Six districts x (3 admitted + 1 rejected): the cap is per agent per phase.
        self.assertEqual(sum(1 for r in posts if r["authorized"]), 18)
        rejected = [r for r in posts if not r["authorized"]]
        self.assertEqual(len(rejected), 6)
        self.assertTrue(all("attention budget exhausted" in r["reason"] for r in rejected))

    def test_transient_error_recovers(self):
        manifest, _ = self.run_one(self.tmp / "episodes" / "ep-flaky",
                                   transport=simple_transport(fail_first=2))
        self.assertEqual(manifest["status"], "completed")
        self.assertEqual(len(manifest["attempts"]), 1)           # in-call retries only
        self.assertEqual(manifest["attempts"][0]["call_categories"]["infrastructure_error"], 2)

    def test_persistent_error_one_rerun_then_missing(self):
        manifest, _ = self.run_one(self.tmp / "episodes" / "ep-dead",
                                   transport=dead_transport())
        self.assertEqual(manifest["status"], "missing")          # recorded, reported
        self.assertEqual(len(manifest["attempts"]), 2)           # exactly one rerun
        self.assertEqual([a["status"] for a in manifest["attempts"]],
                         ["infrastructure_error", "infrastructure_error"])
        for a in manifest["attempts"]:
            self.assertTrue((self.tmp / "episodes" / "ep-dead" / a["log"]).exists())
        # 2 episode attempts x 3 provider attempts: every reservation accounted for.
        self.assertEqual(manifest["accounted_cost_nanodollars"],
                         sum(a["accounted_cost_nanodollars"] for a in manifest["attempts"]))
        summary = Budget(self.ledger, CAPS).summary()
        self.assertEqual(summary["unresolved_requests"], 6)      # uncertain, retained
        self.assertGreater(summary["accounted_usd"], 0)

    def test_budget_stop_exits_cleanly(self):
        ledger = self.tmp / "tiny.sqlite"
        cache = self.tmp / "cache-stop"
        work = [{"episode_id": f"ep-{i}", "scenario": generate(2000 + i), "condition": "E0S0"}
                for i in range(2)]
        index = run_batch(work, self.tmp / "run-stop", stage="preparation",
                          ledger_path=ledger, caps=TINY,
                          transport_factory=lambda: simple_transport(), sleep=lambda x: None)
        self.assertEqual(index["episodes"]["ep-0"]["status"], "budget_stop")
        self.assertEqual(index["episodes"]["ep-1"]["status"], "not_launched")
        self.assertEqual(index["halted"], "budget stop")
        self.assertEqual(Budget(ledger, TINY).summary()["unresolved_requests"], 0)


class BatchTests(RunnerCase):
    def work(self, n=4):
        return [{"episode_id": f"ep-{i}", "scenario": generate(2000 + i),
                 "condition": CELLS[i % 4]} for i in range(n)]

    def test_concurrency_resume_and_no_duplicate_paid_calls(self):
        counter = {"calls": 0}
        lock = threading.Lock()

        def factory_transport():
            def counting(request):
                with lock:
                    counter["calls"] += 1
                return simple_transport()(request)
            return counting

        index = run_batch(self.work(), self.tmp / "run", stage="evaluation",
                          ledger_path=self.ledger, caps=CAPS,
                          transport_factory=factory_transport, max_workers=2,
                          sleep=lambda x: None)
        self.assertEqual(index["totals"]["completed"], 4)
        self.assertEqual(index["totals"]["accounted_cost_nanodollars"],
                         sum(e["accounted_cost_nanodollars"] for e in index["episodes"].values()))
        self.assertGreater(counter["calls"], 0)
        for ep in index["episodes"].values():
            self.assertEqual(ep["attempts"], 1)
            log = self.tmp / "run" / ep["dir"] / "attempt-0.jsonl"
            self.assertTrue(verify_records(read_jsonl(log))[0])
        calls_after_first = counter["calls"]
        again = run_batch(self.work(), self.tmp / "run", stage="evaluation",
                          ledger_path=self.ledger, caps=CAPS,
                          transport_factory=factory_transport, max_workers=2,
                          sleep=lambda x: None)
        self.assertTrue(again["resumed"])
        self.assertEqual(counter["calls"], calls_after_first)    # no duplicate paid call
        self.assertTrue(all(e.get("skipped") for e in again["episodes"].values()))

    def test_fixed_stop_refuses_new_launches(self):
        counter = {"calls": 0}

        def factory_transport():
            def counting(request):
                counter["calls"] += 1
                return simple_transport()(request)
            return counting

        stop = datetime.now(timezone.utc) - timedelta(seconds=1)
        index = run_batch(self.work(), self.tmp / "run-stop-time", stage="evaluation",
                          ledger_path=self.ledger, caps=CAPS,
                          transport_factory=factory_transport, stop_at=stop,
                          sleep=lambda x: None)
        self.assertEqual(index["halted"], "fixed stop reached")
        self.assertTrue(all(e["status"] == "not_launched"
                            for e in index["episodes"].values()))
        self.assertEqual(counter["calls"], 0)

    def test_resume_after_interrupted_attempt(self):
        run_dir = self.tmp / "run-resume"
        ep_dir = run_dir / "episodes" / "ep-resume"
        ep_dir.mkdir(parents=True)
        sc = generate(2007)
        engine = Engine(sc, condition="E0S0", episode_id="ep-resume",
                        log_path=ep_dir / "attempt-0.jsonl", **build_hooks("E0S0"))
        cache = ResponseCache(run_dir / "cache")
        with self.assertRaises(InfrastructureError):
            drive(engine, Caller("openai", cache, Budget(self.ledger, CAPS),
                                 dead_transport(), sleep=lambda x: None))
        index = run_batch([{"episode_id": "ep-resume", "scenario": sc, "condition": "E0S0"}],
                          run_dir, stage="preparation", ledger_path=self.ledger, caps=CAPS,
                          transport_factory=lambda: simple_transport(),
                          sleep=lambda x: None)
        entry = index["episodes"]["ep-resume"]
        self.assertEqual(entry["status"], "completed")
        manifest = json.loads((ep_dir / "manifest.json").read_text())
        self.assertEqual([a["status"] for a in manifest["attempts"]],
                         ["interrupted", "completed"])           # interrupted attempt preserved
        self.assertTrue(manifest["attempts"][0]["resumed"])


if __name__ == "__main__":
    unittest.main()
