from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from copy import deepcopy
import hashlib,json,argparse,re

BASE=Path(__file__).resolve().parent
REF=BASE/'official-template.docx'
parser=argparse.ArgumentParser()
parser.add_argument('--data',type=Path,default=BASE/'manuscript.json')
parser.add_argument('--output',type=Path,default=BASE/'seventh-seat-draft.docx')
args=parser.parse_args()
DATA=json.loads(args.data.read_text())
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}'
with ZipFile(REF) as z:
 parts={n:z.read(n) for n in z.namelist()}
REL='http://schemas.openxmlformats.org/package/2006/relationships'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
rels=E.fromstring(parts['word/_rels/document.xml.rels'])
original_relationships=[E.tostring(x) for x in rels]
link_ids={x.get('Target'):x.get('Id') for x in rels if x.get('Type')==R+'/hyperlink'}
def link_id(url):
 if url not in link_ids:
  used={x.get('Id') for x in rels};n=1
  while f'rIdReportLink{n}' in used:n+=1
  rid=f'rIdReportLink{n}'
  E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=R+'/hyperlink',Target=url,TargetMode='External');link_ids[url]=rid
 return link_ids[url]
root=E.fromstring(parts['word/document.xml']);body=root.find('w:body',NS)
paras=body.findall('w:p',NS)
head=next(p for p in paras if ''.join(p.itertext()).find('1. Introduction')>=0)
normal=next(p for p in paras if 'What problem are you addressing' in ''.join(p.itertext()))
# Use actual source paragraph properties, removing guidance italics/list semantics.
def paragraph(text,prototype=normal,style=None,center=False):
 p=deepcopy(prototype)
 props=p.find('w:pPr',NS)
 if props is None:props=E.SubElement(p,W+'pPr')
 for x in list(p):
  if x is not props:p.remove(x)
 for x in list(props):
  if x.tag in (W+'numPr',W+'pageBreakBefore',W+'pBdr'):props.remove(x)
 if style:
  old=props.find('w:pStyle',NS)
  if old is None:old=E.SubElement(props,W+'pStyle')
  old.set(W+'val',style)
 if center:
  old=props.find('w:jc',NS)
  if old is None:old=E.SubElement(props,W+'jc')
  old.set(W+'val','center')
 run=E.SubElement(p,W+'r');rp=E.SubElement(run,W+'rPr')
 fonts=E.SubElement(rp,W+'rFonts')
 for attr in ('ascii','hAnsi','eastAsia','cs'):fonts.set(W+attr,'Old Standard TT')
 for key in ('i','iCs'):
  E.SubElement(rp,W+key).set(W+'val','0')
 if prototype is head:
  E.SubElement(rp,W+'b').set(W+'val','1')
 else:
  E.SubElement(rp,W+'sz').set(W+'val','22')
  E.SubElement(rp,W+'color').set(W+'val','000000')
 p.remove(run)
 def add(parent,value):
  if not value:return
  rr=E.SubElement(parent,W+'r');rr.append(deepcopy(rp));tt=E.SubElement(rr,W+'t');tt.set('{http://www.w3.org/XML/1998/namespace}space','preserve');tt.text=value
 cursor=0
 for match in re.finditer(r'https?://[^\s]+',text):
  url=match.group().rstrip('.,;')
  add(p,text[cursor:match.start()]);h=E.SubElement(p,W+'hyperlink');h.set('{'+R+'}id',link_id(url));add(h,url);cursor=match.start()+len(url)
 add(p,text[cursor:])
 return p

def table(rows,widths):
 t=E.Element(W+'tbl');props=E.SubElement(t,W+'tblPr')
 E.SubElement(props,W+'tblW', {W+'w':str(sum(widths)),W+'type':'dxa'})
 E.SubElement(props,W+'tblLayout',{W+'type':'fixed'})
 borders=E.SubElement(props,W+'tblBorders')
 for edge in ('top','left','bottom','right','insideH','insideV'):
  E.SubElement(borders,W+edge,{W+'val':'single',W+'sz':'4',W+'color':'D6D6D6'})
 margins=E.SubElement(props,W+'tblCellMar')
 for edge in ('top','bottom','left','right'):E.SubElement(margins,W+edge,{W+'w':'90',W+'type':'dxa'})
 grid=E.SubElement(t,W+'tblGrid')
 for width in widths:E.SubElement(grid,W+'gridCol',{W+'w':str(width)})
 for i,row in enumerate(rows):
  if len(row)!=len(widths):raise ValueError('table columns differ')
  tr=E.SubElement(t,W+'tr');rp=E.SubElement(tr,W+'trPr');E.SubElement(rp,W+'cantSplit')
  if i==0:E.SubElement(rp,W+'tblHeader')
  for value,width in zip(row,widths):
   tc=E.SubElement(tr,W+'tc');cp=E.SubElement(tc,W+'tcPr')
   E.SubElement(cp,W+'tcW',{W+'w':str(width),W+'type':'dxa'})
   if i==0:E.SubElement(cp,W+'shd',{W+'fill':'F1F1F1',W+'val':'clear'})
   p=paragraph(str(value))
   if i==0:
    for run in p.findall('w:r',NS):E.SubElement(run.find('w:rPr',NS),W+'b')
   tc.append(p)
 return t

title_table=body.findall('w:tbl',NS)[0]
title_para=next(p for p in title_table.findall('.//w:p',NS) if 'PROJECT TITLE' in ''.join(p.itertext()))
for t in title_para.findall('.//w:t',NS):
 if t.text and 'PROJECT TITLE' in t.text:t.text=t.text.replace('PROJECT TITLE',DATA['title'])
titlecell=title_table.find('w:tr/w:tc',NS)
for p in list(titlecell):
 if p.tag==W+'p' and p is not title_para:titlecell.remove(p)
titlecell.append(paragraph(DATA['subtitle'],center=True))
second=title_table.findall('w:tr',NS)[1].find('w:tc',NS)
for x in list(second):
 if x.tag!=W+'tcPr':second.remove(x)
second.append(paragraph(DATA['author']+' | '+DATA['affiliation'],center=True))
second.append(paragraph('With Apart Research',center=True))
second.append(paragraph('Abstract',head,style='Heading2',center=True))
second.append(paragraph(DATA['abstract']))
# The title standard forbids decorative rules below the title.
for borders in title_table.findall('.//w:tblBorders',NS)+title_table.findall('.//w:tcBorders',NS):
 for x in list(borders):x.set(W+'val','nil')
sect=body.find('w:sectPr',NS)
for x in list(body):
 if x is not title_table and x is not sect:body.remove(x)
# Reuse source section patterns. Insert all blocks before the unchanged sectPr.
for heading,paragraphs in DATA['sections']:
 hp=paragraph(heading,head,style='Heading2')
 if heading=='References':
  E.SubElement(hp.find('w:pPr',NS),W+'pageBreakBefore').set(W+'val','1')
 body.insert(body.index(sect),hp)
 for text in paragraphs:
  if isinstance(text,dict):
   body.insert(body.index(sect),table(text['table'],text['widths']))
   if text.get('caption'):body.insert(body.index(sect),paragraph(text['caption']))
  else:body.insert(body.index(sect),paragraph(text))
parts['word/document.xml']=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
parts['word/_rels/document.xml.rels']=E.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
assert [E.tostring(x) for x in list(rels)[:len(original_relationships)]]==original_relationships
out=args.output
out.parent.mkdir(parents=True,exist_ok=True)
with ZipFile(out,'w',ZIP_DEFLATED) as z:
 for name,data in parts.items():z.writestr(name,data)
with ZipFile(REF) as a,ZipFile(out) as b:
 assert a.namelist()==b.namelist()
 assert all(a.read(n)==b.read(n) for n in a.namelist() if n not in ('word/document.xml','word/_rels/document.xml.rels'))
print(out)
