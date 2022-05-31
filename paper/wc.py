import json

import typer

from .util import get_content_file_list, ensure_paper_dir


def _wc_data() -> dict[str, int]:
    wc_map = {}
    content_files = get_content_file_list()
    for cf in content_files:
        contents = open(cf, "r").read().strip()
        if contents.startswith("---\n"):
            contents = contents.split("---\n")[2]
        wc_map[cf] = len(contents.split())
    return wc_map


def _wc_string() -> str:
    wc_map_raw = _wc_data()
    wc_map = {}
    for k, v in wc_map_raw.items():
        wc_map[k.replace("./content/", "")] = v
    filename_max_len = max(*[len(fn) + 2 for fn in wc_map.keys()], len("Files"), len("**TOTAL**"))
    wc_max_len = max(*[len(str(wc)) for wc in wc_map.values()], len("Word Count"))

    output = "## Current word count:\n"
    output += f"| {'File':<{filename_max_len}} | {'Word Count':<{wc_max_len}} |\n"
    output += f"| {'':-<{filename_max_len}} | {'':-<{wc_max_len}} |\n"
    for f, wc in wc_map.items():
        output += f"| {f'`{f}`':<{filename_max_len}} | {wc:<{wc_max_len}} |\n"
    output += f"| {'**TOTAL**':<{filename_max_len}} | {sum(wc_map.values()):<{wc_max_len}} |"
    return output


def _wc_json() -> str:
    wc_map_raw = _wc_data()
    wc_map = {}
    for k, v in wc_map_raw.items():
        wc_map[k.replace("./content/", "")] = v
    return json.dumps({"total": sum(wc_map.values()), "breakdown": wc_map})


def wc():
    ensure_paper_dir()

    typer.echo(_wc_string())
    typer.echo()
