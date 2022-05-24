import os
import shutil
import subprocess
from datetime import datetime

import typer
from docx import Document
from docx import enum
from docx.shared import Pt
from docx.oxml.ns import qn
from PyPDF2 import PdfFileReader, PdfFileWriter

from . import LIB_NAME, LIB_VERSION
from .shared import PAPER_STATE

def _add_chicago_title(doc: Document, meta: dict):
    starting_graph = doc.paragraphs[0]
    starting_graph.paragraph_format.page_break_before = True

    raw_date = meta['data']['date']
    if raw_date == None:
        target_date = datetime.now()
    else:
        target_date = raw_date
    date_string = target_date.strftime("%B %-d, %Y")

    starting_graph.insert_paragraph_before(meta["data"]["title"], style="Title")
    starting_graph.insert_paragraph_before("by", style="Author")
    starting_graph.insert_paragraph_before(meta["data"]["author"], style="Author")
    starting_graph.insert_paragraph_before(f"{meta['data']['professor']}\n{meta['data']['class_mnemonic']} — {meta['data']['class_name']}\n{date_string}", style="Author")


def package(filename: str, meta: dict):
    if PAPER_STATE["verbose"]:
        typer.echo("Packaging docx...")
    doc = Document(filename)

    if len(doc.paragraphs) == 0:
        if PAPER_STATE["verbose"]:
            typer.echo("No first paragraph; adding blank...")
        doc.add_paragraph("", style="First Paragraph")

    # change font if we were asked to
    if "font_override" in meta and meta["font_override"] != None:
        if PAPER_STATE["verbose"]:
            typer.echo(f"Changing base font to {meta['font_override']}...")
        doc.styles["Normal"].font.name = meta['font_override']

    # set metadata
    if PAPER_STATE["verbose"]:
        typer.echo("Fixing docx metadata...")
    doc.core_properties.title = meta["data"]["title"]
    doc.core_properties.author = meta["data"]["author"]
    doc.core_properties.last_modified_by = meta["data"]["author"]
    doc.core_properties.revision = max(1, int(subprocess.check_output(["git", "rev-list", "--all", "--count"])) - 1)

    # add title
    if PAPER_STATE["verbose"]:
        typer.echo("Adding title page...")
    _add_chicago_title(doc, meta)

    # check "Total Row" box on tables
    if len(doc.tables) > 0:
        if PAPER_STATE["verbose"]:
            typer.echo("Fixing table formatting...")
    for t in doc.tables:
        tblLook = t._tblPr.first_child_found_in("w:tblLook")
        tblLook.set(qn("w:lastRow"), "1")

    # add "Works Cited" label to bibliography
    if PAPER_STATE["verbose"]:
        typer.echo("Adding bibliography label...")
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

    if PAPER_STATE["verbose"]:
        typer.echo(f"Writing final docx to {filename}...")
    doc.save(filename)

def make_pdf(filename: str, meta: dict):
    if PAPER_STATE["verbose"]:
        typer.echo("Generating PDF...")
    filepath = os.path.abspath(filename)
    base = os.path.splitext(filepath)[0]
    pdf_filepath = base + ".pdf"
    if os.path.exists(pdf_filepath):
        os.unlink(pdf_filepath)

    outpath = os.path.expanduser(f"~/Library/Containers/com.microsoft.Word/Data/Documents/{os.path.basename(pdf_filepath)}")

    applescript = f"""
    tell application "System Events" to set wordIsRunning to exists (processes where name is "Microsoft Word")

    set outpath to "{outpath[1:].replace('/', ':')}"
    tell application id "com.microsoft.Word"
        activate
        open file "{filepath[1:].replace('/', ':')}"
        repeat while not (active document is not missing value)
            delay 0.5
        end repeat
        set activeDoc to active document
        save as activeDoc file name outpath file format format PDF
        close activeDoc saving no
        if not wordIsRunning then
            quit
        end if
    end tell
    """
    subprocess.run(["osascript", "-"], input=applescript.encode("utf-8"))

    shutil.move(outpath, pdf_filepath)

    if PAPER_STATE["verbose"]:
        typer.echo("Fixing PDF metadata...")
    reader = PdfFileReader(pdf_filepath)
    writer = PdfFileWriter()
    writer.appendPagesFromReader(reader)
    pdf_date = datetime.utcnow().strftime("%Y%m%d%H%MZ00'00'")
    writer.addMetadata({
        "/Author": meta["data"]["author"],
        "/Title": meta["data"]["title"],
        "/Producer": f"{LIB_NAME} {LIB_VERSION}",
        "/CreationDate": f"D:{pdf_date}",
    })

    if PAPER_STATE["verbose"]:
        typer.echo(f"Writing final PDF to {pdf_filepath}...")
    with open(pdf_filepath, "wb") as pdfout:
        writer.write(pdfout)
