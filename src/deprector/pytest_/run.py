from dataclasses import dataclass
import logging
from pathlib import Path
from typing import (
    List,
    Optional,
)

import pytest

from . import (
    plugin,
)
from .. import (
    errors,
)


_logger = logging.getLogger(__name__)


@dataclass
class Deprector:
    package_name: str
    save_path: Path
    collector: Optional[plugin.Collect] = None
    analyzer: Optional[plugin.Analyze] = None

    def _pytest_args(self, *args):
        return [
            "--pyargs", self.package_name,
            *args,
        ]

    def collect(self, *extra_args: List[str]) -> bool:
        if self.collector is None:
            self.collector = plugin.Collect(save_path=self.save_path)
        args = self._pytest_args(*extra_args)
        code = pytest.main(
            args,
            plugins=[self.collector]
        )
        if code == pytest.ExitCode.NO_TESTS_COLLECTED:
            raise errors.NoTestsCollected(
                f"No tests were collected with the selected args: {args}"
            )
        if code in {pytest.ExitCode.OK, pytest.ExitCode.TESTS_FAILED}:
            _logger.info("pytest run for `collect` completed with code: %s (failures are allowed)", code)
            return False if code == pytest.ExitCode.OK else True
        raise errors.CollectError(
            "pytest run for `collect` completed with error: %s", code
        )

    def analyze(self, *registries: List[str]) -> bool:
        if self.analyzer is None:
            self.analyzer = plugin.Analyze(save_path=self.save_path)
        self.analyzer.configure(*registries)
        args = self._pytest_args()
        code = pytest.main(
            args,
            plugins=[self.analyzer]
        )
        if code in {pytest.ExitCode.OK}:
            _logger.info("pytest run for `analyze` completed without failures")
            return False
        if code in {pytest.ExitCode.TESTS_FAILED}:
            _logger.info("pytest run for `analyze` completed with failures")
            return True
        raise errors.AnalyzeError(
            "pytest run for `analyze` completed with error: %s", code
        )
