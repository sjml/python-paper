import os
from distutils import dir_util
from pathlib import Path
import subprocess
import datetime
import re
import io

import typer
import yaml
import matplotlib.dates as md
import matplotlib.pyplot as plt

from . import LIB_NAME, LIB_VERSION
from .util import merge_dictionary
from .doc_handling import package, make_pdf

VERSION_STRING = f"{LIB_NAME} v{LIB_VERSION}"

METADATA_START_SENTINEL = "<!-- begin paper metadata -->"
METADATA_END_SENTINEL   = "<!-- end paper metadata -->"

_app = typer.Typer()
def main():
    _app()

def get_metadata() -> dict:
    data = list(yaml.safe_load_all(open("./paper_meta.yml")))[0]
    if "data" not in data:
        data["data"] = {}
    if "date" not in data["data"] or data["data"]["date"] == "[DATE]":
        data["data"]["date"] = None
    else:
        date = datetime.datetime.fromisoformat(data["data"]["date"])
        data["data"]["date"] = date
    return data

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

    with open(os.devnull, 'wb') as dev_null:
        subprocess.call(["git", "init"], stdout=dev_null)
        subprocess.call(["git", "add", "."], stdout=dev_null)
        subprocess.call(["git", "commit", "-m", f"Initial project creation"], stdout=dev_null)

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
    meta = get_metadata()
    if "assignment" in meta:
        return meta["assignment"]
    else:
        return os.path.basename(os.getcwd())

@_app.command()
def build():
    ensure_paper_dir()

    if not os.path.exists("./out"):
        os.mkdir("./out")

    meta = get_metadata()

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
        "--reference-doc", "./resources/ChicagoStyle-TimesNewRoman_Template.docx",
        "--output", docx_filename,
        "--metadata-file", "./paper_meta.yml",
        "--resource-path", "./content",
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

    cmd.extend([os.path.join("./content", f) for f in os.listdir("./content") if f.endswith(".md")])

    subprocess.call(cmd)

    package(docx_filename, meta)
    make_pdf(docx_filename, meta)

def wc_data() -> dict[str,int]:
    wc_map = {}
    content_files = os.listdir("./content")
    for cf in content_files:
        cf_path = os.path.join("./content", cf)
        contents = open(cf_path, "r").read().strip()
        if contents.startswith("---\n"):
            contents = contents.split("---\n")[2]
        wc_map[cf] = len(contents.split())
    return wc_map

def wc_string() -> str:
    wc_map = wc_data()
    filename_max_len = max(*[len(fn)+2 for fn in wc_map.keys()], len("Files"), len("**TOTAL**"))
    wc_max_len = max(*[len(str(wc)) for wc in wc_map.values()], len("Word Count"))

    output = "## Current word count:\n"
    output += f"| {'File':<{filename_max_len}} | {'Word Count':<{wc_max_len}} |\n"
    output += f"| {'':-<{filename_max_len}} | {'':-<{wc_max_len}} |\n"
    for f, wc in wc_map.items():
        output += f"| {f'`{f}`':<{filename_max_len}} | {wc:<{wc_max_len}} |\n"
    output += f"| {'**TOTAL**':<{filename_max_len}} | {sum(wc_map.values()):<{wc_max_len}} |"
    return output

@_app.command()
def wc():
    ensure_paper_dir()

    print(wc_string())
    print()

def get_commit_data() -> list[dict[str,str|int|None]]:
    log = subprocess.check_output(["git",
        "log",
        '--format=%P|||%ct|||%B||-30-||',
    ]).decode("utf-8").strip()
    commits_raw = [c.strip() for c in log.split("||-30-||") if len(c) > 0]
    commits = []
    for c in commits_raw:
        git_hash, timestamp, message = c.split("|||")
        wc = None
        wcs = re.findall(r"\[WC: (\d+)]", message)
        if len(wcs) == 1:
            wc = int(wcs[0])
        if len(git_hash) == 0:
            git_hash = None
        commits.append({
            "hash": git_hash,
            "timestamp": int(timestamp),
            "message": message,
            "word_count": wc
        })
    return commits

def get_progress_image_str() -> str:
    commits = get_commit_data()
    commits.reverse()
    dates = [datetime.datetime.fromtimestamp(c["timestamp"]) for c in commits]
    dates.append(datetime.datetime.now())
    dates = md.date2num(dates)
    wcs = [c["word_count"] for c in commits]
    wcs = [c if isinstance(c, int) else 0 for c in wcs]
    wcs.append(sum(wc_data().values()))

    meta = get_metadata()
    due_date = meta["data"]["date"]
    if due_date:
        due_date = md.date2num(due_date)
    goal_wc = meta.get("target_word_count", None)

    plt.rcParams['font.family'] = 'sans-serif'
    fig, ax = plt.subplots()
    xfmt = md.DateFormatter("%h\n%d\n%Y")
    ax.xaxis.set_major_formatter(xfmt)
    ys = wcs.copy()
    if goal_wc:
        ys.append(goal_wc)
    plt.ylim(0, max(ys) + 100)
    if due_date:
        plt.xlim(min(dates) - 1, max(max(dates), due_date) + 1)
    else:
        plt.xlim(min(dates) - 1, max(dates) + 1)

    plt.title("Progress")
    ax.set_ylabel("Word Count")
    ax.plot(dates, wcs)
    if goal_wc:
        ax.axhline(goal_wc, color="green")
    if due_date:
        ax.axvline(due_date, color="red")
    fig.tight_layout()

    plt.rcParams['svg.fonttype'] = 'none'
    svg = io.BytesIO()
    fig.savefig(svg, format="svg")
    svg_str = svg.getvalue().decode("utf-8")

    proper_font_str = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji'"
    svg_str = svg_str.replace("'sans-serif'", proper_font_str)

    return svg_str

@_app.command()
def save():
    ensure_paper_dir()

    meta = get_metadata()

    if not os.path.exists("./README.md"):
        with open("./README.md", "w") as readme:
            readme.write(f"# {meta['class_mnemonic']}: {get_assignment()}\n\n")
            readme.write(f"{METADATA_START_SENTINEL}\n")
            readme.write(f"{METADATA_END_SENTINEL}\n")

    readme_text = open("./README.md", "r").read()
    readme_before = readme_text[:readme_text.index(METADATA_START_SENTINEL)]
    readme_before = f"{readme_before}{METADATA_START_SENTINEL}\n"
    readme_after = readme_text[readme_text.index(METADATA_END_SENTINEL)+len(METADATA_END_SENTINEL):]
    readme_after = f"\n{METADATA_END_SENTINEL}{readme_after}"

    with open("./progress.svg", "w") as progress:
        progress.write(get_progress_image_str())

    readme_text = f"{readme_before}{wc_string()}\n\n![WordCountProgress](./progress.svg){readme_after}"
    with open("./README.md", "w") as readme:
        readme.write(readme_text)

    message = typer.prompt("Commit message?")
    wc = wc_data();
    total = sum(wc.values())
    message += f"\n\n[WC: {total}]"
    with open(os.devnull, 'wb') as dev_null:
        subprocess.call(["git", "add", "."], stdout=dev_null)
        subprocess.call(["git", "commit", "-m", message], stdout=dev_null)


# doesn't handle branching and stuff
@_app.command()
def push():
    ensure_paper_dir()

    remote = subprocess.check_output(["git", "remote", "-v"])

    if len(remote) == 0:
        meta = get_metadata()
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
