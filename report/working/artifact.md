# Official Apart report template contract

Reference: /Users/theda/Documents/ChatGPT/Seventh Seat/report-work/official-template.docx
SHA256: c29a134bb8fcb73a6da30582a6ea28c77ad2482c337aecd61bdd553d1d7a93ac
Render: template-render/page-1.png through page-5.png, all inspected. One section, US Letter portrait, one-inch margins, single column, no header/footer, original title footnote links to the sprint. The source author grid has six placeholder authors compressed into narrow nested tables; collapse it to the actual one-author layout.

Package inventory: template-package.json. Preserve every part byte-for-byte except word/document.xml. Existing numbering, embedded Old Standard TT fonts, theme, relationships, settings, footnote and footnote URL are retained. There are no TOC or cross-reference fields to refresh. The title footnote is a native footnoteReference and remains intact.

Typography: title style Title, Old Standard TT bold 20 pt centered; main headings are source Heading2 paragraphs with their direct Old Standard TT formatting, with 18 pt before and 6 pt after inherited from style. Subheadings retain source Heading3. Body paragraphs clone source document body p[4] (the first Introduction guidance paragraph): Old Standard TT inherited size, ordinary roman rather than italic guidance. Direct paragraph properties are preserved except list numbering and unwanted page breaks when cloning. No text shrink to fit.

Editable slots: document.xml/body/tbl[1]/tr[1]/tc title; tbl[1]/tr[2]/tc author metadata, Abstract heading and abstract text; remove body/tbl[2] template instructions; body heading/body-paragraph groups Introduction, Related Work, Methods, Results, Discussion and Limitations, Conclusion, Code and Data, Author Contributions, References, Appendix, LLM Usage Statement. Replace guidance text with supported manuscript prose; unused optional author slots are removed. Results and abstract remain visibly pending in the internal draft until verified evaluation output exists. No empirical fixture values may enter the paper.

Flow: compact title/author/abstract on page one, followed by numbered main sections; references and required ethics appendix after main text. Target at most eight main pages. Cloned body paragraphs and source headings may repeat for content capacity. No source section geometry changes. Title-table border rules are removed to meet the document title standard; the retained template still supplies its fonts, title style, section hierarchy, footnote and geometry. This is the sole planned visual style deviation.

Fidelity gates: source SHA unchanged, only documented XML part changes, original footnote/fonts/styles/relationships retained, render every output page and inspect all pages, no clipped tables/text or placeholders in final submission, precise prior-work disclosure and no fabricated results. The internal pending-results draft is not a submission-ready artifact.

Results tables use native fixed-width Word tables inside the unchanged section geometry, with repeated header rows, explicit widths totaling 9360 twips, light cell borders and source body typography. They change only document.xml. The original pending-results manuscript remains separate; assemble_verified_manuscript.py writes a new input file from verified tables. Layout fixtures are visibly labelled and never treated as research findings.

Hyperlink fidelity exception: document.xml.rels gains external relationships for the manuscript citation URLs. Every original relationship is retained in its original order; all other package parts remain byte-identical. The source footnote relationship remains intact. This makes citation URLs clickable in the rendered PDF.
