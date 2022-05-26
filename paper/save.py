import os
import io
import json
import subprocess
from datetime import datetime

import typer
import matplotlib.dates as md
import matplotlib.pyplot as plt

from .util import ensure_paper_dir, get_metadata, get_assignment, get_content_file_list
from .wc import _wc_data, _wc_json, _wc_string

METADATA_START_SENTINEL = "<!-- begin paper metadata -->"
METADATA_END_SENTINEL   = "<!-- end paper metadata -->"

def _get_commit_data() -> list[dict[str,str|int|None]]:
    log = subprocess.check_output(["git",
        "log",
        '--format=%P|||%ct|||%B||-30-||',
    ]).decode("utf-8").strip()
    commits_raw = [c.strip() for c in log.split("||-30-||") if len(c) > 0]
    commits = []
    for c in commits_raw:
        git_hash, timestamp, message = c.split("|||")
        wc = None
        wc_splits = message.split("\nPAPER_DATA\n")
        if len(wc_splits) < 2:
            continue
        try:
            wc_data = json.loads(wc_splits[1])
        except json.JSONDecodeError:
            continue
        wc = wc_data["total"]
        if len(git_hash) == 0:
            git_hash = None
        commits.append({
            "hash": git_hash,
            "timestamp": int(timestamp),
            "message": message,
            "word_count": wc
        })
    return commits

def _get_progress_image_str() -> str:
    commits = _get_commit_data()
    commits.reverse()
    dates = [datetime.fromtimestamp(c["timestamp"]) for c in commits]
    dates.append(datetime.now())
    dates = md.date2num(dates)
    wcs = [c["word_count"] for c in commits]
    wcs = [c if isinstance(c, int) else 0 for c in wcs]
    wcs.append(sum(_wc_data().values()))

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


def save(message: str = typer.Option(..., prompt="Commit message?")):
    ensure_paper_dir()

    meta = get_metadata()

    if not os.path.exists("./README.md"):
        with open("./README.md", "w") as readme:
            readme.write(f"# {meta['data']['class_mnemonic']}: {get_assignment()}\n\n")
            readme.write(f"{METADATA_START_SENTINEL}\n")
            readme.write(f"{METADATA_END_SENTINEL}\n")

    readme_text = open("./README.md", "r").read()
    readme_before = readme_text[:readme_text.index(METADATA_START_SENTINEL)]
    readme_before = f"{readme_before}{METADATA_START_SENTINEL}\n"
    readme_after = readme_text[readme_text.index(METADATA_END_SENTINEL)+len(METADATA_END_SENTINEL):]
    readme_after = f"\n{METADATA_END_SENTINEL}{readme_after}"

    with open("./progress.svg", "w") as progress:
        progress.write(_get_progress_image_str())

    readme_text = f"{readme_before}{_wc_string()}\n\n![WordCountProgress](./progress.svg){readme_after}"
    with open("./README.md", "w") as readme:
        readme.write(readme_text)

    message += f"\n\nPAPER_DATA\n{_wc_json()}"
    with open(os.devnull, 'wb') as dev_null:
        subprocess.call(["git", "add", "."], stdout=dev_null)
        subprocess.call(["git", "commit", "-m", message], stdout=dev_null)

def push():
    ensure_paper_dir()

    remote = subprocess.check_output(["git", "remote", "-v"])

    if len(remote) == 0:
        meta = get_metadata()
        default_repo = f"{meta['data']['class_mnemonic']}_{get_assignment()}"

        repo_name = typer.prompt("What should be the repository name?", default_repo)
        is_private = typer.confirm("Private repository?", True)

        cmd = ["gh", "repo", "create", f"{repo_name}", "--source=.", "--push"]
        if is_private:
            cmd.append("--private")
        subprocess.call(cmd)
    else:
        cmd = ["git", "push"]
        subprocess.call(cmd)
