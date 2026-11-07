"""Local release preserves analysis while excluding private runtime material."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from tests import _path
from tests.test_analysis import fx_scenario, write_run_episode, ALL
from seventh_seat.analysis.contrasts import DEFAULT_BOOTSTRAP_SEED
from seventh_seat.experiment import source_hashes
from seventh_seat.world.params import CELLS

spec=importlib.util.spec_from_file_location('export_research',Path(__file__).resolve().parents[1]/'scripts/export_research.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.run=self.root/'run';self.run.mkdir()
        self.out=self.root/'export'
        index={'data_status':'scripted-fixture','episodes':{}}
        for i,cells in enumerate((CELLS,CELLS[:3])):
            block=self.run/f's{i}';sc=fx_scenario(f'eval-s{7777+i}',7777+i)
            for cell in cells:
                eid=write_run_episode(block,sc,cell,{d:12 for d in ALL})
                m=json.loads((block/'episodes'/eid/'manifest.json').read_text())
                index['episodes'][eid]={k:m[k] for k in ('scenario_id','condition','status')}
        index['episodes']['eval-s7778-E1S1']={'scenario_id':'eval-s7778','condition':'E1S1','status':'not_launched','reason':'fixed stop reached'}
        (self.run/'index.json').write_text(json.dumps(index))
        lock={'source_hashes':source_hashes(),'protocol_commit':'a'*40,
              'bootstrap_seed':DEFAULT_BOOTSTRAP_SEED,'bootstrap_resamples':10000,'confirmatory':False,
              'blocks':[{'seed':7777+i,'cells':list(CELLS),'stratum':'cheap'} for i in range(2)]}
        (self.run/'lock.json').write_text(json.dumps(lock))
        (self.run/'provider-cache').mkdir();(self.run/'provider-cache/private.json').write_text('private opaque state')
        (self.run/'.env').write_text('private credential')
        (self.run/'budget.sqlite').write_bytes(b'private budget')

    def test_export_reproduces_complete_and_incomplete_blocks(self):
        receipt=module.export(self.run,self.out)
        self.assertEqual(receipt['evaluation_episodes'],7)
        self.assertEqual(receipt['complete_blocks'],1)
        self.assertFalse((self.out/'.env').exists())
        self.assertFalse((self.out/'budget.sqlite').exists())
        self.assertFalse((self.out/'provider-cache').exists())
        r=json.loads((self.out/'analysis/results.json').read_text())
        self.assertEqual(len(r['blocks']['incomplete_dropped_from_contrasts']),1)
        for name in receipt['files']:
            self.assertEqual((self.run/name).read_bytes(),(self.out/name).read_bytes())

    def test_tampered_records_rejected_before_export(self):
        p=next(self.run.glob('s*/episodes/*/attempt-0.jsonl'))
        p.write_text(p.read_text().replace('season_executed','tampered_season'))
        with self.assertRaises(ValueError):module.export(self.run,self.out)
        self.assertFalse(self.out.exists())

    def test_symlinked_export_input_rejected(self):
        p=self.run/'index.json';outside=self.root/'outside.json';shutil.move(p,outside);p.symlink_to(outside)
        with self.assertRaises(ValueError):module.export(self.run,self.out)
        self.assertFalse(self.out.exists())

    def test_reject_existing_or_nested_destination(self):
        for dest in (self.run,self.run/'nested',self.root):
            with self.assertRaises(ValueError):module.export(self.run,dest)

if __name__=='__main__':unittest.main()
