from collections import defaultdict
from pathlib import Path
from typing import (
    Iterable,
    Protocol,
)

import rich
from . import (
    depr,
    module,
    source,
)


REPRESENTS_ANY = any


class CallsitesRegistry(depr.SourceContainer):
    def __init__(self):
        self._paths = defaultdict(set)

    def add_deprecator_calls(self, pkg_ipath: module.IPath):
        sources = list(depr.get_deprecation_sites(
            pkg_ipath,
        ))
        for source in sources:
            self.add_file(Path(source.filename), int(source.lineno))
        return self

    def add_file(self, path: Path, *linenos: Iterable[int]):
        linenos = list(linenos or [REPRESENTS_ANY])
        self[path].update(linenos)
        return self

    def add_module(self, ipath: module.IPath, *linenos: Iterable[int]):
        self.add_file(module.get_fpath(ipath), *linenos)
        return self

    def __getitem__(self, key):
        key = Path(key).resolve()
        return self._paths[key]

    def __setitem__(self, key, val: Iterable):
        key = Path(key).resolve()
        self[key].update(val)

    def __contains__(self, source: depr.Source):
        path_match = self[source.filename]
        if not path_match:
            return False
        if REPRESENTS_ANY in path_match:
            return True
        return source.lineno in path_match
