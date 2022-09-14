from collections import defaultdict
from dataclasses import field, replace
import json
import io
import logging
from pathlib import Path
from typing import (
    Container,
    Dict,
    Iterable,
    List,
    Optional,
)

import pytest
import pydantic
from pydantic.dataclasses import dataclass
import rich
from _pytest.config import Config

from .. import (
    depr,
    module,
    report,
    source,
    util,
    api,
)
from . import (
    checks,
)


_logger = logging.getLogger(__name__)


@dataclass
class Collected:
    
    package: Optional[module.Name] = None
    records: List[depr.Record] = field(default_factory=list)
    paths: List[Path] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.records)

    def __len__(self) -> int:
        return len(self.records)

    def to_json(self) -> str:
        return json.dumps(self, default=pydantic.json.pydantic_encoder, indent=4)

    @classmethod
    def from_json(cls, text: str):
        return pydantic.parse_raw_as(cls, text)


class PluginBase:
    def __init__(
            self,
            save_path="deprector.json",
        ):
        self._save_path = Path(save_path)
        self._session = None


class PytestConfigureError(ValueError):
    pass


class Collect(PluginBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._collected = None
        self._collector = depr.Collector()
        self._collector.activate()

    def configure(self, package: module.Name):
        _logger.debug("package set to %s", package)
        self._collected = Collected()
        self._collected.package = package

        paths_to_match = list(package.submodules_search_paths)
        self._collector.register(*paths_to_match)
        _logger.debug("registered paths %s with collector", paths_to_match)
        # self._collector = depr.Collector(
        #     root_paths=self._root_fpaths
        # )
        # self._collector.activate()

    def pytest_configure(self, config: Config):
        packages = []
        opts = config.option
        if opts.pyargs:
            packages = list(opts.file_or_dir)
            if len(packages) != 1:
                raise PytestConfigureError(f"--pyargs should be specified exactly once; instead found {packages}")
        else:
            raise PytestConfigureError(f"Expected package name given as --pyargs argument, instead got: {config.invocation_params}")
        self.configure(module.Name(packages[0]))

    def store(self, *records: Iterable[depr.Record], **kwargs) -> int:
        added = []
        for rec in records:
            added.append(
                replace(rec, **kwargs)
            )
        n_added = len(added)
        self._collected.records.extend(added)
        _logger.debug("%d new records collected (%d total)", n_added, len(self._collected))
        return n_added

    def save(self):
        if not self._collected:
            _logger.warning("Attempting to save empty data")
        text = self._collected.to_json()
        n_written = self._save_path.write_text(text)
        _logger.info("Collected data saved at %d (%d chars)", self._save_path, n_written)

    def pytest_collect_file(self, file_path: Path):
        self._collected.paths.append(file_path)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtestloop(self, session):
        before_tests = self._collector.archive("pytest_collection")
        self.store(*before_tests, provenance={"pytest": "collection"})
        yield
        n_test_items = len(session.items)
        if n_test_items:
            _logger.info("%d items in test session; %d collected records will be saved", n_test_items, len(self._collected))
            self.save()

    # def pytest_pycollect_makemodule(self, module_path: module.FPath):
    #     ipath = module.get_ipath(module_path, self._root_fpath)
    #     print(f"collecting imports for {ipath}")
    #     recs = depr.get_import_deprs(ipath)
    #     self.store(*recs, provenance={"import": ipath})

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item: pytest.Item, nextitem):
        yield
        test_id = item.nodeid
        to_add = self._collector.archive(test_id)
        self.store(*to_add, provenance={"pytest": test_id})


class Analyze(PluginBase):
    def __init__(self,
            **kwargs,
        ):
        super().__init__(**kwargs)
        self._collected = None
    
        self._registries = []

        self._source_records = []
        self._unmatched = []

        self._by_file = None

    def pytest_configure(self, config):
        rich.print(config.option)
        self.load()

    def configure(self, *registry_keys):
        for key in registry_keys:
            reg = api.get_callsites_registry(key)
            rich.print(reg._paths)
            self._registries.append(reg)
        self.load()

    def load(self):
        _logger.debug("Loading collected data from %s", self._save_path)
        text = self._save_path.read_text()
        assert text
        self._collected = Collected.from_json(text)
        _logger.debug("Loaded %d records from %s", len(self._collected), self._save_path)

        source_records = self.populate_sources(self._collected.records)
        _logger.debug("Detected %d sources", len(source_records))

        by_file = util.groupby(source_records, "filename")
        _logger.debug("Detected %d sources in %d files", len(source_records), len(by_file))

        self._source_records = source_records
        self._by_file = by_file

    def __getitem__(self, key):
        if isinstance(key, Path):
            return self._by_file[str(key)]
        return self._by_file[key]

    def matches_callsite(self, source: depr.Source) -> bool:
        for reg in self._registries:
            if source in reg:
                return True
        return False

    def populate_sources(self,
            records: Iterable[depr.Record],
        ) -> List[report.SourceRecord]:
        source_records = []
        unmatched = []
        for rec in records:
            src = depr.get_primary_source(rec, skip=self.matches_callsite)
            if src is None:
                unmatched.append(rec)
                continue
            src_rec = report.SourceRecord(
                filename=src.filename,
                lineno=src.lineno,
                message=src.message,
                record_id=rec.collection_id,
                provenance=rec.provenance,
            )
            # key = src.filename, src.message
            source_records.append(src_rec)
        if unmatched:
            _logger.warning("%d records could not be matched to a primary source", len(unmatched))
        return source_records

    @pytest.hookimpl(hookwrapper=True)
    def pytest_collection(self, session):
        self._session = session
        yield

    # @pytest.hookimpl(hookwrapper=True)
    def pytest_collect_file(self, parent, file_path: Path):
        if file_path.suffix in {".py"}:
            records = self[file_path]
            return checks.SourceFileChecks.from_parent(
                self._session,
                path=file_path,
                name=str(file_path),
                records=records
            )

    def pytest_collection_modifyitems(self, items):
        our_classes = (checks.SourceLine,)
        _logger.debug("%d items collected by pytest", len(items))
        items[:] = [
            item for item in items
            if isinstance(item, our_classes)
        ]
        _logger.debug("%d items after filtering by keeping types: %s", len(items), our_classes)
        return True
