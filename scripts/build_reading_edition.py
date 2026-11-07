#!/usr/bin/env python3
"""Render the unchanged final manuscript as a house-style web/PDF reading edition."""
import argparse, hashlib, html, json, re
from pathlib import Path

RESEARCH='https://github.com/RavenSeldon/seventh-seat/releases/tag/research-2026-11-07'
PDF='https://github.com/RavenSeldon/seventh-seat/releases/download/reading-2026-11-07/seventh-seat-reading.pdf'
SUBMISSION='https://github.com/RavenSeldon/seventh-seat/releases/download/research-2026-11-07/seventh-seat.pdf'
def rich(s):
    return re.sub(r'https://[^\s<]+', lambda m:f'<a href="{m[0]}">{m[0]}</a>', html.escape(str(s)))

def web(m, source_hash):
    toc=''.join(f'<a href="#s{i}">{html.escape(title)}</a>' for i,(title,_) in enumerate(m['sections']))
    body=[]
    for i,(title,parts) in enumerate(m['sections']):
        body.append(f'<section id="s{i}"><h2>{html.escape(title)}</h2>')
        for p in parts:
            if isinstance(p,str):body.append(f'<p>{rich(p)}</p>')
            else:
                rows=p['table'];body.append('<div class="table-scroll" tabindex="0" role="region" aria-label="'+html.escape(p['caption'])+'"><table><caption>'+html.escape(p['caption'])+'</caption><thead><tr>'+''.join(f'<th scope="col">{html.escape(str(c))}</th>' for c in rows[0])+'</tr></thead><tbody>')
                body.extend('<tr>'+''.join(f'<td>{html.escape(str(c))}</td>' for c in row)+'</tr>' for row in rows[1:]);body.append('</tbody></table></div>')
        body.append('</section>')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="The Seventh Seat: evidence and escalation for an unrepresented downstream party. Complete research paper, methods, results and limitations."><title>The Seventh Seat — The paper</title><style>
:root{color-scheme:dark;--bg:#101115;--panel:#15161c;--ink:#f1f0ed;--muted:#b0b1bb;--cyan:#51dbea;--lavender:#d0bce9;--gold:#e1be83;--line:#383941}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:95px}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.85 Georgia,'Times New Roman',serif}a{color:var(--cyan);text-underline-offset:4px;overflow-wrap:anywhere}a:hover{color:var(--lavender)}a:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--gold);outline-offset:5px}.skip{position:absolute;left:20px;top:-100px;z-index:100;background:var(--bg);padding:12px}.skip:focus{top:8px}.masthead{position:sticky;top:0;z-index:10;background:rgba(16,17,21,.97);border-bottom:1px solid var(--line);font:13px/1.4 Arial,sans-serif}.masthead>div{max-width:1200px;margin:auto;display:flex;justify-content:space-between;gap:24px;padding:10px 32px;align-items:center}.masthead a{display:inline-flex;align-items:center;min-height:44px;text-decoration:none}.brand{color:var(--ink);white-space:nowrap}.masthead nav a{white-space:nowrap}.brand span{display:grid;place-items:center;width:32px;height:32px;border:1px solid var(--lavender);border-radius:50%;flex-shrink:0;font:italic 17px Georgia;color:var(--lavender);margin-right:12px}.masthead nav{display:flex;gap:24px}.layout{max-width:1200px;margin:auto;display:grid;grid-template-columns:220px minmax(0,1fr);gap:65px;padding:60px 32px 80px}aside{position:sticky;top:105px;align-self:start;font:12px/1.5 Arial,sans-serif;border-left:1px solid var(--lavender);padding-left:20px}aside p,.eyebrow{font:11px/1.5 Arial,sans-serif;letter-spacing:.13em;text-transform:uppercase;color:var(--gold)}aside a{display:block;color:var(--muted);text-decoration:none;padding:8px 0}aside a:hover{color:var(--ink)}article{min-width:0;width:100%;max-width:760px}h1,h2,h3{font-family:Arial,Helvetica,sans-serif;font-weight:400}h1{font-size:clamp(44px,6vw,70px);line-height:1.08;letter-spacing:-.04em;margin:25px 0 20px}.subtitle{font:italic 26px/1.4 Georgia,serif;color:var(--lavender);margin-bottom:28px}.author{font:13px/1.8 Arial,sans-serif;color:var(--muted)}.actions{display:flex;flex-wrap:wrap;gap:14px 26px;margin:26px 0 32px;font:13px/1.5 Arial,sans-serif}.actions a{display:flex;min-height:44px;align-items:center}.edition{font:12px/1.8 Arial,sans-serif;color:var(--muted);border-top:1px solid var(--line);padding-top:18px}.abstract{padding:28px 0;border-bottom:1px solid var(--line);margin-bottom:38px}.abstract h2{color:var(--lavender);font-size:20px}.abstract p{font-size:17px}section{padding-top:18px;margin-bottom:30px;scroll-margin-top:90px}h2{color:var(--cyan);font-size:25px;line-height:1.35;margin:18px 0}p{margin:0 0 20px}table{width:100%;border-collapse:collapse;font:13px/1.65 Arial,sans-serif;font-variant-numeric:tabular-nums}th,td{text-align:left;vertical-align:top;padding:12px 10px;border-bottom:1px solid var(--line)}th{color:var(--gold);font-weight:400}caption{caption-side:bottom;text-align:left;color:var(--muted);font-size:12px;padding:14px 0 0}.table-scroll{overflow-x:auto;margin:28px 0 36px}.table-scroll table{min-width:480px}footer{border-top:1px solid var(--line);padding:28px 32px;max-width:1136px;margin:auto;color:var(--muted);font:12px/1.8 Arial,sans-serif}footer a{display:inline-flex;align-items:center;min-height:44px;margin-right:22px}.receipt{font:11px/1.7 monospace;overflow-wrap:anywhere}details.contents{display:none}@media(max-width:900px){.layout{grid-template-columns:1fr;padding:35px 24px 55px;gap:0}aside{display:none}article{margin:auto}details.contents{display:block;font:13px/1.8 Arial,sans-serif;border-block:1px solid var(--line);padding:14px 0;margin:28px 0}summary{cursor:pointer;color:var(--lavender);min-height:30px}details.contents a{display:block;padding:7px 0;color:var(--muted);text-decoration:none}.masthead>div{padding:8px 24px}.masthead nav{gap:18px}.masthead .home{display:none}.subtitle{font-size:23px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{body{color:#111;background:#fff}aside,.masthead,.actions,details.contents,.skip{display:none}.layout{display:block;padding:0}article{max-width:none}h1,h2,.subtitle{color:#111}a{color:#111}section{break-inside:auto}h2{break-after:avoid}table{break-inside:avoid}}
</style></head><body><a class="skip" href="#paper">Skip to the paper</a><div class="masthead"><div><a class="brand" href="../"><span aria-hidden="true">VII</span>The Seventh Seat</a><nav aria-label="Publication"><a href="../">Exhibits</a><a href="'''+RESEARCH+'''">Records ↗</a><a class="home" href="https://benamuwo.com/">Ben Amuwo ↗</a></nav></div></div><div class="layout"><aside aria-label="Paper contents"><p>In this paper</p>'''+toc+'''</aside><article id="paper"><header><p class="eyebrow">Research paper · November 2026</p><h1>'''+html.escape(m['title'])+'''</h1><p class="subtitle">'''+html.escape(m['subtitle'])+'''</p><p class="author">'''+html.escape(m['author'])+'<br>'+html.escape(m['affiliation'])+'''</p><div class="actions"><a href="'''+PDF+'''">Reading PDF ↓</a><a href="'''+SUBMISSION+'''">Original submission PDF ↓</a><a href="'''+RESEARCH+'''">Code &amp; research records ↗</a></div><p class="edition">Reading edition. The manuscript wording and tables are unchanged from the released paper. This layout is designed for the web; the original submission-format copy remains available above.</p></header><details class="contents"><summary>Contents · methods, results &amp; limitations</summary>'''+toc+'''</details><div class="abstract"><h2>Abstract</h2><p>'''+rich(m['abstract'])+'''</p></div>'''+''.join(body)+'''<p class="receipt">Manuscript SHA-256<br>'''+source_hash+'''</p></article></div><footer><p>The Seventh Seat · Benjamin Amuwo · 2026<br>Original paper: CC BY 4.0. Third-party material retains its own terms.</p><a href="../">Back to the exhibits</a><a href="https://benamuwo.me/first-notice/">First Notice ↗</a><a href="https://benamuwo.me/schrodingers_civ/">Schrödinger’s Civilization ↗</a><a href="https://benamuwo.com/">The wider work ↗</a><p>如實 · 道 · 愛 · 不二</p></footer></body></html>'''

def pdf(m, dest, fonts):
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    from reportlab.lib.pagesizes import A4
    for name,file in [('Body','DejaVuSerif.ttf'),('Sans','DejaVuSans.ttf'),('Italic','DejaVuSerif-Italic.ttf')]:pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
    ink=colors.HexColor('#f1f0ed'); muted=colors.HexColor('#b0b1bb'); cyan=colors.HexColor('#51dbea'); lavender=colors.HexColor('#d0bce9'); gold=colors.HexColor('#e1be83');line=colors.HexColor('#383941')
    styles={
      'body':ParagraphStyle('body',fontName='Body',fontSize=10.2,leading=15.6,textColor=ink,spaceAfter=10,splitLongWords=True,allowWidows=0,allowOrphans=0),
      'heading':ParagraphStyle('heading',fontName='Sans',fontSize=17,leading=22,textColor=cyan,spaceBefore=20,spaceAfter=13,keepWithNext=True),
      'title':ParagraphStyle('title',fontName='Sans',fontSize=44,leading=48,textColor=ink,spaceAfter=18),
      'subtitle':ParagraphStyle('subtitle',fontName='Italic',fontSize=19,leading=26,textColor=lavender,spaceAfter=24),
      'small':ParagraphStyle('small',fontName='Sans',fontSize=8,leading=12,textColor=muted,spaceAfter=10),
      'table':ParagraphStyle('table',fontName='Sans',fontSize=8,leading=12,textColor=ink),
      'th':ParagraphStyle('th',fontName='Sans',fontSize=8,leading=12,textColor=gold),
    }
    def para(s,style='body'):
        text=rich(s).replace('<a href=',f'<a color="#51dbea" href=')
        return Paragraph(text,styles[style])
    w,h=A4;cw=w-108
    def page(c,d):
        c.saveState();c.setFillColor(colors.HexColor('#101115'));c.rect(0,0,w,h,stroke=0,fill=1)
        c.setStrokeColor(line);c.setLineWidth(.5);c.line(54,h-45,w-54,h-45);c.line(54,44,w-54,44)
        c.setFont('Sans',7);c.setFillColor(muted);c.drawString(54,h-34,'THE SEVENTH SEAT');c.drawRightString(w-54,h-34,'BENJAMIN AMUWO  /  2026')
        c.drawString(54,30,'READING EDITION  ·  CC BY 4.0');c.setFillColor(gold);c.drawRightString(w-54,30,f'{d.page:02d}');c.restoreState()
    class Doc(SimpleDocTemplate):
        def afterFlowable(self,f):
            if isinstance(f,Paragraph) and f.style.name=='heading':
                name=f'heading-{self.seq.nextf("heading")}';self.canv.bookmarkPage(name);self.canv.addOutlineEntry(f.getPlainText(),name,0,False)
    doc=Doc(str(dest),pagesize=A4,leftMargin=54,rightMargin=54,topMargin=66,bottomMargin=62,title=m['title']+' — Reading edition',author=m['author'],subject=m['subtitle'])
    story=[Spacer(1,15),para('RESEARCH PAPER  /  NOVEMBER 2026','small'),para(m['title'],'title'),para(m['subtitle'],'subtitle'),para(m['author']+' · '+m['affiliation'],'small'),para('Reading edition. Manuscript wording and tables are unchanged from the released paper. The original submission-format PDF remains in the research archive.','small'),para('Abstract','heading'),para(m['abstract'])]
    for title,parts in m['sections']:
        story.append(para(title,'heading'))
        for p in parts:
            if isinstance(p,str):story.append(para(p))
            else:
                rows=[[para(str(c),'th' if i==0 else 'table') for c in row] for i,row in enumerate(p['table'])]
                widths=[cw*x/sum(p['widths']) for x in p['widths']]
                t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
                t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.5,line),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]))
                story.append(KeepTogether([Spacer(1,8),t,Spacer(1,9),para(p['caption'],'small'),Spacer(1,9)]))
    doc.build(story,onFirstPage=page,onLaterPages=page)

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--manuscript',type=Path,required=True);a.add_argument('--html',type=Path,required=True);a.add_argument('--pdf',type=Path);a.add_argument('--fonts',type=Path);x=a.parse_args()
    raw=x.manuscript.read_bytes();m=json.loads(raw);x.html.parent.mkdir(parents=True,exist_ok=True);x.html.write_text(web(m,hashlib.sha256(raw).hexdigest()))
    if x.pdf:
        if not x.fonts:a.error('--fonts required for PDF')
        x.pdf.parent.mkdir(parents=True,exist_ok=True);pdf(m,x.pdf,x.fonts)
