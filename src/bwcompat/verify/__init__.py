from collections import defaultdict
from dataclasses import (
    dataclass,
)
import fnmatch
import json
import importlib

import pytest


@dataclass
class Importable:
    module: str
    name: str

    def __str__(self):
        return f"{self.module}:{self.name}"


class ModuleImportFrom(pytest.Item):

    def __init__(self, *, target: Importable, **kwargs):
        super().__init__(
            **kwargs,
        )
        self._target = target

    def runtest(self):
        obj = self._target
        src = f"from {obj.module} import {obj.name} as _"
        globals_ = {}
        exec(src, globals_)

    def repr_failure(self, excinfo):
        exc = excinfo.value
        if isinstance(exc, ImportError):
            return f"import failed for {self._target}: {exc!r}"
        return repr(exc)

    def reportinfo(self) -> tuple:
        return str(self._target.module), 0, str(self._target)


class ModuleImport(pytest.Item):
    def __init__(self, *, target: str, **kwargs):
        super().__init__(
            **kwargs,
        )
        self._target = target

    def runtest(self):
        src = f"from {self._target} import *"
        src = f"import {self._target}"
        globals_ = {}
        exec(src, globals_)

    def repr_failure(self, excinfo):
        exc = excinfo.value
        if isinstance(exc, ImportError):
            return f"import failed for {self._target}: {exc!r}"

    def reportinfo(self) -> tuple:
        return str(self._target), 0, str(self._target)


class ImportablesFile(pytest.File):

    def collect(self):
        by_module = defaultdict(list)
        data = json.loads(self.path.read_text())
        for d in data:
            target = Importable(module=d["module_name"], name=d["name"])
            by_module[target.module].append(target)
        
        for module, targets in by_module.items():
            yield ModuleImport.from_parent(name=str(module), target=module, parent=self)
            for target in targets:
                yield ModuleImportFrom.from_parent(name=str(target), target=target, parent=self)


class ActivateRegistry:

    def pytest_addoption(self, parser):
        parser.addoption(
            "--bwcompat-registry",
            dest="bwcompat_registry",
            default=None
        )

    def pytest_configure(self, config):
        self.registry = config.getoption("bwcompat_registry")
        if self.registry:
            from bwcompat.patch import load_registry

            self.registry = load_registry(self.registry)
            self.registry.activate()

    def pytest_unconfigure(self):
        if self.registry:
            self.registry.deactivate()


class TestImportables:

    def pytest_addoption(self, parser):
        parser.addoption(
            "--bwcompat-importables",
            dest="bwcompat_importables_filename",
            default=""
        )

    def pytest_configure(self, config):
        self.filename = config.getoption("bwcompat_importables_filename")

    def pytest_collect_file(self, file_path, parent):
        if fnmatch.fnmatch(file_path.name, self.filename):
            return ImportablesFile.from_parent(path=file_path, parent=parent)
