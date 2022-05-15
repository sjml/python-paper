from docx import Document
from docx import enum
from docx.shared import Pt


def package(filename: str, meta: dict):
    doc = Document(filename)

    if len(doc.paragraphs) == 0:
        doc.add_paragraph("", style="First Paragraph")

    starting_graph = doc.paragraphs[0]
    starting_graph.paragraph_format.page_break_before = True

    starting_graph.insert_paragraph_before(meta["data"]["title"], style="Title")
    starting_graph.insert_paragraph_before("by", style="Author")
    starting_graph.insert_paragraph_before(meta["data"]["author"], style="Author")
    starting_graph.insert_paragraph_before(f"{meta['professor']}\n{meta['class_mnemonic']} — {meta['class_name']}\n{meta['data']['date']}", style="Author")

    last_graph_idx = -1
    while True:
        last_graph = doc.paragraphs[last_graph_idx]
        if "Bibliography" not in last_graph.style.style_id:
            break
        last_graph_idx -= 1

    bib_start = doc.paragraphs[last_graph_idx+1]
    if "Bibliography" in bib_start.style.style_id:
        bib_label = bib_start.insert_paragraph_before("Works Cited")
        bib_label.paragraph_format.alignment = enum.text.WD_ALIGN_PARAGRAPH.CENTER
        bib_label.paragraph_format.space_after = Pt(24)
        bib_label.paragraph_format.page_break_before = True
        bib_label.runs[0].underline = True

    doc.save(filename)
