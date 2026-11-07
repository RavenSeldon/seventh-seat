from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
from copy import deepcopy
import hashlib,json

BASE=Path(__file__).resolve().parent
REF=BASE/'official-template.docx'
DATA=json.loads((BASE/'manuscript.json').read_text())
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}'
with ZipFile(REF) as z:
 parts={n:z.read(n) for n in z.namelist()}
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
 t=E.SubElement(run,W+'t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=text
 return p

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
 for text in paragraphs:body.insert(body.index(sect),paragraph(text))
parts['word/document.xml']=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
out=BASE/'seventh-seat-draft.docx'
with ZipFile(out,'w',ZIP_DEFLATED) as z:
 for name,data in parts.items():z.writestr(name,data)
with ZipFile(REF) as a,ZipFile(out) as b:
 assert a.namelist()==b.namelist()
 assert all(a.read(n)==b.read(n) for n in a.namelist() if n!='word/document.xml')
print(out)
