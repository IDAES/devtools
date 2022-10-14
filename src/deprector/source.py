import ast
try:
    from ast import unparse
except ImportError:
    from ast_compat import unparse
from collections import deque
from dataclasses import dataclass, field
from functools import singledispatchmethod
from numbers import Number
import os
from pathlib import Path
import re
import textwrap
from typing import (
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
)

import rich

from . import (
    module,
)


Const = Union[Number, str, bool, None]


def _constify(node: ast.AST) -> Const:
    return node.value if isinstance(node, ast.Constant) else unparse(node)


@dataclass
class FunctionCall:
    name: str
    lineno: int
    as_string: str
    args: Tuple[Const, ...] = field(default_factory=tuple)
    kwargs: Dict[str, Const] = field(default_factory=dict)

    @classmethod
    def from_ast_node(cls, node: ast.Call):
        if not isinstance(node.func, ast.Name): return
        name = node.func.id
        lineno = node.lineno
        args = [
            _constify(arg)
            for arg in node.args
        ]
        kwargs = {
            kw.arg: _constify(kw.value)
            for kw in node.keywords
        }

        return cls(
            name=node.func.id,
            lineno=node.lineno,
            args=args,
            kwargs=kwargs,
            as_string=unparse(node)
        )


T = TypeVar("T")


class Collector(Generic[T], ast.NodeVisitor):

    def fit(self, source: str, **kwargs):
        tree = ast.parse(source)
        self.visit(tree)
        return self

    def collect(self) -> Iterable[T]:
        return []

    def fit_collect(self, source: str, **kwargs) -> Iterable[T]:
        return (
            self
            .fit(source, **kwargs)
            .collect()
        )


def collect(collector: Collector, fpaths: Iterable[os.PathLike], drop_empty: bool = False) -> Dict[os.PathLike, List[T]]:
    all_found = {}
    for fpath in fpaths:
        source = Path(fpath).read_text()
        found_for_fpath = collector.fit_collect(source, fpath=fpath)
        all_found[fpath] = list(found_for_fpath)
    if drop_empty:
        all_found = {k: v for k, v in all_found.items() if v}
    return all_found


class CollectFunctionCall(Collector[FunctionCall]):
    def __init__(self, names: List[str]):
        self.names = set(names)

    def visit_Call(self, node: ast.Call):
        if not isinstance(node.func, ast.Name): return
        if node.func.id in self.names:
            self.collected_.append(
                FunctionCall.from_ast_node(node)
            )

    def fit(self, *args, **kwargs):
        self.collected_ = []
        return super().fit(*args, **kwargs)

    def collect(self) -> List[FunctionCall]:
        return list(self.collected_)
        del self.collected_


def walk(node):
    q = deque([node])
    while q:
        node = q.popleft()
        try:
            q.extend(node.get_children())
        except AttributeError:
            pass
        yield node


def get_source(path: Path) -> str:
    return Path(path).read_text()


def get_valid_snippet(path: Path, start_line: int, limit: int = 10):
    src = get_source(path)
    snippet_lines = []
    lines = src.splitlines()[start_line - 1:]
    for n_seen, line in enumerate(lines, start=1):
        if n_seen > limit:
            break
        snippet_lines.append(line)
        snippet = textwrap.dedent("\n".join(snippet_lines))
        try:
            node = ast.parse(snippet)
        except Exception as e:
            continue
        else:
            return snippet
    else:
        return lines[0]
        # raise ("No valid snippet found")


def main(
        package: module.Name
    ):
    module_fpaths = sorted(module.SourceFile.find_in_package(package))
    collector = CollectFunctionCall(names=["relocated_module_attribute", "deprecation_warning"])
    res = collect(collector, fpaths=module_fpaths, drop_empty=True)
    rich.print(res)


if __name__ == '__main__':
    main("idaes")
