import enum

import typer
import jsbeautifier

from .shared import PAPER_STATE
from .util import get_metadata
from .doc_handling import make_pdf, package

class Format(str, enum.Enum):
    docx = "docx"
    docx_pdf = "docx+pdf"
    json = "json"


def prepare_command(cmd: list[str], f: Format) -> str:
    if f in [Format.docx, Format.docx_pdf]:
        cmd.extend([
            "--to=docx",
            "--reference-doc", "./.paper_resources/ChicagoStyle_Template.docx",
        ])
        return "docx"

    elif f == Format.json:
        cmd.extend(["--to", "json"])
        return "json"


def finish_file(filepath: str, f: Format):
    meta = get_metadata()

    if f in [Format.docx, Format.docx_pdf]:
        package(filepath, meta)
        if f == Format.docx_pdf:
            make_pdf(filepath, meta)

    elif f == Format.json:
        if PAPER_STATE["verbose"]:
            typer.echo("Prettifying JSON output...")
        opts = jsbeautifier.default_options()
        opts.indent_size = 2
        with open(filepath, "r") as jsonin:
            output_json = jsonin.read()
        pretty_json = jsbeautifier.beautify(output_json, opts)
        if PAPER_STATE["verbose"]:
            typer.echo(f"Writing final JSON to {filepath}...")
        with open(filepath, "w") as jsonout:
            jsonout.write(pretty_json)
