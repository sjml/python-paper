import os
import shutil
from pathlib import Path
import subprocess

import typer
import yaml

from .util import merge_dictionary, ensure_paper_dir, get_paper_version_stamp


def new(project_name: str):
    typer.echo(f"Starting new project called '{project_name}'...")
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


def init():
    if len(os.listdir(".")) > 0:
        typer.echo(f"Directory needs to be empty to initialize project.")
        raise typer.Exit(1)
    template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources", "project_template")
    proj_path = Path(".").resolve()
    shutil.copytree(template_path, proj_path.as_posix(), dirs_exist_ok=True)

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
                raise typer.Exit(1)
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

    os.mkdir("research")

    with open(os.devnull, "wb") as dev_null:
        subprocess.call(["git", "init"], stdout=dev_null)
        subprocess.call(["git", "add", "."], stdout=dev_null)
        subprocess.call(["git", "commit", "-m", f"Initial project creation\n---\n{get_paper_version_stamp()}"], stdout=dev_null)


def dev():
    ensure_paper_dir()

    template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources", "project_template")
    src_res_path = os.path.join(template_path, ".paper_resources")
    proj_path = Path(".").resolve()
    dst_res_path = proj_path.joinpath("./.paper_resources").as_posix()

    if os.path.islink(dst_res_path):
        if Path(dst_res_path).resolve() == Path(src_res_path).resolve():
            typer.echo("Looks like this project is already set up for dev!")
            raise typer.Exit(1)

    typer.echo("This symlinks the package resource directory to this local one, deleting the local version.")
    typer.echo("It's meant for development on paper itself.")
    do_it = typer.confirm("Is that what you're up to?")
    if do_it:
        shutil.rmtree(dst_res_path)
        os.symlink(os.path.relpath(src_res_path, "."), dst_res_path)
