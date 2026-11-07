"""Release only source-bound exhibit data; enforce offline hosting limits."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from tests import test_export_research as fixture
from tests.test_analysis import fx_scenario,ALL
from seventh_seat.world.engine import Engine
from seventh_seat.interventions import build_hooks
scripts=Path(__file__).resolve().parents[1]/'scripts';sys.path.insert(0,str(scripts))
from export_observatory import export
from build_research_release import build


def representative_fixture(fx):
    ep=fx.run/'s0/episodes/eval-s7777-E0S0'
    eng=Engine(fx_scenario('eval-s7777',7777),condition='E0S0',episode_id=ep.name,log_path=ep/'attempt-0.jsonl',**build_hooks('E0S0'))
    eng.start()
    eng._log('D1','observation',result={'fixture_note':'Recorded view <img src=x onerror=alert(1)>','board':[]})
    eng.submit('D1','post',{'text':'A quoted claim <img src=x onerror=alert(1)> & no inference of belief.'})
    eng.end_phase()
    for actor in ALL:eng.submit(actor,'plan',{'river':12,'alt':0})
    eng.end_phase();eng.submit('D1','read_ledger',{});eng.end_phase()
    for actor in ALL:eng.submit(actor,'commit',{'river':12,'alt':0})
    eng.end_phase()
    m=json.loads((ep/'manifest.json').read_text());m['attempts'][0]['log_head']=eng.log.head
    (ep/'manifest.json').write_text(json.dumps(m))

class ResearchReleaseTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixture.ExportTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
        representative_fixture(self.fx)
        fixture.module.export(self.fx.run,self.fx.out)
        self.data=self.fx.root/'exhibit';export(self.fx.out,self.data,fixture=True)
        self.three=self.fx.root/'three';self.three.mkdir()
        from build_release import THREE_FILES
        for name in THREE_FILES:
            p=self.three/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('// Local test stub; no browser execution.\n')
        (self.three/'package.json').write_text(json.dumps({'version':'0.160.0'}));(self.three/'LICENSE').write_text('Test stub')
        self.output=self.fx.root/'release'

    def test_local_release_keeps_fixture_status_hashes_and_size_budget(self):
        r=build(self.data,self.output,self.three)
        self.assertEqual(r['data_status'],'scripted-fixture')
        self.assertEqual(sum(p.stat().st_size for p in self.output.rglob('*') if p.is_file()),r['total_bytes'])
        self.assertLess(r['first_load']['bytes'],1.5*1024*1024)
        html=(self.output/'seven/index.html').read_text()
        self.assertNotIn('cdn.jsdelivr.net',html)
        self.assertIn('eval-s7777-E0S0',html)
        self.assertNotIn('eval-s7778-E0S0',html)
        self.assertEqual(set(r['files']),{str(p.relative_to(self.output)) for p in self.output.rglob('*') if p.is_file()}-{'RELEASE.json'})

    def test_tampered_exhibit_is_rejected_before_build(self):
        p=self.data/'summary.json';p.write_text(p.read_text()+' ')
        with self.assertRaises(ValueError):build(self.data,self.output,self.three)
        self.assertFalse(self.output.exists())

    def test_symlink_input_is_rejected(self):
        p=self.data/'summary.json';target=self.fx.root/'escaped.json';p.rename(target);p.symlink_to(target)
        with self.assertRaises(ValueError):build(self.data,self.output,self.three)
        self.assertFalse(self.output.exists())

if __name__=='__main__':unittest.main()
