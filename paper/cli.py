import os
from distutils import dir_util
import shutil
from pathlib import Path
import subprocess
import datetime
import re
import io
import enum

import typer
import yaml
import matplotlib.dates as md
import matplotlib.pyplot as plt
import jsbeautifier

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

@_app.command()
def reinit():
    ensure_paper_dir()

    template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources", "project_template")
    proj_path = Path(".").resolve()
    res_path = proj_path.joinpath("./resources").as_posix()

    shutil.rmtree(res_path)
    shutil.copytree(os.path.join(template_path, "resources"), res_path)

    os.unlink("paper_meta.yml")
    shutil.copy(os.path.join(template_path, "paper_meta.yml"), "paper_meta.yml")
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

class Format(str, enum.Enum):
    docx = "docx"
    docx_pdf = "docx+pdf"
    json = "json"

@_app.command()
def build(output_format: Format = Format.docx):
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

    cmd = ["pandoc",
        "--from=markdown+bracketed_spans",
        "--metadata-file", "./paper_meta.yml",
        "--resource-path", "./content",
    ]

    if output_format in [Format.docx, Format.docx_pdf]:
        output_suffix = "docx"
        cmd.extend([
            "--to=docx",
            "--reference-doc", "./resources/ChicagoStyle-TimesNewRoman_Template.docx",
        ])
    elif output_format == Format.json:
        output_suffix = "json"
        cmd.extend(["--to", "json"])

    output_filename = f"./out/{meta['filename']}.{output_suffix}"
    cmd.extend(["--output", output_filename])

    filter_dir = os.path.join(".", "resources", "filters")
    filters = [f for f in os.listdir(filter_dir) if f.startswith("filter-")]
    filter_cmds = ["--lua-filter" if not toggle else os.path.join(filter_dir, f) for f in filters for toggle in range(2)]
    cmd.extend(filter_cmds)

    bib_path_strings = meta.get("sources", [])
    bib_paths: list[Path] = [Path(bps).expanduser().resolve() for bps in bib_path_strings]
    bib_paths = [p.as_posix() for p in bib_paths if p.exists()]

    if len(bib_paths) > 0:
        cmd.extend([
            "--citeproc",
            "--csl", "./resources/chicago-fullnote-bibliography-with-ibid.csl",
        ])
        cmd.extend(["--bibliography" if not toggle else bp for bp in bib_paths for toggle in range(2)])

        post_filters = [f for f in os.listdir(filter_dir) if f.startswith("post-filter-")]
        post_filter_cmds = ["--lua-filter" if not toggle else os.path.join(filter_dir, f) for f in post_filters for toggle in range(2)]
        cmd.extend(post_filter_cmds)
    else:
        typer.echo("No citation processing.")

    cmd.extend([os.path.join("./content", f) for f in os.listdir("./content") if f.endswith(".md")])

    # print(" ".join(cmd))
    subprocess.check_call(cmd)

    if output_format in [Format.docx, Format.docx_pdf]:
        package(output_filename, meta)
        if output_format == Format.docx_pdf:
            make_pdf(output_filename, meta)
    elif output_format == Format.json:
        opts = jsbeautifier.default_options()
        opts.indent_size = 2
        with open(output_filename, "r") as jsonin:
            output_json = jsonin.read()
        pretty_json = jsbeautifier.beautify(output_json, opts)
        with open(output_filename, "w") as jsonout:
            jsonout.write(pretty_json)

def wc_data() -> dict[str,int]:
    wc_map = {}
    content_files = [f for f in os.listdir("./content") if f.endswith(".md")]
    content_files.sort()
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
        wc_max_buffer = max(goal_wc * 0.05, 100)
        plt.ylim(0, max(ys) + wc_max_buffer)
        yticks = plt.yticks()
        if goal_wc not in yticks[0]:
            plt.yticks(list(yticks[0]) + [goal_wc])

    xmin = min(dates) - 1
    if due_date:
        xmax = max(max(dates), due_date)
    else:
        xmax = max(dates)
    date_range = xmax - xmin
    date_max_buffer = max(date_range * 0.05, 2)
    plt.xlim(xmin, xmax + date_max_buffer)
    xticks = plt.xticks()
    if due_date and due_date not in xticks[0]:
        plt.xticks(list(xticks[0]) + [due_date])
        xticks = list(plt.xticks()[0])
        xticks.sort()
        idx = xticks.index(due_date)
        if idx < len(xticks)-1:
            xticks.pop(idx+1)
        if idx > 0:
            xticks.pop(idx-1)
        plt.xticks(xticks)

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
def save(message: str = typer.Option(..., prompt="Commit message?")):
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
