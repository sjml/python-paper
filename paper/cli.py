import os
from distutils import dir_util
from pathlib import Path
import subprocess
import datetime
import re

import typer
import yaml

from . import LIB_NAME, LIB_VERSION
from .util import merge_dictionary
from .doc_handling import package, make_pdf

VERSION_STRING = f"{LIB_NAME} v{LIB_VERSION}"

_app = typer.Typer()
def main():
    _app()

@_app.command()
def new(project_name: str):
    print(f"Starting new project called '{project_name}'...")
    dirname = os.path.normpath(project_name)
    if project_name != dirname:
        typer.echo(f"Invalid project name: '{project_name}'")
        raise typer.Exit(1)
    if os.path.exists(dirname):
        typer.echo(f"Directory already exists: '{dirname}'")
        raise typer.Exit(1)

    os.mkdir(dirname)
    os.chdir(dirname)
    init()

@_app.command()
def init():
    if len(os.listdir(".")) > 0:
        typer.echo(f"Directory needs to be empty to initialize project.")
        raise typer.Exit(1)
    template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources", "project_template")
    proj_path = Path(".").resolve()
    dir_util.copy_tree(template_path, proj_path.as_posix())

    meta = {}
    curr_path = proj_path
    meta_chain = []
    while True:
        meta_path = curr_path.joinpath("paper_meta.yml")
        if os.path.exists(meta_path):
            metas = list(yaml.safe_load_all(open(meta_path.as_posix())))
            metas = [m for m in metas if m != None]
            if len(metas) > 1:
                typer.echo(f"Found more than one meta document at '{meta_path}'.")
                typer.Exit(1)
            meta_chain.append(metas[0])
        curr_path = curr_path.parent
        if curr_path.as_posix() == curr_path.root:
            break
    meta_chain.reverse()

    for m in meta_chain:
        if not m:
            continue
        merge_dictionary(meta, m)

    with open("paper_meta.yml", "w") as output:
        output.write("---\n")
        yaml.safe_dump(meta, output, sort_keys=False)
        output.write("---\n")

    dev_null = open(os.devnull, 'wb')
    subprocess.call(["git", "init"], stdout=dev_null)
    subprocess.call(["git", "add", "."], stdout=dev_null)
    subprocess.call(["git", "commit", "-m", f"Project creation at {datetime.datetime.now()}"], stdout=dev_null)

def ensure_paper_dir():
    def bail():
        typer.echo("Not in a paper directory.")
        typer.Exit(1)
    if not os.path.exists("./paper_meta.yml") or not os.path.isfile("./paper_meta.yml"):
        bail
    if not os.path.exists("./content") or not os.path.isdir("./content"):
        bail()
    if not os.path.exists("./resources") or not os.path.isdir("./resources"):
        bail()
    file_list = os.listdir("./content")
    if len(file_list) == 0:
        bail()

def get_assignment() -> str:
    meta = list(yaml.safe_load_all(open("./paper_meta.yml")))[0]
    if "assignment" in meta:
        return meta["assignment"]
    else:
        return os.path.basename(os.getcwd())

@_app.command()
def build():
    ensure_paper_dir()

    if not os.path.exists("./out"):
        os.mkdir("./out")

    meta = list(yaml.safe_load_all(open("./paper_meta.yml")))[0]

    if "filename" not in meta:
        author = meta["data"]["author"].split(",")[0].split(" ")[-1]
        mnemonic = re.sub(r"\s", "", meta["class_mnemonic"])
        meta["filename"] = f"{author}_{mnemonic}"
        assignment_underscored = re.sub(r"\s+", "_", get_assignment())
        meta["filename"] += f"_{assignment_underscored}"

    docx_filename = f"./out/{meta['filename']}.docx"

    cmd = ["pandoc",
        "--from=markdown+bracketed_spans",
        "--to=docx",
        "--reference-doc", "./resources/ChicagoStyleTemplate.docx",
        "--output", docx_filename,
        "--metadata-file", "./paper_meta.yml",
    ]

    bib_path_strings = meta.get("sources", [])
    bib_paths = [Path(bps).expanduser().resolve() for bps in bib_path_strings]
    bib_paths = [p for p in bib_paths if p.exists()]

    if len(bib_paths) > 0:
        cmd.extend([
            "--citeproc",
            "--csl", "./resources/chicago-fullnote-bibliography-with-ibid.csl",
        ])
        for bp in bib_paths:
            cmd.extend(["--bibliography", bp])
    else:
        typer.echo("No citation processing.")

    cmd.extend([os.path.join("./content", f) for f in os.listdir("./content")])

    subprocess.call(cmd)

    package(docx_filename, meta)
    make_pdf(docx_filename, meta)


@_app.command()
def wc():
    ensure_paper_dir()


@_app.command()
def save():
    message = typer.prompt("Commit message?")

    dev_null = open(os.devnull, 'wb')
    subprocess.call(["git", "add", "."], stdout=dev_null)
    subprocess.call(["git", "commit", "-m", message], stdout=dev_null)

    dev_null.close()


# doesn't handle branching and stuff
@_app.command()
def push():
    ensure_paper_dir()

    remote = subprocess.check_output(["git", "remote", "-v"])

    if len(remote) == 0:
        meta = list(yaml.safe_load_all(open("./paper_meta.yml")))[0]
        default_repo = f"{meta['class_mnemonic']}_{get_assignment()}"

        repo_name = typer.prompt("What should be the repository name?", default_repo)
        is_private = typer.confirm("Private repository?", True)

        cmd = ["gh", "repo", "create", f"{repo_name}", "--source=.", "--push"]
        if is_private:
            cmd.append("--private")
        subprocess.call(cmd)
    else:
        cmd = ["git", "push"]
        subprocess.call(cmd)
