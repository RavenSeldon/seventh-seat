"""The end-to-end scripted dry run passes every check and is deterministic."""
from pathlib import Path
import tempfile
import unittest

from tests import _path  # noqa: F401
from seventh_seat import rehearsal


class DryRun(unittest.TestCase):
    def test_passes_and_reproduces(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = rehearsal.run(Path(td) / "a"), rehearsal.run(Path(td) / "b")
            self.assertTrue(a["passed"], {k: v for k, v in a["checks"].items() if not v})
            # Independent runs: identical world-state sequences and outcomes (log bytes differ only
            # by measured call latency; byte identity is the cached-replay check inside the run).
            for k in a["episodes"]:
                self.assertEqual(a["episodes"][k]["state_sequence_sha256"], b["episodes"][k]["state_sequence_sha256"])
                self.assertEqual(a["episodes"][k]["outcome"], b["episodes"][k]["outcome"])
            self.assertEqual(a["episodes"]["reference-trades"]["outcome"]["shortfall"], 14)
            self.assertEqual(a["data_status"], "scripted-fixture")


if __name__ == "__main__":
    unittest.main()
