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
    def bail():
        typer.echo("Not in a paper directory.")
        raise typer.Exit(1)
    if not os.path.exists("./paper_meta.yml") or not os.path.isfile("./paper_meta.yml"):
        bail
    if not os.path.exists("./.paper_resources") or not os.path.isdir("./.paper_resources"):
        bail()
    if not os.path.exists("./content") or not os.path.isdir("./content"):
        bail()
    file_list = os.listdir("./content")
    if len(file_list) == 0:
        bail()

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
