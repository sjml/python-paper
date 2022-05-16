import os
import subprocess
from datetime import datetime

from docx import Document
from docx import enum
from docx.shared import Pt
from PyPDF2 import PdfFileReader, PdfFileWriter

from . import LIB_NAME, LIB_VERSION


def package(filename: str, meta: dict):
    doc = Document(filename)

    if len(doc.paragraphs) == 0:
        doc.add_paragraph("", style="First Paragraph")

    starting_graph = doc.paragraphs[0]
    starting_graph.paragraph_format.page_break_before = True

    raw_date = meta['data']['date']
    if raw_date == None:
        target_date = datetime.now()
    else:
        target_date = raw_date
    # I think this is the Chicago style?
    date_string = target_date.strftime("%B %-d, %Y")
    # MLA: "%-d %B %Y"

    starting_graph.insert_paragraph_before(meta["data"]["title"], style="Title")
    starting_graph.insert_paragraph_before("by", style="Author")
    starting_graph.insert_paragraph_before(meta["data"]["author"], style="Author")
    starting_graph.insert_paragraph_before(f"{meta['professor']}\n{meta['class_mnemonic']} — {meta['class_name']}\n{date_string}", style="Author")

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

    doc.core_properties.author = meta["data"]["author"]
    doc.core_properties.title = meta["data"]["title"]

    doc.save(filename)

def make_pdf(filename: str, meta: dict):
    filepath = os.path.abspath(filename)
    base = os.path.splitext(filepath)[0]
    pdf_filename = base + ".pdf"

    applescript = f"""
    tell application "System Events" to set wordIsRunning to exists (processes where name is "Microsoft Word")

    tell application id "com.microsoft.Word"
        activate
        open "{filepath}"
        repeat while not (active document is not missing value)
            delay 0.5
        end repeat
        set activeDoc to active document
        save as activeDoc file name "{pdf_filename}" file format format PDF
        close activeDoc saving no
        if not wordIsRunning then
            quit
        end if
    end tell
    """
    subprocess.run(["osascript", "-"], input=applescript.encode("utf-8"))

    reader = PdfFileReader(pdf_filename)
    writer = PdfFileWriter()
    writer.appendPagesFromReader(reader)
    pdf_date = datetime.utcnow().strftime("%Y%m%d%H%MZ00'00'")
    writer.addMetadata({
        "/Author": meta["data"]["author"],
        "/Title": meta["data"]["title"],
        "/Producer": f"{LIB_NAME} {LIB_VERSION}",
        "/CreationDate": f"D:{pdf_date}",
    })

    with open(pdf_filename, "wb") as pdfout:
        writer.write(pdfout)
