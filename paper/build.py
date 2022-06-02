import os
import sys
import subprocess
import re
import json

import typer

from .util import (
    ensure_paper_dir,
    get_metadata,
    get_assignment,
    get_content_file_list,
    stamp_local_dir,
    get_bibliography_source_list,
    get_paper_version_stamp,
    get_content_timestamp,
)
from .formats import Format, prepare_command, finish_file
from .shared import PAPER_STATE, PANDOC_INPUT_FORMAT

OUTPUT_DIRECTORY_NAME = "output"


def build(output_format: Format):
    ensure_paper_dir()

    meta = get_metadata()

    if output_format == None:
        if "default_format" in meta:
            output_format = meta["default_format"]
            all_formats = [f.value for f in Format]
            if output_format not in all_formats:
                allf_str = ", ".join([f"'{f}'" for f in all_formats])
                # stealing this error message format from Click because
                #   I can't figure out how to directly invoke the validation
                #   or catch it. :-/
                # https://github.com/pallets/click/blob/a8910b382d37cce14adeb44a73aca1d4e87c2413/src/click/types.py#L295
                typer.echo(
                    f"Error: Invalid value for 'default_format' in metadata: '{output_format}' is not one of {allf_str}."
                )
                raise typer.Exit(2)
        else:
            output_format = Format.docx

    if PAPER_STATE["verbose"]:
        typer.echo(f"Building for format {output_format}")

    content_timestamp = int(get_content_timestamp())
    if PAPER_STATE["verbose"]:
        typer.echo(f"Setting source epoch to {content_timestamp}")
    os.environ["SOURCE_DATE_EPOCH"] = str(content_timestamp)

    if not os.path.exists(os.path.join(".", OUTPUT_DIRECTORY_NAME)):
        os.mkdir(os.path.join(".", OUTPUT_DIRECTORY_NAME))

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

    # fmt: off
    cmd = ["pandoc",
        "--from", PANDOC_INPUT_FORMAT,
        "--metadata-file", "./paper_meta.yml",
        "--resource-path", "./content",
    ]
    # fmt: on

    output_suffix, tmp_prefix_files, tmp_suffix_files = prepare_command(cmd, output_format)

    output_filename = os.path.join(".", OUTPUT_DIRECTORY_NAME, f"{meta['filename']}.{output_suffix}")
    cmd.extend(["--output", output_filename])

    filter_dir = os.path.join(".", ".paper_resources", "filters")
    filters = [f for f in os.listdir(filter_dir) if f.startswith("filter-")]
    filter_cmds = [
        "--lua-filter" if not toggle else os.path.join(filter_dir, f) for f in filters for toggle in range(2)
    ]
    cmd.extend(filter_cmds)

    bib_paths = get_bibliography_source_list()

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
        post_filter_cmds = [
            "--lua-filter" if not toggle else os.path.join(filter_dir, f) for f in post_filters for toggle in range(2)
        ]
        cmd.extend(post_filter_cmds)
    else:
        if PAPER_STATE["verbose"]:
            typer.echo("No citation processing.")

    input_file_list = []
    input_file_list.extend(tmp_prefix_files)
    input_file_list.extend(get_content_file_list())
    input_file_list.extend(tmp_suffix_files)
    cmd.extend(input_file_list)

    if PAPER_STATE["verbose"]:
        typer.echo("Invoking pandoc:")
        typer.echo(f"\t{' '.join(cmd)}")
    subprocess.check_call(cmd)

    log_lines = finish_file(output_filename, output_format)

    if PAPER_STATE["verbose"]:
        typer.echo("Cleaning up temp files...")
    for f in tmp_prefix_files:
        os.unlink(f)
    for f in tmp_suffix_files:
        os.unlink(f)

    _record_build_data(log_lines)


def _record_build_data(log_lines: list[str]):
    # paper version record
    stamp_local_dir()

    # record data on cited references
    bib_paths = get_bibliography_source_list()
    if len(bib_paths) > 0:
        cited_reference_keys = []
        refs = []
        with open(os.devnull, "wb") as dev_null:
            # fmt: off
            cmd = ["pandoc",
                "--to", os.path.join(os.path.dirname(__file__), "resources", "writers", "ref_list.lua"),
                "--metadata-file", "./paper_meta.yml",
                "--citeproc"
            ]
            # fmt: on
            cmd.extend(["--bibliography" if not toggle else bp for bp in bib_paths for toggle in range(2)])
            cmd.extend(get_content_file_list())
            ref_str = subprocess.check_output(cmd, stderr=dev_null).decode("utf-8").strip()
            cited_reference_keys.extend(ref_str.splitlines())

            # gotta do one-by-one because a .json file will get assumed as a dumped AST;
            #   others will get autodetected
            for ref_list in bib_paths:
                # fmt: off
                cmd = ["pandoc",
                    "--to", "csljson",
                ]
                # fmt: on
                if ref_list.endswith(".json"):
                    cmd.extend(["--from", "csljson"])
                cmd.append(ref_list)
                source_data_text = subprocess.check_output(cmd, stderr=dev_null)
                source_data = json.loads(source_data_text)
                for entry in source_data:
                    if entry["id"] in cited_reference_keys:
                        refs.append(entry)

        with open(os.path.join(".paper_data", "cited_references.json"), "w") as refs_out:
            json.dump(refs, refs_out, indent="  ")

    with open(os.path.join(".paper_data", "build_environment.txt"), "w") as build_out:
        separator = f"{'#' * 60}"

        # paper version
        build_out.write(get_paper_version_stamp())
        build_out.write(f"\n{separator}\n")

        # python libraries
        python_reqs = (
            subprocess.check_output([sys.executable, "-m", "pip", "freeze", "--local"]).decode("utf-8").splitlines()
        )
        python_reqs = [r for r in python_reqs if not r.startswith("-e ")]
        build_out.write("\n".join(python_reqs))
        build_out.write(f"\n{separator}\n")

        # format-specific stuff, if needed
        build_out.write("\n".join(log_lines))
