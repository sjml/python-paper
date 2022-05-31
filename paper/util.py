import os
from datetime import datetime

import typer
import yaml


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
        typer.echo(f"Not in a paper directory: {reason}")
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
        year_str = "786 A.U.C."
    return f"{target_date.strftime('%B %-d')}, {year_str}"


def get_content_file_list() -> list[str]:
    content_files = []
    for dirpath, _, files in os.walk("./content"):
        content_files.extend([os.path.join(dirpath, f) for f in files if f.endswith(".md")])
    content_files.sort()
    return content_files
