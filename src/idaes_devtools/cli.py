import typer
from rich import print

from . import __version__


app = typer.Typer(
    rich_markup_mode=True,
    no_args_is_help=True,
)


@app.command()
def main():
    print(f"idaes-devtools, {__version__}")
    raise typer.Exit(0)
