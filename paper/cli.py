import typer

from .formats import Format
from .shared import PAPER_STATE

_app = typer.Typer()
def main():
    _app()

@_app.callback()
def paper(verbose: bool = False):
    """
    Shane's little paper-writing utility.
    """
    PAPER_STATE["verbose"] = verbose

@_app.command()
def new(project_name: str):
    from .project_setup import new
    new(project_name)

@_app.command()
def init():
    from .project_setup import init
    init()

@_app.command()
def reinit():
    from .project_setup import reinit
    reinit()

@_app.command()
def dev():
    from .project_setup import dev
    dev()

@_app.command()
def build(output_format: Format = "docx"):
    from .build import build
    build(output_format)

@_app.command()
def wc():
    from .wc import wc
    wc()

@_app.command()
def save(message: str = typer.Option(..., prompt="Commit message?")):
    from .save import save
    save(message)

@_app.command()
def push():
    from .save import push
    push()
