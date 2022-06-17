import subprocess

import typer

from .util import ensure_paper_dir, get_content_file_list
from .shared import PANDOC_INPUT_FORMAT, PAPER_STATE


def fmt(wrap: bool, columns: int):
    ensure_paper_dir()

    for cf in get_content_file_list():
        # fmt: off
        cmd = ["pandoc",
            "--from", PANDOC_INPUT_FORMAT,
            "--to", PANDOC_INPUT_FORMAT,
        ]
        if wrap:
            cmd.extend([
                "--wrap", "auto",
                "--columns", str(columns),
            ])
        else:
            cmd.extend([
                "--wrap", "preserve",
            ])
        # fmt: on

        cmd.append(cf)

        md_out = subprocess.check_output(cmd).decode("utf-8")
        md_curr = open(cf, "r").read()
        if md_out.strip() != md_curr.strip():
            if PAPER_STATE["verbose"]:
                typer.echo(f"Reformatting {cf}...")
            with open(cf, "w") as out:
                out.write(md_out)
