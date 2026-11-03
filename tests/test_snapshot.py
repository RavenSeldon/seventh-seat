"""Gate G-OBS, contract half (E-011): snapshots balance, missing events error,
fixtures are labelled, and the page embeds exactly what the engine produced."""
import copy
import pathlib
import unittest

from tests import _path  # noqa: F401
from seventh_seat.observatory.snapshot import (SnapshotError, canonical_hash, embed, embedded,
                                               embedded_posters, scripted_fixtures, validate)

PAGE = pathlib.Path(__file__).resolve().parents[1] / "observatory" / "diorama" / "index.html"


class SnapshotContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = scripted_fixtures()

    def test_fixtures_reproduce_the_reference_worlds(self):
        no_trade, trade = self.fixtures
        self.assertEqual(sum(no_trade["withdrawals_by_actor"].values()), 70)
        self.assertEqual(no_trade["downstream_flow"], 30)
        self.assertEqual(sum(trade["withdrawals_by_actor"].values()), 84)
        self.assertEqual(trade["downstream_flow"], 16)

    def test_fixtures_are_labelled_scripted(self):
        for f in self.fixtures:
            self.assertEqual(f["data_status"], "scripted-fixture")

    def test_accounting_must_balance(self):
        bad = copy.deepcopy(self.fixtures[1])
        bad["downstream_flow"] = 30
        with self.assertRaisesRegex(SnapshotError, "accounting does not balance"):
            validate(bad)

    def test_missing_actor_is_an_error_not_zero(self):
        bad = copy.deepcopy(self.fixtures[1])
        del bad["withdrawals_by_actor"]["D3"]
        with self.assertRaisesRegex(SnapshotError, "missing is not zero"):
            validate(bad)

    def test_unexpected_actor_rejected(self):
        bad = copy.deepcopy(self.fixtures[0])
        bad["withdrawals_by_actor"]["D7"] = 0
        with self.assertRaisesRegex(SnapshotError, "unexpected actor"):
            validate(bad)

    def test_unknown_status_rejected(self):
        bad = copy.deepcopy(self.fixtures[0])
        bad["data_status"] = "illustrative"
        with self.assertRaisesRegex(SnapshotError, "data_status"):
            validate(bad)

    def test_experimental_needs_a_verified_manifest(self):
        bad = copy.deepcopy(self.fixtures[1])
        bad["data_status"] = "experimental"
        with self.assertRaisesRegex(SnapshotError, "export manifest"):
            validate(bad)
        bad["provenance"]["manifest_sha256"] = "a" * 64
        validate(bad)

    def test_pre_rendered_frames_match_embedded_snapshots(self):
        html = PAGE.read_text(encoding="utf-8")
        keys = set(embedded_posters(html))
        hashes = {canonical_hash(s) for s in embedded(html)}
        self.assertTrue(keys <= hashes, "a pre-rendered frame belongs to no embedded snapshot")
        for v in embedded_posters(html).values():
            self.assertTrue(v.startswith("data:image/jpeg;base64,"))

    def test_event_refs_required(self):
        bad = copy.deepcopy(self.fixtures[0])
        bad["event_refs"] = []
        with self.assertRaisesRegex(SnapshotError, "event_refs"):
            validate(bad)

    def test_trade_fixture_cites_the_accepted_trades(self):
        self.assertEqual(len(self.fixtures[1]["event_refs"]), 1 + 4)
        self.assertEqual(len(self.fixtures[0]["event_refs"]), 1)

    def test_page_embeds_exactly_the_engine_fixtures(self):
        html = PAGE.read_text(encoding="utf-8")
        self.assertEqual(embedded(html), self.fixtures,
                         "page is stale: run python3 -m seventh_seat.observatory.snapshot")

    def test_embed_refuses_invalid_snapshots(self):
        bad = copy.deepcopy(self.fixtures[0])
        bad["downstream_flow"] += 1
        with self.assertRaises(SnapshotError):
            embed(PAGE.read_text(encoding="utf-8"), [bad])


if __name__ == "__main__":
    unittest.main()
