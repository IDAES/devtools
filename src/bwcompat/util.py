import fnmatch
import importlib
from operator import attrgetter
import importlib.metadata
from typing import (
    Iterable,
    List,
)


def matches_any(s: str, patterns: Iterable[str]) -> bool:
    return any(
        fnmatch.fnmatch(s, pat)
        for pat in patterns
    )


def get_entry_points(group_name: str) -> List[importlib.metadata.EntryPoint]:
    eps = importlib.metadata.entry_points()
    try:
        # this happens for Python 3.7 (via importlib_metadata) and Python 3.10+
        entry_points = list(eps.select(group=group_name))
    except AttributeError:
        # this will happen on Python 3.8 and 3.9, where entry_points() has dict-like group selection
        entry_points = list(eps[group_name])
    # importlib.metadata can load entry points twice, see https://github.com/pypa/setuptools/issues/3649
    entry_points = sorted(set(entry_points))
    return entry_points


class EntrypointLike(str):
    sep: str = ":"

    def __new__(cls, *args):
        s = super().__new__(cls, *args)
        if s.count(cls.sep) != 1:
            raise ValueError(f"Expected exactly 1 instance of {cls.sep!r}, instead have: {s!r}")
        return s

    @property
    def parts(self):
        sep = type(self).sep
        mod, found_sep, obj = self.partition(sep)
        assert found_sep
        return mod, obj

    def load(self):
        modname, attrspec = self.parts
        mod = importlib.import_module(modname)
        obj = attrgetter(attrspec)(mod)
        return obj
