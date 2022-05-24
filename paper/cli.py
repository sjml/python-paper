import typer

from .formats import Format

_app = typer.Typer()
def main():
    _app()

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
def build(output_format: Format = Format.docx):
    from .build import build
    build(output_format)

@_app.command()
def wc():
    from .save import wc
    wc()

@_app.command()
def save(message: str = typer.Option(..., prompt="Commit message?")):
    from .save import save
    save(message)

@_app.command()
def push():
    from .save import push
    push()
