"""Report numbers and interpretation are reconstructed from verified records."""
import importlib.util
import json
from pathlib import Path
import unittest
from tests import test_export_research as fixture

spec=importlib.util.spec_from_file_location('report_results',Path(__file__).resolve().parents[1]/'scripts/report_results.py')
report=importlib.util.module_from_spec(spec);spec.loader.exec_module(report)

class ReportResultsTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixture.ExportTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
        fixture.module.export(self.fx.run,self.fx.out)

    def test_hand_computed_means_contrasts_and_missingness(self):
        data=report.summarize(self.fx.out)
        self.assertEqual(data['complete_scenarios'],1)
        self.assertEqual(data['evaluable_episodes'],7)
        self.assertEqual(data['missing_episodes'],['eval-s7778-E1S1'])
        self.assertEqual(data['contrasts']['shortfall']['E']['estimate'],0)
        for row in data['cells'].values():
            self.assertEqual(row['mean']['shortfall'],2)
            self.assertEqual(row['mean']['breach'],1)
            self.assertEqual(row['mean']['U'],1)
            self.assertEqual(row['mean']['unmet_min_need'],0)
            self.assertEqual(row['mean']['alt_cost'],0)
        self.assertTrue(all(v=='not assessed confirmatorily' for v in data['hypotheses'].values()))

    def test_modified_export_is_rejected(self):
        p=self.fx.out/'index.json';data=json.loads(p.read_text());data['episodes'].pop('eval-s7778-E1S1');p.write_text(json.dumps(data))
        with self.assertRaises(ValueError):report.summarize(self.fx.out)

if __name__=='__main__':unittest.main()
