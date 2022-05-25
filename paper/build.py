import os
from pathlib import Path
import subprocess
import re

import typer

from .util import ensure_paper_dir, get_metadata, get_assignment
from .formats import Format, prepare_command, finish_file
from .shared import PAPER_STATE

OUTPUT_DIRECTORY_NAME = "output"

def build(output_format: Format):
    ensure_paper_dir()

    if PAPER_STATE["verbose"]:
        typer.echo(f"Building for format {output_format}")

    if not os.path.exists(os.path.join(".", OUTPUT_DIRECTORY_NAME)):
        os.mkdir(os.path.join(".", OUTPUT_DIRECTORY_NAME))

    meta = get_metadata()

    if "filename" not in meta:
        author = meta["data"]["author"].split(",")[0].split(" ")[-1]
        if "class_mnemonic" in meta["data"]:
            mnemonic = re.sub(r"\s", "", meta["data"]["class_mnemonic"])
            meta["filename"] = f"{author}_{mnemonic}"
        else:
            meta["filename"] = author
        assignment_underscored = re.sub(r"\s+", "_", get_assignment())
        meta["filename"] += f"_{assignment_underscored}"
        if PAPER_STATE["verbose"]:
            typer.echo(f"No filename given; using generated \"{meta['filename']}\"")

    cmd = ["pandoc",
        "--from=markdown+bracketed_spans-auto_identifiers",
        "--metadata-file", "./paper_meta.yml",
        "--resource-path", "./content",
    ]

    output_suffix = prepare_command(cmd, output_format)

    output_filename = os.path.join(".", OUTPUT_DIRECTORY_NAME, f"{meta['filename']}.{output_suffix}")
    cmd.extend(["--output", output_filename])

    filter_dir = os.path.join(".", ".paper_resources", "filters")
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
            cmd.extend(["--csl", "./.paper_resources/chicago-fullnote-bibliography-short-title-subsequent.csl"])
        else:
            cmd.extend(["--csl", "./.paper_resources/chicago-fullnote-bibliography-with-ibid.csl"])
        cmd.extend(["--bibliography" if not toggle else bp for bp in bib_paths for toggle in range(2)])

        post_filters = [f for f in os.listdir(filter_dir) if f.startswith("post-filter-")]
        post_filter_cmds = ["--lua-filter" if not toggle else os.path.join(filter_dir, f) for f in post_filters for toggle in range(2)]
        cmd.extend(post_filter_cmds)
    else:
        if PAPER_STATE["verbose"]:
            typer.echo("No citation processing.")

    content_files = [os.path.join("./content", f) for f in os.listdir("./content") if f.endswith(".md")]
    content_files.sort()
    cmd.extend(content_files)

    if PAPER_STATE["verbose"]:
        typer.echo("Invoking pandoc:")
        typer.echo(f"\t{' '.join(cmd)}")
    subprocess.check_call(cmd)

    finish_file(output_filename, output_format)
