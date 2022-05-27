import os
import enum
import tempfile
import subprocess
import shutil

import typer
import jsbeautifier

from . import LIB_NAME, LIB_VERSION
from .shared import PAPER_STATE
from .util import get_metadata, get_date_string
from .doc_handling import make_pdf, package

class Format(str, enum.Enum):
    docx = "docx"
    docx_pdf = "docx+pdf"
    latex = "latex"
    latex_pdf = "latex+pdf"
    json = "json"


def prepare_command(cmd: list[str], f: Format) -> str:
    meta = get_metadata()

    if f in [Format.docx, Format.docx_pdf]:
        cmd.extend([
            "--to=docx",
            "--reference-doc", "./.paper_resources/ChicagoStyle_Template.docx",
        ])
        return "docx"

    elif f in [Format.latex, Format.latex_pdf]:
        cmd.extend([
            "--to=latex",
            "--shift-heading-level-by", "-1",
        ])
        if "latex" in meta and type(meta["latex"]) == dict and "fragment" in meta["latex"] and meta["latex"]["fragment"] == True:
            if PAPER_STATE["verbose"]:
                typer.echo(f"Generating LaTeX fragment...")
        else:
            if PAPER_STATE["verbose"]:
                typer.echo(f"Generating full LaTeX file...")
            cmd.extend([
                "--template", "./.paper_resources/ChicagoStyle_Template.tex",
            ])

        cmd.extend([
            "--variable", f"library_name={LIB_NAME}",
            "--variable", f"library_version={LIB_VERSION}",
        ])
        for k,v in meta["data"].items():
            if v:
                if k == "date":
                    v = get_date_string()
                vesc = v.replace("_", "\_")
                cmd.extend(["--variable", f"{k}={{{vesc}}}"])

        if "latex" in meta and type(meta["latex"]) == dict and "ragged" in meta["latex"] and meta["latex"]["ragged"] == True:
            cmd.extend([
                "--variable", f"ragged=true",
            ])

        return "tex"

    elif f == Format.json:
        cmd.extend(["--to", "json"])
        return "json"

    else:
        raise RuntimeError(f"Unrecognized format: {f}")


def finish_file(filepath: str, f: Format):
    meta = get_metadata()

    if f in [Format.docx, Format.docx_pdf]:
        package(filepath, meta)
        if f == Format.docx_pdf:
            make_pdf(filepath, meta)

    elif f == Format.latex_pdf:
        current = os.getcwd()
        output_path = os.path.dirname(filepath)
        os.chdir(output_path)
        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            tex_engine = "xelatex"
            cmd = [
                tex_engine,
                    "--halt-on-error",
                    "--interaction", "nonstopmode",
                    "--output-directory", tmpdir,
                    "--jobname", meta["filename"],
                    os.path.basename(filepath),
            ]
            # LaTex needs to be run twice to do the pagination stuff
            try:
                subprocess.check_output(cmd)
                subprocess.check_output(cmd)
            except subprocess.CalledProcessError as e:
                print(f"{tex_engine.upper()} ERROR: {e.returncode}")
                print(e.output)
            pdf_filename = f"{meta['filename']}.pdf"
            if os.path.exists(pdf_filename):
                os.unlink(pdf_filename)
            shutil.move(
                os.path.join(tmpdir, pdf_filename),
                ".",
            )
        os.chdir(current)

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
