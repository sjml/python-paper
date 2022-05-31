import typer

from .formats import Format
from .shared import PAPER_STATE

_app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
)


def main():
    _app()


@_app.callback()
def paper(verbose: bool = False):
    """\b
    Shane’s little paper-{writing|managing|building} utility
        <https://github.com/sjml/paper>
    """
    PAPER_STATE["verbose"] = verbose


@_app.command()
def new(project_name: str):
    """
    Create the scaffolding for a new writing/research project.
    """
    from .project_setup import new

    new(project_name)


@_app.command()
def init():
    """
    While in an empty directory, set it up for a project.
    (Called as part of the process for `new`.)
    """
    from .project_setup import init

    init()


@_app.command()
def dev():
    """
    Set up a project for development work on paper itself.
    Deletes the local `.paper_resources` directory and symlinks
    the template’s version, so changes here affect the actual program.
    """
    from .project_setup import dev

    dev()


@_app.command()
def build(output_format: Format = typer.Option(None)):
    """
    Generate versions of the paper ready for submission.
    """
    from .build import build

    build(output_format)


@_app.command()
def fmt(wrap: bool = True, columns: int = 80):
    """
    Run an automated formatter on all the local Markdown files.
    """
    from .mdfmt import fmt

    fmt(wrap, columns)


@_app.command()
def wc():
    """
    Print word count metrics for the project.
    """
    from .wc import wc

    wc()


@_app.command()
def save(message: str = typer.Option(..., prompt="Commit message?")):
    """
    Make a git commit with some extra tracking data.
    """
    from .save import save

    save(message)


@_app.command()
def push():
    """
    Push local git changes to the remote repository.
    """
    from .save import push

    push()


@_app.command()
def web():
    """
    Open the remote repository’s GitHub site.
    """
    from .save import web

    web()
