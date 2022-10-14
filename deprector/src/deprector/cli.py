from pathlib import Path
from typing import (
    List,
    Optional,
)

import typer
import pytest
import rich

from . import (
    api,
)
from .pytest_.plugin import (
    Collect,
    Analyze,
)


app = typer.Typer(
    rich_markup_mode=True,
    help="deprector - the DEPRecation detECTOR",
)


PYTEST_OPTS = [
    # "-o", "cli_log=1",
]


@app.command()
def collect(
    package_name: str,
    save_path: Path = typer.Option(
        "deprector.json",
        file_okay=True,
        dir_okay=False,
        exists=False,
        resolve_path=True,
    ),
    pytest_args: Optional[List[str]] = typer.Argument(
        None,
        help="Additional command-line arguments to pass to pytest",
    )
):
    plugin = Collect(
        save_path=save_path
    )
    pytest_args = [
        "--pyargs", package_name,
        "-p", "no:deprector.collect",
        *pytest_args,
        *PYTEST_OPTS,
    ]
    return pytest.main(
        pytest_args,
        plugins=[plugin]
    )

@app.command(
    help="Run `collect` first!"
)
def analyze(
    package_name: str,
    registry: Optional[List[str]] = typer.Option(
        None,
        "-r",
        "--registry",
        "--callsite-registry",
    ),
    save_path: Path = typer.Option(
        "deprector.json",
        file_okay=True,
        dir_okay=False,
        exists=False,
        resolve_path=True,
    )
):
    plugin = Analyze(
        save_path=save_path,
    )
    plugin.configure(
        *registry,
    )
    pytest_args = [
        "--pyargs", package_name,
        "-p", "no:deprector.collect",
        *PYTEST_OPTS,
    ]
    return pytest.main(
        pytest_args,
        plugins=[plugin]
    )


@app.command()
def list_function_calls(
        package_name: str,
        function_name: Optional[List[str]] = typer.Option(
            None,
            "-f",
            "--function-name",
        ),
        check: bool = False,
    ):
    found = api.get_function_calls_in_source(
        package_name,
        list(function_name),
    )
    if check:
        raise typer.Exit(
            0 if not found else 1
        )
    rich.print(found)
