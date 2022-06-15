import os
import subprocess
from datetime import datetime
from pathlib import Path

import typer
import yaml

from . import LIB_NAME, LIB_VERSION_STR
from .shared import PAPER_STATE


def merge_dictionary(target, new_dict):
    for k, v in new_dict.items():
        if isinstance(target.get(k, None), dict) and isinstance(v, dict):
            merge_dictionary(target[k], v)
        elif isinstance(v, list):
            if isinstance(target.get(k, None), list):
                target[k].extend(v)
            else:
                target[k] = v
        else:
            if k in target and v.startswith("[") and v.endswith("]"):
                continue
            target[k] = v


def ensure_paper_dir():
    def bail(reason: str):
        if PAPER_STATE["verbose"]:
            typer.echo(f"Not in a paper directory: {reason}")
        else:
            typer.echo(f"Not in a paper directory.")
        raise typer.Exit(1)

    if not os.path.exists("./paper_meta.yml") or not os.path.isfile("./paper_meta.yml"):
        bail("missing metadata file")
    if not os.path.exists("./.paper_resources") or not os.path.isdir("./.paper_resources"):
        bail("missing resources directory")
    if not os.path.exists("./content") or not os.path.isdir("./content"):
        bail("missing content directory")
    file_list = os.listdir("./content")
    if len(file_list) == 0:
        bail("no content files")


_meta = None


def get_metadata() -> dict:
    global _meta
    if _meta == None:
        data = list(yaml.safe_load_all(open("./paper_meta.yml")))[0]
        if "data" not in data:
            data["data"] = {}
        if "date" not in data["data"] or data["data"]["date"] == "[DATE]":
            data["data"]["date"] = None
        else:
            date = datetime.fromisoformat(data["data"]["date"])
            data["data"]["date"] = date
        _meta = data
    return _meta


def get_assignment() -> str:
    meta = get_metadata()
    if "assignment" in meta:
        return meta["assignment"]
    else:
        return os.path.basename(os.getcwd())


def get_date_string() -> str:
    meta = get_metadata()
    raw_date = meta["data"]["date"]
    if raw_date == None:
        target_date = datetime.now()
    else:
        target_date = raw_date
    # because one of my example documents has a due date of 33 AD, and what's
    #  the point of making your own system if you can't have a little Easter egg?
    #  :D
    year_str = target_date.strftime("%Y").lstrip("0")
    if year_str == "33":
        year_str = "A.U.C. 786"
    return f"{target_date.strftime('%B %-d')}, {year_str}"


def get_paper_version_stamp() -> str:
    version = f"{LIB_NAME} v{LIB_VERSION_STR}"

    wd = os.path.dirname(__file__)
    is_git = 0 == subprocess.call(["git", "rev-parse"], cwd=wd)
    if is_git:
        git_rev = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=wd).decode("utf-8").strip()
        version = f"{version}\n{git_rev}"
        diffs = subprocess.check_output(["git", "diff", "--stat"], cwd=wd).decode("utf-8").strip()
        if len(diffs) != 0:
            version = f"{version}+dev"

    return version


def stamp_local_dir():
    vers = get_paper_version_stamp()
    if not os.path.exists(".paper_data"):
        os.mkdir(".paper_data")
    with open(os.path.join(".paper_data", "last_paper_version.txt"), "w") as stamp:
        stamp.write(f"{vers}\n")


def get_content_file_list() -> list[str]:
    content_files = []
    for dirpath, _, files in os.walk("./content"):
        content_files.extend([os.path.join(dirpath, f) for f in files if f.endswith(".md")])
    content_files.sort()
    return content_files


def get_content_timestamp() -> float:
    # if there are no changes in the content directory, return the last commit time
    content_status = subprocess.check_output(["git", "status", "./content", "--porcelain"]).decode("utf-8").strip()
    if len(content_status) == 0:
        git_commit_time_str = subprocess.check_output(["git", "log", "-1", "--format=%ct"]).decode("utf-8").strip()
        return float(git_commit_time_str)
    # otherwise return the most recent mod time in the directory
    mod_times = []
    for dirpath, _, files in os.walk("./content"):
        [mod_times.append(os.path.getmtime(os.path.join(dirpath, f))) for f in files if not f.startswith(".")]
    return max(mod_times)


def get_bibliography_source_list() -> list[str]:
    meta = get_metadata()

    bib_path_strings = meta.get("sources", [])
    bib_paths: list[Path] = [Path(bps).expanduser().resolve() for bps in bib_path_strings]
    bib_paths = [p.as_posix() for p in bib_paths if p.exists()]

    return bib_paths
