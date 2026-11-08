import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'deploy/install_experience.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class InstallExperienceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name); (self.base/'releases/old/seventh-seat').mkdir(parents=True)
        (self.base/'current').symlink_to('releases/old')
        self.views = self.base/'views.py'; self.views.write_bytes(b'old route')
        self.old_sha, self.new_sha, self.archive_sha = m.OLD_VIEWS_SHA, m.NEW_VIEWS_SHA, m.ARCHIVE_SHA
        self.addCleanup(self.restore_constants)
        m.OLD_VIEWS_SHA = m.digest(b'old route'); m.NEW_VIEWS_SHA = m.digest(b'new route')
        data = b'unchanged experiment'
        self.entry = {'sha256':m.digest(data), 'bytes':len(data)}
        self.receipt = {'data_status':'experimental','working_tree_clean':True,'files':{'data/a.json':self.entry},'total_bytes':0}
        for _ in range(5):
            blob = (json.dumps(self.receipt)+'\n').encode(); self.receipt['total_bytes']=len(blob)+len(data)
        blob = (json.dumps(self.receipt)+'\n').encode()
        (self.base/'current/seventh-seat/RELEASE.json').write_bytes(blob)
        self.archive = self.base/'site.zip'
        with zipfile.ZipFile(self.archive,'w') as z:
            z.writestr('seventh-seat/RELEASE.json',blob);z.writestr('seventh-seat/data/a.json',data)
        m.ARCHIVE_SHA = m.digest(self.archive.read_bytes());self.reloads=0
    def restore_constants(self):
        m.OLD_VIEWS_SHA, m.NEW_VIEWS_SHA, m.ARCHIVE_SHA = self.old_sha,self.new_sha,self.archive_sha
    def reload(self): self.reloads += 1
    def install(self, verify=lambda *_:None, reload=None):
        return m.install(self.archive,b'new route',self.base,self.views,reload or self.reload,verify)
    def unchanged(self):
        self.assertEqual(self.views.read_bytes(),b'old route');self.assertEqual((self.base/'current').readlink(),Path('releases/old'))
    def test_success_retains_previous(self):
        release=self.install();self.assertEqual(self.views.read_bytes(),b'new route');self.assertEqual(self.reloads,1)
        self.assertEqual((release/'previous-views.py').read_bytes(),b'old route');self.assertTrue((self.base/'releases/old').is_dir())
    def test_bad_archive_rejected_before_mutation(self):
        m.ARCHIVE_SHA='wrong'
        with self.assertRaises(ValueError): self.install()
        self.unchanged();self.assertEqual(self.reloads,0)
    def test_unrelated_route_edits_rejected(self):
        self.views.write_bytes(b'unrelated')
        with self.assertRaises(ValueError):self.install()
        self.assertEqual(self.views.read_bytes(),b'unrelated');self.assertEqual(self.reloads,0)
    def test_changed_science_rejected(self):
        self.receipt['files']['data/a.json']['sha256']='different'
        (self.base/'current/seventh-seat/RELEASE.json').write_text(json.dumps(self.receipt))
        with self.assertRaises(ValueError):self.install()
        self.unchanged();self.assertEqual(self.reloads,0)
    def test_failed_health_check_rolls_back_both(self):
        def fail(*_):raise RuntimeError('HTTP failure')
        with self.assertRaises(RuntimeError):self.install(verify=fail)
        self.unchanged();self.assertEqual(self.reloads,2)
    def test_failed_first_reload_rolls_back_both(self):
        def fail_once():
            self.reload()
            if self.reloads==1:raise RuntimeError('reload failure')
        with self.assertRaises(RuntimeError):self.install(reload=fail_once)
        self.unchanged();self.assertEqual(self.reloads,2)

if __name__=='__main__':unittest.main()
