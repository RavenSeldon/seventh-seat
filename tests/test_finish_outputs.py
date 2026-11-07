"""The unattended finishing step produces private inputs and fails closed."""
import importlib.util
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import unittest
from unittest.mock import patch,Mock
from tests import test_export_research as fixture
from seventh_seat.world.events import canonical

spec=importlib.util.spec_from_file_location('finish_outputs',Path(__file__).resolve().parents[1]/'scripts/finish_outputs.py')
finish=importlib.util.module_from_spec(spec);spec.loader.exec_module(finish)

class FinishTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixture.ExportTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
        self.runs=self.fx.root/'runs';self.runs.mkdir()
        self.fx.run.rename(self.runs/'evaluation-2026-11-06')
        pilot={'data_status':'scripted-fixture','batches':[],'decision':{'status':'outside_target'}}
        (self.runs/'pilot-2026-11-06').mkdir();(self.runs/'pilot-2026-11-06/result.json').write_text(json.dumps(pilot))
        lp=self.runs/'evaluation-2026-11-06/lock.json';lock=json.loads(lp.read_text());lock['calibration_result_sha256']=hashlib.sha256(canonical(pilot).encode()).hexdigest();lp.write_text(json.dumps(lock))
        db=sqlite3.connect(self.runs/'research-budget.sqlite');db.execute('create table charges (provider text,status text,actual integer,reserved integer)');db.execute("insert into charges values ('openai','settled',1000,2000)");db.commit();db.close()

    def invoke(self,state):
        (self.runs/'controller-status.json').write_text(json.dumps({'state':state}))
        with patch.object(finish,'ROOT',self.fx.root),patch.object(sys,'argv',['finish_outputs.py']),patch.object(finish.subprocess,'Popen',return_value=Mock()):return finish.main()

    def test_completed_collector_builds_reproducible_inputs(self):
        self.assertEqual(self.invoke('results_ready'),0)
        status=json.loads((self.runs/'report-output-status.json').read_text())
        self.assertEqual(status['state'],'report_inputs_ready')
        self.assertEqual(status['complete_scenarios'],1)
        self.assertTrue((self.runs/'report-output-2026-11-06/report-tables.md').exists())

    def test_stopped_collector_cannot_publish_ready_status(self):
        self.assertEqual(self.invoke('stopped'),1)
        self.assertEqual(json.loads((self.runs/'report-output-status.json').read_text())['state'],'stopped')
        self.assertFalse((self.runs/'report-output-2026-11-06').exists())

if __name__=='__main__':unittest.main()
