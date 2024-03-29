import os
import sys
import enum
import tempfile
import subprocess
import shutil
import json

import typer

from . import LIB_NAME, LIB_VERSION_STR
from .shared import PAPER_STATE, PANDOC_INPUT_FORMAT
from .util import get_metadata, get_date_string
from .doc_handling import make_pdf, package, generate_title_page_string


class Format(str, enum.Enum):
    docx = "docx"
    docx_pdf = "docx+pdf"
    latex = "latex"
    latex_pdf = "latex+pdf"
    json = "json"


def prepare_command(cmd: list[str], f: Format) -> tuple[str, list[str], list[str]]:
    meta = get_metadata()

    if f in [Format.docx, Format.docx_pdf]:
        # fmt: off
        cmd.extend([
            "--to=docx",
            "--reference-doc", "./.paper_resources/ChicagoStyle_Template.docx",
        ])
        # fmt: on

        prefix_files = []
        if "no_title_page" not in meta or meta["no_title_page"] == False:
            file_handle, file_name = tempfile.mkstemp(".md", dir="output", prefix="title_page_", text=True)
            prefix_files.append(file_name)
            if PAPER_STATE["verbose"]:
                typer.echo(f"Generating title page into {file_name}...")
            with open(file_handle, "w") as title_page_file:
                title_page_file.write(generate_title_page_string(meta))

        return "docx", prefix_files, []

    elif f in [Format.latex, Format.latex_pdf]:
        # fmt: off
        cmd.extend([
            "--to=latex",
            "--shift-heading-level-by", "-1",
        ])
        # fmt: on
        if (
            "latex" in meta
            and type(meta["latex"]) == dict
            and "fragment" in meta["latex"]
            and meta["latex"]["fragment"] == True
        ):
            if PAPER_STATE["verbose"]:
                typer.echo(f"Generating LaTeX fragment...")
        else:
            if PAPER_STATE["verbose"]:
                typer.echo(f"Generating full LaTeX file...")
            # fmt: off
            cmd.extend([
                "--template", "./.paper_resources/ChicagoStyle_Template.tex",
            ])
            # fmt: on

        # fmt: off
        cmd.extend([
            "--variable", f"library_name={LIB_NAME}",
            "--variable", f"library_version={LIB_VERSION_STR}",
        ])
        # fmt: on
        for k, v in meta["data"].items():
            if v:
                if k == "date":
                    v = get_date_string()
                # process any markdown inside the variables (italics in a title, for instance)
                # fmt: off
                marked_up = subprocess.check_output(["pandoc",
                    "--from", PANDOC_INPUT_FORMAT,
                    "--to", "latex"
                ], input=v.encode("utf-8"))
                # fmt: on
                marked_up = marked_up.decode("utf-8").strip()

                cmd.extend(["--variable", f"{k}={{{marked_up}}}"])

        if (
            "latex" in meta
            and type(meta["latex"]) == dict
            and "ragged" in meta["latex"]
            and meta["latex"]["ragged"] == True
        ):
            # fmt: off
            cmd.extend([
                "--variable", f"ragged=true",
            ])
            # fmt: on

        if "base_font_override" in meta and meta["base_font_override"] != None:
            if PAPER_STATE["verbose"]:
                typer.echo(f"Changing base font to {meta['base_font_override']}...")
            cmd.extend(["--variable", f"base_font_override={meta['base_font_override']}"])  # fmt: skip
        if "mono_font_override" in meta and meta["mono_font_override"] != None:
            if PAPER_STATE["verbose"]:
                typer.echo(f"Changing mono font to {meta['mono_font_override']}...")
            cmd.extend(["--variable", f"mono_font_override={meta['mono_font_override']}"])  # fmt: skip

        return "tex", [], []

    elif f == Format.json:
        cmd.extend(["--to", "json"])  # fmt: skip
        return "json", [], []

    else:
        raise RuntimeError(f"Unrecognized format: {f}")


def finish_file(filepath: str, f: Format) -> list[str]:
    log_lines = []
    meta = get_metadata()

    if f in [Format.docx, Format.docx_pdf]:
        package(filepath, meta)
        if f == Format.docx_pdf:
            make_pdf(filepath, meta)

    elif f == Format.latex_pdf:
        current = os.getcwd()
        output_path = os.path.dirname(filepath)
        os.chdir(output_path)

        tmpdir = "pdf_out"
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)
        os.mkdir(tmpdir)

        tex_engine = "xelatex"
        # fmt: off
        cmd = [
            tex_engine,
                "--halt-on-error",
                "--interaction", "nonstopmode",
                "--output-directory", tmpdir,
                "--jobname", meta["filename"],
                os.path.basename(filepath),
        ]
        # fmt: on

        try:
            if PAPER_STATE["verbose"]:
                typer.echo("Running LaTeX build command:")
                typer.echo(f"\t{' '.join(cmd)}")
            # LaTex needs to be run twice to do the pagination stuff
            for _ in range(2):
                output = subprocess.check_output(cmd).decode("utf-8")
                if PAPER_STATE["verbose"]:
                    typer.echo(output)
            pdf_filename = f"{meta['filename']}.pdf"
            if os.path.exists(pdf_filename):
                os.unlink(pdf_filename)
            shutil.move(
                os.path.join(tmpdir, pdf_filename),
                ".",
            )

            engine_data = subprocess.check_output([tex_engine, "--version"]).decode("utf-8").strip()
            log_lines.extend(engine_data.splitlines())
            log_lines.append("-----")
            log_data = open(os.path.join(tmpdir, f"{meta['filename']}.log")).read()
            package_data = [l[len("Package: ") :] for l in log_data.splitlines() if l.startswith("Package: ")]
            log_lines.extend(package_data)

        except subprocess.CalledProcessError as e:
            typer.echo(f"{tex_engine.upper()} ERROR: {e.returncode}")
            typer.echo(e.output.decode("utf-8").replace("\\n", "\n"))
            sys.exit(e.returncode)

        finally:
            shutil.rmtree(tmpdir)

        os.chdir(current)

    elif f == Format.json:
        if PAPER_STATE["verbose"]:
            typer.echo("Prettifying JSON output...")

        json_in = json.load(open(filepath, "r"))
        with open(filepath, "w") as outfile:
            json.dump(json_in, outfile, indent="  ")

    return log_lines
