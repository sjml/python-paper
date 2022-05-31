import subprocess

from .util import get_content_file_list
from .shared import PANDOC_INPUT_FORMAT


def fmt(wrap: bool, columns: int):
    for cf in get_content_file_list():
        # fmt: off
        cmd = ["pandoc",
            "--from", PANDOC_INPUT_FORMAT,
            "--to", PANDOC_INPUT_FORMAT,
            "--output", cf,
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

        subprocess.check_call(cmd)
