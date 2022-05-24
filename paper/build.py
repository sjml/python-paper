import os
from pathlib import Path
import subprocess
import re

import typer
import jsbeautifier

from .util import ensure_paper_dir, get_metadata, get_assignment
from .formats import Format
from .doc_handling import make_pdf, package
from .shared import PAPER_STATE

def build(output_format: Format = Format.docx):
    ensure_paper_dir()

    if PAPER_STATE["verbose"]:
        typer.echo(f"Building for format {output_format}")

    if not os.path.exists("./out"):
        os.mkdir("./out")

    meta = get_metadata()

    if "filename" not in meta:
        author = meta["data"]["author"].split(",")[0].split(" ")[-1]
        mnemonic = re.sub(r"\s", "", meta["data"]["class_mnemonic"])
        meta["filename"] = f"{author}_{mnemonic}"
        assignment_underscored = re.sub(r"\s+", "_", get_assignment())
        meta["filename"] += f"_{assignment_underscored}"
        if PAPER_STATE["verbose"]:
            typer.echo(f"No filename given; using generated \"{meta['filename']}\"")

    cmd = ["pandoc",
        "--from=markdown+bracketed_spans",
        "--metadata-file", "./paper_meta.yml",
        "--resource-path", "./content",
    ]

    if output_format in [Format.docx, Format.docx_pdf]:
        output_suffix = "docx"
        cmd.extend([
            "--to=docx",
            "--reference-doc", "./resources/ChicagoStyle-TimesNewRoman_Template.docx",
        ])
    elif output_format == Format.json:
        output_suffix = "json"
        cmd.extend(["--to", "json"])

    output_filename = f"./out/{meta['filename']}.{output_suffix}"
    cmd.extend(["--output", output_filename])

    filter_dir = os.path.join(".", "resources", "filters")
    filters = [f for f in os.listdir(filter_dir) if f.startswith("filter-")]
    filter_cmds = ["--lua-filter" if not toggle else os.path.join(filter_dir, f) for f in filters for toggle in range(2)]
    cmd.extend(filter_cmds)

    bib_path_strings = meta.get("sources", [])
    bib_paths: list[Path] = [Path(bps).expanduser().resolve() for bps in bib_path_strings]
    bib_paths = [p.as_posix() for p in bib_paths if p.exists()]

    if len(bib_paths) > 0:
        if PAPER_STATE["verbose"]:
            typer.echo("Processing citations...")
        cmd.append("--citeproc")
        if not "use_ibid" in meta or meta["use_ibid"] == False:
            cmd.extend(["--csl", "./resources/chicago-fullnote-bibliography-short-title-subsequent.csl"])
        else:
            cmd.extend(["--csl", "./resources/chicago-fullnote-bibliography-with-ibid.csl"])
        cmd.extend(["--bibliography" if not toggle else bp for bp in bib_paths for toggle in range(2)])

        post_filters = [f for f in os.listdir(filter_dir) if f.startswith("post-filter-")]
        post_filter_cmds = ["--lua-filter" if not toggle else os.path.join(filter_dir, f) for f in post_filters for toggle in range(2)]
        cmd.extend(post_filter_cmds)
    else:
        if PAPER_STATE["verbose"]:
            typer.echo("No citation processing.")

    cmd.extend([os.path.join("./content", f) for f in os.listdir("./content") if f.endswith(".md")])

    if PAPER_STATE["verbose"]:
        typer.echo("Invoking pandoc:")
        typer.echo(f"\t{' '.join(cmd)}")
    subprocess.check_call(cmd)

    if output_format in [Format.docx, Format.docx_pdf]:
        package(output_filename, meta)
        if output_format == Format.docx_pdf:
            make_pdf(output_filename, meta)
    elif output_format == Format.json:
        if PAPER_STATE["verbose"]:
            typer.echo("Prettifying JSON output...")
        opts = jsbeautifier.default_options()
        opts.indent_size = 2
        with open(output_filename, "r") as jsonin:
            output_json = jsonin.read()
        pretty_json = jsbeautifier.beautify(output_json, opts)
        if PAPER_STATE["verbose"]:
            typer.echo(f"Writing final JSON to {output_filename}...")
        with open(output_filename, "w") as jsonout:
            jsonout.write(pretty_json)
