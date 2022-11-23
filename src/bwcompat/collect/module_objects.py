from dataclasses import (
    dataclass,
    field,
    asdict,
)
import fnmatch
import json
import importlib
import importlib.util
import inspect
import logging
from pathlib import Path
import pickle
import subprocess
import sys
import textwrap
from typing import (
    Callable,
    Iterable,
    List,
)
from types import ModuleType


_logger = logging.getLogger(__name__)



def _matches_any(s: str, patterns: Iterable[str]) -> bool:
    return any(
        fnmatch.fnmatch(s, pat)
        for pat in patterns
    )


def _skip_nothing(*args):
    return False


@dataclass
class ObjectInModule:
    name: str
    module_name: str
    module_file: str
    type_name: str

    dunder_module_name: str = None
    dunder_doc: str = field(default="", repr=False)
    source_text: str = field(default="", repr=False)
    source_lineno: int = 0

    @classmethod
    def to_json(cls, items, **kwargs) -> str:
        data = [
            asdict(item)
            for item in items
        ]
        return json.dumps(data, default=str, **kwargs)

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        if isinstance(data, dict):
            yield cls(**data)
        elif isinstance(data, list):
            yield from (
                cls(**datum)
                for datum in data
            )
        else:
            raise ValueError(f"Unsupported json for {cls}: {json_str}")

    @classmethod
    def from_module_object(cls, mod: ModuleType, name: str, obj: object):
        self = cls(
            name=name,
            module_name=mod.__name__,
            type_name=type(obj).__name__,
            module_file=mod.__file__,
        )
        dunder_module = getattr(obj, "__module__", None)
        if dunder_module:
            self.dunder_module_name = str(dunder_module)
            # self.dunder_doc = obj.__doc__
        return self


def _is_part_of_test_suite(name: str):
    return _matches_any(
        name,
        [
            "*.test_*",
            "*.conftest",
        ]
    )


def _find_modules_in_dir(
        dirpath: Path,
        root: Path = None,
        sep: str =".",
        suffixes=frozenset([".py"]),
    ) -> Iterable[str]:
    if root is None:
        root = dirpath.parent
    relpath = dirpath.relative_to(root)
    for path in dirpath.glob("*"):
        if path.is_dir():
            yield from _find_modules_in_dir(path, root)
        if path.suffix not in suffixes:
            continue
        stem = path.stem
        if stem == "__main__":
            continue
        parts = list(relpath.parts)
        if stem != "__init__":
            parts.append(stem)
        yield sep.join(parts)


def _find_modules(pkg_name: str) -> List[str]:
    spec = importlib.util.find_spec(pkg_name)
    dir_paths = [Path(loc) for loc in spec.submodule_search_locations]
    found = []
    for dir_path in dir_paths:
        found.extend(_find_modules_in_dir(dir_path))
    return sorted(set(found))


def collect(pkg_name: str, collector: Callable, skip: Callable = _skip_nothing):
    collected = []
    for name in _find_modules(pkg_name):
        if skip(name): continue
        try:
            mod = importlib.import_module(name)
            res = collector(mod)
        except ImportError as e:
            _logger.error("Could not import %s: %s", mod, repr(e))
            continue
        except Exception as e:
            _logger.error("Could not collect information from %s using %s: %s", mod, collector, repr(e))
            continue
        else:
            collected.extend(res)
    return collected


@dataclass
class DefinedInPackage:
    prefix: str

    def __call__(self, mod: ModuleType) -> Iterable[ObjectInModule]:
        for obj_name, obj in mod.__dict__.items():
            if getattr(obj, "__module__", "").startswith(self.prefix):
                yield ObjectInModule.from_module_object(mod, obj_name, obj)


def main(args=None):
    args = args or sys.argv[1:]
    package = args[0]
    script_name = __spec__.name

    collected = collect(
        package,
        collector=DefinedInPackage(package),
        skip=_is_part_of_test_suite,
    )

    outpath = Path(f"{package}-{script_name}.json")
    outpath.write_text(ObjectInModule.to_json(collected, indent=4))


if __name__ == '__main__':
    main()
