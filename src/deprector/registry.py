from collections import defaultdict
from pathlib import Path
from typing import (
    Dict,
    Iterable,
    List,
    Protocol,
)

import rich
from . import (
    api,
    depr,
    module,
    source,
)


REPRESENTS_ANY = any


class CallsitesRegistry(depr.SourceContainer):
    def __init__(self):
        self._paths = defaultdict(set)

    def add_function_calls(self, package: module.Name, function_names: Iterable[str]):
        function_calls_by_file = api.get_function_calls_in_source(
            package, function_names,
        )
        for file, calls in function_calls_by_file.items():
            linenos = []
            for call in calls:
                linenos.append(int(call.lineno))
            self.add_file(file.path, *linenos)
        return self

    @property
    def data(self) -> Dict[Path, List[int]]:
        return {
            path: sorted(linenos)
            for path, linenos in self._paths.items()
        }

    def add_file(self, path: Path, *linenos: Iterable[int]):
        linenos = list(linenos or [REPRESENTS_ANY])
        self[path].update(linenos)
        return self

    def add_module(self, name: module.Name, *linenos: Iterable[int]):
        self.add_file(module.SourceFile.from_module(name), *linenos)
        return self

    def _normalize_key(self, key) -> Path:
        return Path(key).resolve()

    def __getitem__(self, key):
        key = self._normalize_key(key)
        return self._paths[key]

    def __setitem__(self, key, val: Iterable):
        key = self._normalize_key(key)
        self[key].update(val)

    def __contains__(self, source: depr.Source):
        path_match = self[source.filename]
        if not path_match:
            return False
        if REPRESENTS_ANY in path_match:
            return True
        return source.lineno in path_match
