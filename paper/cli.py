import os
from distutils import dir_util
from pathlib import Path
import subprocess
import datetime
import re
import http.client

import typer
import yaml

from . import LIB_NAME, LIB_VERSION
from .util import merge_dictionary
from .doc_handling import package

VERSION_STRING = f"{LIB_NAME} v{LIB_VERSION}"

_app = typer.Typer()

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
    proj_path = Path(".").absolute()
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
        curr_path = curr_path.parent
        if curr_path.as_posix() == curr_path.root:
            break
        meta_chain.append(metas[0])
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
        if "assignment" in meta:
            assignment = re.sub(r"\s+", "_", meta["assignment"])
            meta["filename"] += f"_{assignment}"

    docx_filename = f"./out/{meta['filename']}.docx"

    cmd = [ "pandoc",
        "--from=markdown+bracketed_spans",
        "--to=docx",
        "--reference-doc", "./resources/ChicagoStyleTemplate.docx",
        "--output", docx_filename,
        "--metadata-file", "./paper_meta.yml",
    ]

    bib_path = "./sources.biblatex"
    if not os.path.exists(bib_path):
        # try to snag it?
        hc = http.client.HTTPConnection("127.0.0.1", port=23119)
        url = "/better-bibtex/export/library?/1/library.biblatex"

        try:
            hc.request("GET", url)
            resp = hc.getresponse()
            code = resp.getcode()
            if code != 200:
                raise RuntimeError()
            source_text = resp.read()
            with open(bib_path, "w") as output:
                output.write(source_text)
        except ConnectionError:
            typer.echo("No library export and Zotero is not running.")
    if os.path.exists(bib_path):
        cmd.extend([
            "--citeproc",
            "--bibliography", bib_path,
            "--csl", "./resources/chicago-fullnote-bibliography-with-ibid.csl",
        ])
    else:
        typer.echo("No citation processing.")

    cmd.extend([os.path.join("./content", f) for f in os.listdir("./content")])

    subprocess.call(cmd)

    package(docx_filename, meta)

@_app.command()
def wc():
    ensure_paper_dir()

@_app.command()
def push():
    ensure_paper_dir()

def main():
    _app()
