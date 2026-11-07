"""Post-collection descriptive event census; no hypothesis or source changes."""
import argparse,collections,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
receipt=json.loads((a.run/'EXPORT.json').read_text())
for name,digest in receipt['files'].items():
 if hashlib.sha256((a.run/name).read_bytes()).hexdigest()!=digest: raise ValueError('receipt mismatch: '+name)
counts=collections.Counter();calls=collections.Counter();attempts=collections.Counter();bycell={}
for name in sorted(receipt['files']):
 f=a.run/name
 if f.name=='manifest.json':
  m=json.loads(f.read_text());attempts[len(m['attempts'])]+=1
 if f.suffix=='.jsonl':
  for line in f.read_text().splitlines():
   e=json.loads(line);counts[e['action']]+=1
   bycell.setdefault(e['condition'],collections.Counter())[e['action']]+=1
   if e['action']=='model_call':calls[e['result']['category']]+=1
out={'scope':'Post-collection descriptive census of all exported attempts; absence concerns structured tools, not unstructured prose or internal beliefs.','source_export_receipt_sha256':hashlib.sha256((a.run/'EXPORT.json').read_bytes()).hexdigest(),'attempt_count_distribution':dict(attempts),'event_counts':dict(sorted(counts.items())),'model_call_categories':dict(calls),'event_counts_by_cell':{k:dict(sorted(v.items())) for k,v in sorted(bycell.items())}}
a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='event_counts_by_cell'}))
