"""Final allocation rows must agree with act-based secondary outcomes too."""
import json
from pathlib import Path
import sys
import unittest
from tests import test_export_research as fixture
from seventh_seat.world.events import canonical,sha256_hex
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_report_records import audit

class AllocationAuditTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixture.ExportTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)

    def test_direct_arithmetic_reproduces_complete_block_and_preserves_missingness(self):
        fixture.module.export(self.fx.run,self.fx.out)
        r=audit(self.fx.out)
        self.assertEqual(r['allocation_rows_episodes_checked'],7)
        self.assertEqual(r['complete_blocks'],1)
        self.assertEqual(r['data_status'],'scripted-fixture')
        self.assertEqual(r['numeric_cross_checks'],119)

    def test_inconsistent_final_secondary_rows_fail_audit(self):
        # Rebuild a self-consistent hash chain containing an inconsistent final
        # alternative-supply row: the frozen act-based outcomes remain unchanged.
        p=self.fx.run/'s0/episodes/eval-s7777-E0S0/attempt-0.jsonl'
        records=[json.loads(line) for line in p.read_text().splitlines()]
        final=next(r for r in records if r['action']=='season_executed')
        final['result']['by_district']['D1']['alt']=1
        # Use the logger's actual hash schema, with the predecessor included.
        for i,r in enumerate(records):
            if i:r['prev_hash']=records[i-1]['hash']
            r['hash']=sha256_hex(canonical({k:v for k,v in r.items() if k!='hash'}))
        p.write_text(''.join(canonical(r)+'\n' for r in records))
        mp=p.parent/'manifest.json';m=json.loads(mp.read_text());m['attempts'][0]['log_head']=records[-1]['hash'];mp.write_text(json.dumps(m))
        fixture.module.export(self.fx.run,self.fx.out)
        with self.assertRaisesRegex(ValueError,'cross-check failed'):audit(self.fx.out)

if __name__=='__main__':unittest.main()
