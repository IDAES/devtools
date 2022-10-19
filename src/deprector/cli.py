import enum
import logging
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
    pytest_,
    errors,
)


_logger = logging.getLogger(__name__)


class ExitCode(enum.IntEnum):
    ZERO_DETECTED = 0
    DETECTED = 1
    COLLECT_ERROR = 2
    ANALYZE_ERROR = 3
    OTHER_ERROR = 4


def _exit_with(code: ExitCode):
    _logger.info("deprector will now exit with code %s", repr(code))
    raise typer.Exit(int(code))


app = typer.Typer(
    rich_markup_mode=True,
    help="deprector - the DEPRecation detECTOR",
)


def _config_logging(verbose=None):
    from rich.logging import RichHandler
    logging.basicConfig(
        level=logging.INFO if not verbose else logging.DEBUG,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()]
    )


class Step(str, enum.Enum):
    collect = "collect"
    analyze = "analyze"


@app.command()
def run(
    package_name: str,
    verbose: bool = typer.Option(
        False,
        "-v", "--verbose",
    ),
    save_path: Path = typer.Option(
        "deprector.json",
        file_okay=True,
        dir_okay=False,
        exists=False,
        resolve_path=True,
    ),
    step: List[Step] = typer.Option(
        [Step.collect, Step.analyze],
        "-s",
        "--step",
        help="Specify the individual step(s) to be run (default: all)",
    ),
    pytest_args: Optional[List[str]] = typer.Argument(
        None,
        help="Additional command-line arguments to pass to pytest",
    ),
    registry: Optional[List[str]] = typer.Option(
        None,
        "-r",
        "--registry",
        "--callsite-registry",
    ),
):
    _config_logging(verbose=verbose)
    runner = pytest_.Deprector(
        package_name=package_name,
        save_path=save_path,
    )
    steps_to_run = set(step)
    results = {}
    try:
        if Step.collect in steps_to_run:
            _logger.info("Running step 'collect'")
            results[Step.collect] = runner.collect()
        if Step.analyze in steps_to_run:
            _logger.info("Running step 'analyze'")
            results[Step.analyze] = runner.analyze()
    except errors.CollectError:
        _logger.exception("Error during 'collect' step")
        _exit_with(ExitCode.COLLECT_ERROR)
    except errors.AnalyzeError:
        _logger.exception("Error during 'analyze' step")
        _exit_with(ExitCode.ANALYZE_ERROR)
    except Exception as e:
        _logger.exception("An unspecified error occurred")
        _exit_with(ExitCode.OTHER_ERROR)

    if Step.analyze not in results:
        _logger.info("Run complete without step 'analyze'")
        _exit_with(0)

    any_detected = results[Step.analyze]
    if any_detected:
        _logger.info("One or more deprecations detected")
        _exit_with(ExitCode.DETECTED)
    else:
        _logger.info("No deprecations detected")
        _exit_with(ExitCode.ZERO_DETECTED)


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
