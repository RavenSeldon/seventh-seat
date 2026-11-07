"""A later documentation checkpoint can resume; scientific drift cannot."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
spec=importlib.util.spec_from_file_location('run_experiment',SCRIPTS/'run_experiment.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

class FreezeCheckoutTests(unittest.TestCase):
    def git(self,*args):return subprocess.check_output(['git',*args],cwd=self.root,stderr=subprocess.DEVNULL)
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.git('init');self.git('config','user.email','fixture@example.invalid');self.git('config','user.name','Offline fixture')
        (self.root/'instrument.py').write_text('unchanged scientific instrument\n')
        self.hashes={'instrument.py':hashlib.sha256((self.root/'instrument.py').read_bytes()).hexdigest()}
        self.plan={'source_hashes':self.hashes}
        (self.root/'experiments').mkdir()
        (self.root/'experiments/evaluation-lock.json').write_text(json.dumps(self.plan))
        (self.root/'experiments/research-gates.json').write_text(json.dumps({'G0':'pass'}))
        self.git('add','.');self.git('commit','-m','freeze');self.git('tag','prereg-frozen')

    def test_documentation_descendant_is_allowed(self):
        (self.root/'README.md').write_text('Later reporting checkpoint\n')
        self.git('add','.');self.git('commit','-m','documentation')
        self.assertEqual(runner.verify_frozen_checkout(self.root,self.plan,self.hashes),{'G0':'pass'})

    def test_scientific_or_gate_drift_is_rejected(self):
        with self.assertRaises(ValueError):runner.verify_frozen_checkout(self.root,self.plan,{'instrument.py':'0'*64})
        (self.root/'experiments/research-gates.json').write_text(json.dumps({'G0':'changed'}))
        with self.assertRaises(ValueError):runner.verify_frozen_checkout(self.root,self.plan,self.hashes)

    def test_changed_plan_is_rejected(self):
        with self.assertRaises(ValueError):runner.verify_frozen_checkout(self.root,{**self.plan,'different':True},self.hashes)

if __name__=='__main__':unittest.main()
