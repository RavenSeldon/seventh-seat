"""Exhibit marks retain exact source provenance and honest fixture labels."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from tests import test_export_research as fixture
from seventh_seat.observatory.snapshot import validate
from seventh_seat.world.events import canonical

scripts=Path(__file__).resolve().parents[1]/'scripts';sys.path.insert(0,str(scripts))
spec=importlib.util.spec_from_file_location('export_observatory',scripts/'export_observatory.py')
exhibit=importlib.util.module_from_spec(spec);spec.loader.exec_module(exhibit)

class ExhibitExportTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixture.ExportTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
        # First locked scenario is incomplete. Witness selection must skip it,
        # using completeness/order rather than looking for a dramatic outcome.
        p=self.fx.run/'lock.json';data=json.loads(p.read_text());data['blocks'].reverse();p.write_text(json.dumps(data))
        fixture.module.export(self.fx.run,self.fx.out)
        self.output=self.fx.root/'exhibit'

    def test_exact_truth_provenance_and_complete_scenario_selection(self):
        receipt=exhibit.export(self.fx.out,self.output,fixture=True)
        self.assertEqual(receipt['snapshots'],7);self.assertEqual(receipt['witness_episodes'],4)
        manifest=json.loads((self.output/'manifest.json').read_text())
        digest=hashlib.sha256((self.output/'manifest.json').read_bytes()).hexdigest()
        for snap in json.loads((self.output/'snapshots.json').read_text()):
            validate(snap);self.assertEqual(snap['data_status'],'scripted-fixture')
            self.assertEqual(snap['downstream_flow'],28)
            self.assertEqual(sum(snap['withdrawals_by_actor'].values()),72)
            self.assertEqual(snap['provenance']['manifest_sha256'],digest)
            core={k:v for k,v in snap.items() if k!='provenance'}
            self.assertEqual(hashlib.sha256(canonical(core).encode()).hexdigest(),manifest['episodes'][snap['episode_id']]['snapshot_core_sha256'])
        summary=json.loads((self.output/'summary.json').read_text())
        self.assertEqual(summary['witness_seed'],7777)
        self.assertEqual(summary['mean_shortfall_intervals_descriptive']['E0S0'],{'mean':2,'ci95':[2,2],'n':1})
        self.assertEqual(summary['missing_episodes'],['eval-s7778-E1S1'])
        self.assertNotIn('cache',receipt['files'])

    def test_fixture_cannot_be_exported_as_experimental(self):
        with self.assertRaises(ValueError):exhibit.export(self.fx.out,self.output)
        self.assertFalse(self.output.exists())

    def test_modified_source_receipt_fails_closed(self):
        p=self.fx.out/'index.json';p.write_text(p.read_text()+' ')
        with self.assertRaises(ValueError):exhibit.export(self.fx.out,self.output,fixture=True)
        self.assertFalse(self.output.exists())

if __name__=='__main__':unittest.main()
