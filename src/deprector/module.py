from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
import importlib
from importlib.machinery import (
    ModuleSpec,
    PathFinder,
    FileFinder,
    SourceFileLoader,
)
import logging
from operator import attrgetter
import os
from pathlib import Path, PurePath
import sys
from types import (
    ModuleType,
)
from typing import (
    Iterable,
    List,
    NewType,
    Optional,
    Protocol,
    Set,
    Tuple,
    Union,
)

from . import (
    util
)


_logger = logging.getLogger(__name__)


SysPath = NewType("SysPath", Path)
"A pathlib.Path object for the absolute path to one of the directories in sys.path"


NAME_SEPARATOR = "."
SOURCE_SUFFIX = ".py"


def _get_internal_syspaths() -> List[Path]:
    base = Path(os.__file__).parent
    assert base.is_dir()
    return [
        base,
        base / "lib-dynload",
        Path(sys.executable).parent,
    ]


_INTERNAL_SYSPATHS = frozenset(_get_internal_syspaths())


@lru_cache
def _get_startup_sys_path() -> List[str]:
    "Use this instead of sys.path since sys.path can be modified by e.g. pytest"

    from subprocess import check_output
    import json

    args = [
        sys.executable,
        "-c", "import sys; import json; print(json.dumps(sys.path))",
    ]
    out = check_output(args, text=True)
    return json.loads(out.strip())


def _compare_with_current_sys_path(reference_sys_path: List[str]):
    ref = list(reference_sys_path)
    added = set(sys.path) - set(ref)
    if added:
        _logger.info(
            "The current sys.path has entries that are not present at startup: %s. "
            "This is likely due to pytest and is considered normal. "
            "The extra entries will be ignored by the functionality in the %s module.",
            sorted(added),
            __name__,
        )


@lru_cache
def _get_syspaths(
        exclude_internal: bool = True,
        exclude_cwd: bool = True,
    ) -> List[Path]:
    orig_syspaths = list(_get_startup_sys_path())
    _compare_with_current_sys_path(orig_syspaths)

    syspaths = []
    for path in orig_syspaths:
        path = Path(path)
        if not path.is_dir(): continue
        if exclude_cwd and path == Path():
            continue
        if exclude_internal and path in _INTERNAL_SYSPATHS:
            continue
        syspaths.append(path)
    return syspaths


class PureName(str):
    "pathlib.Path-lib manipulation for module names"
    Parts = Tuple[str, ...]

    def __new__(cls, *parts):
        parts = cls._ensure_parts(parts)
        cls._validate(parts)

        joined = cls._join(parts)
        self = super().__new__(cls, joined)
        self._parts = parts
        return self

    @classmethod
    def _split(cls, s: str) -> Parts:
        return tuple(s.split(NAME_SEPARATOR))

    @classmethod
    def _join(cls, parts: Parts) -> str:
        return NAME_SEPARATOR.join(parts)

    @classmethod
    def _ensure_parts(cls, parts) -> Parts:
        if not parts:
            raise ValueError(f"{parts} must not be empty")
        if len(parts) == 1:
            val = parts[0]
            if isinstance(val, str):
                parts = cls._split(val)
            elif isinstance(val, cls):
                parts = cls.parts
        return tuple(parts)

    @classmethod
    def _validate(cls, parts):
        if not _all_identifiers(parts):
            _logger.warning(f"{parts} contains invalid identifiers")

    @property
    def parts(self):
        return self._parts

    def __len__(self):
        return len(self._parts)

    def __iter__(self):
        return iter(self._parts)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __le__(self, other) -> bool:
        return self._parts < other._parts

    def __repr__(self):
        c = self.__class__.__name__
        joined = str(self)
        return f"<{c}('{joined}')>"

    def _create(self, *args):
        return type(self)(*args)

    def _with_added_parts(self, *new_parts):
        return self._create(*self._parts, *new_parts)

    def __getitem__(self, key):
        if isinstance(key, str):
            new_parts = type(self)._split(key)
            return self._with_added_parts(new_parts)

        if isinstance(key, slice):
            return self._create(*self._parts[key])

        return self._parts[key]

    @property
    def is_root(self):
        return len(self) == 1

    @property
    def parent(self):
        if self.is_root:
            return None
        return self[:-1]

    @property
    def parents(self):
        if self.is_root:
            return []
        return [
            self[:n_to_take]
            for n_to_take in range(len(self) - 1, 0, -1)
        ]

    @property
    def lineage(self):
        "Sequence of ancestors starting from root and ending with self"
        return [
            self[:n_to_take]
            for n_to_take in range(1, len(self) + 1)
        ]

    @property
    def root(self):
        if self.is_root:
            return self
        return self[:1]

    @property
    def relative_to_root(self):
        if self.is_root:
            raise ValueError(f"{self} is already root")
        return self[1:]

    def _to_relpath(self) -> PurePath:
        return PurePath(*self)

    def __fspath__(self) -> str:
        return self._to_relpath()

    @classmethod
    def from_relpath(cls, path: Union[PurePath, str]):
        path = Path(path).with_suffix("")
        if path.name in {"__init__"}:
            path = path.parent
        if path.is_absolute():
            raise ValueError("Only relative paths are supported")
        return cls(*path.parts)


class ModuleSpecNotFound(ModuleNotFoundError):
    pass


class ImportlessFinder(importlib.abc.MetaPathFinder):

    def __init__(self):
        self._finder_cache = {}
        self._spec_cache = {}

    def _store_spec(self, name: PureName, spec: ModuleSpec):
        _logger.debug("storing spec for %s", name)
        self._spec_cache[name] = spec
        locs = spec.submodule_search_locations or []
        for loc in locs:
            self._finder_cache[loc] = FileFinder(loc, (SourceFileLoader, [SOURCE_SUFFIX]))

    def _find_spec_from_cached_parent(self, name: PureName):
        parent_spec = self._spec_cache[name.parent]
        for loc in parent_spec.submodule_search_locations:
            finder = self._finder_cache[loc]
            spec = finder.find_spec(name)
            if spec is not None:
                return spec

    def _find_spec(self, name: PureName):

        if name.is_root:
            finder = PathFinder.find_spec
        else:
            finder = self._find_spec_from_cached_parent
        spec = finder(name)
        self._store_spec(name, spec)
        return spec

    def find_spec(self, name: PureName, target=None):
        try:
            found = self._spec_cache[name]
        except KeyError:
            _logger.debug("%s not found in cache", name)
            pass
        else:
            _logger.debug("%s found in cache", name)
            return found

        missing = [name]
        for parent in name.parents:
            spec = self._spec_cache.get(parent, None)
            if spec is not None:
                break
            else:
                missing.append(parent)

        missing_rooter_first = missing[::-1]
        for name in missing_rooter_first:
            spec = self._find_spec(name)

        assert spec.name == name, (spec, name)
        return spec

    def invalidate_caches(self):
        for d in [
            self._finder_cache,
            self._spec_cache,
        ]:
            d.clear()


_FINDER = ImportlessFinder()


class Name(PureName):
    "Concrete subclass implementing operations that interact with the filesystem and/or the import machinery"

    def __new__(
            cls,
            *args,
        ):
        pure = PureName(*args)
        try:
            spec = _FINDER.find_spec(pure)
            assert spec, "spec was not found"
        except Exception as e:
            _logger.exception("Spec not found for %s", pure)
            raise e
            return pure

        self = super().__new__(cls, *args)
        self._spec = spec
        return self

    def exists(self):
        return self._spec is not None

    @property
    def spec(self) -> ModuleSpec:
        return self._spec

    def is_package(self):
        if not self.spec: return None
        return self.spec.submodule_search_locations and self.spec.origin

    def is_namespace_package(self):
        if not self.spec: return None
        return self.spec.submodule_search_locations and self.spec.origin

    def has_file(self):
        if not self.spec: return None
        return bool(self.spec.origin)

    @property
    def origin(self):
        if not self.spec: return None
        return Path(self.spec.origin)

    @property
    def submodules_search_paths(self):
        if not self.spec: return None
        return [
            Path(loc)
            for loc in self._spec.submodule_search_locations or []
        ]

    def import_module(self) -> ModuleType:
        return importlib.import_module(str(self))

    def check_imported(self) -> bool:
        return str(self) in sys.modules


def _find_matching_syspath(path: Path):

    def _get_matching_relpath(syspath):
        if (syspath / path).exists():
            return path

    def _get_matching_abspath(syspath):
        try:
            relpath = path.relative_to(syspath)
        except ValueError as err:
            pass
        else:
            return relpath

    found: Set[Tuple[SysPath, Path]] = set()
    get_matching = _get_matching_abspath if path.is_absolute() else _get_matching_relpath
    syspaths = list(_get_syspaths(exclude_internal=True, exclude_cwd=True))
    for syspath in syspaths:
        relpath = get_matching(syspath)
        if relpath:
            found.add((syspath, relpath))

    assert len(found) == 1, f"Expected 1 found for {path}, instead found {found}"
    return found.pop()


def _all_identifiers(parts: Iterable[str]) -> bool:
    return all(
        part.isidentifier()
        for part in parts
    )


class SourceFile:

    def __new__(cls, path, module=None):
        path = Path(path)
        if path.suffix not in {"", SOURCE_SUFFIX}:
            raise ValueError(f"Not a source file: {path}")
        syspath, relpath = _find_matching_syspath(path)
        module_name = Name.from_relpath(relpath)
        if not module:
            module = Name.from_relpath(relpath)

        abspath = syspath / relpath
        self = super().__new__(cls)
        self._path = abspath
        self._module = module

        self._syspath = syspath
        self._relative_to_syspath = relpath
        return self

    @property
    def path(self) -> Path:
        return self._path

    @property
    def module(self) -> Name:
        return self._module

    def __str__(self):
        return str(self.path)

    @property
    def _cmp(self):
        return (self.path, str(self.module))

    def __hash__(self):
        return hash(self._cmp)

    def __fspath__(self):
        return str(self.path)

    def __repr__(self):
        cn = self.__class__.__name__
        return f"{cn}('{self.relative_to_syspath}', from '{self.syspath}')"

    def __format__(self, spec) -> str:
        format_map = {
            "m": attrgetter("module"),
            "p": attrgetter("path"),
            "r": attrgetter("relative_to_syspath"),
            "": os.fspath,
        }
        try:
            return str(format_map[spec](self))
        except KeyError:
            raise ValueError(f"Unsupported format specification {spec} (supported: {format_map})")

    @property
    def syspath(self) -> Path:
        return self._syspath

    @property
    def _cmp(self) -> Tuple:
        return self.path, self.module

    def hash(self) -> int:
        return hash(self._cmp)

    def __eq__(self, other) -> bool:
        return self._cmp == other._cmp

    def __lt__(self, other) -> bool:
        return self._cmp < other._cmp

    @property
    def relative_to_syspath(self) -> Path:
        return self._relative_to_syspath

    def read_text(self):
        return self.path.read_text()

    @classmethod
    def from_module(cls, name: Union[Name, str]):
        name = Name(name)
        return cls(
            path=Path(name.spec.origin),
            module=name,
        )

    @classmethod
    def find_in_package(cls, name: Union[str, Name], suffix=SOURCE_SUFFIX):
        package_name = Name(name)
        for dirpath in package_name.submodules_search_paths:
            for fpath in dirpath.rglob(f"*{suffix}"):
                yield cls(fpath)


if __name__ == '__main__':
    print(PureName("foo.bar"))