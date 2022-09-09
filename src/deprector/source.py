import ast
from collections import deque
from functools import singledispatchmethod
from dataclasses import dataclass
from pathlib import Path
import re
import textwrap
from typing import (
    List,
)

import astroid
from rich import print

from . import (
    module,
)


class CollectCallArg(ast.NodeVisitor):
    def __init__(self, *names):
        self._names = set(names)
        self._found = []

    def __iter__(self):
        return iter(self._found)

    def visit_Call(self, node: ast.Call):
        if not isinstance(node.func, ast.Name): return
        try:
            if node.func.id in self._names:
                print(ast.dump(node, annotate_fields=True))
                message = node.args[0].value
                self._found.append((message, node.lineno))
        except: pass


class CollectModuleDepr(ast.NodeVisitor):

    def __init__(self, *names):
        self._names = set(names)
        self._found = []
        self.deprecation = None

    # def visit_Call(self, node: ast.Call):
    #     if not isinstance(node.func, ast.Name): return
    #     # print(ast.dump(node, annotate_fields=True))
    #     if node.func.id in self._names:
    #         # print(ast.dump(node, annotate_fields=True))
    #         message = node.args[0].value
    #         self._found = message

    def visit_ImportFrom(self, node: ast.ImportFrom):
        mod = node.module
        if self.deprecation and mod != self.deprecation:
            self._found.append(mod)
        if mod == "pyomo.common.deprecation":
            self.deprecation = mod


MODULE_DEPR_MESSAGE = re.compile(r"^(?:.*) has been moved to (?P<target>[\w\.]+)$")


def get_module_depr(fpath: module.FPath, root_fpath):
    ipath = module.get_ipath(fpath, root_fpath)
    coll = CollectModuleDepr("deprecation_warning")
    tree = ast.parse(fpath.read_text())
    # print(ast.dump(tree))
    coll.visit(tree)
    # msg = coll._found
    new = list(coll._found)
    # new = re.findall(MODULE_DEPR_MESSAGE, re)

    return (ipath, new)


def get_module_deprs(root_ipath: module.IPath):
    root_fpath = module.get_root_fpath(root_ipath)
    found = []
    for fpath in sorted(root_fpath.rglob("*.py")):
        old, new = get_module_depr(fpath, root_fpath)
        if old and new:
            found.append((old, new))
    return found


def walk(node):
    q = deque([node])
    while q:
        node = q.popleft()
        try:
            q.extend(node.get_children())
        except AttributeError:
            pass
        yield node


def is_deprecation_node(node: astroid.Call):
    if not isinstance(node, astroid.Call): return


def _display(source: str):
    parsed = astroid.parse(source)
    print(parsed.repr_tree())


def get_deprecation_messages(fpath: module.FPath, func_name: str) -> List[str]:
    coll = CollectCallArg(func_name)
    tree = ast.parse(fpath.read_text())
    coll.visit(tree)

    return list(coll)


def main(path):
    root = astroid.parse(
        Path(path).read_text()
    )

    pbs = []
    for node in walk(root):
        if not isinstance(node, astroid.Call): continue
        print(node.repr_tree())
        if is_init_call_with_default_kwarg(node):
            try:
                pb = ProcessBlockInit(
                    call=node,
                    default_kwarg=[n for n in node.keywords if n.arg == "default"][0]
                )
            except:
                pass
            else:
                pbs.append(pb)
                sub_pair = (pb.original, pb.replacement)

    sub_pairs = [
        (pb.original, pb.replacement)
        for pb in pbs
    ]
    print(
        "\n".join(
            " -> ".join(pair)
            for pair in sub_pairs
        )
    )


def get_source(path: Path) -> str:
    return Path(path).read_text()


def get_valid_snippet(path: Path, start_line: int):
    src = get_source(path)
    snippet_lines = []
    lines = src.splitlines()[start_line - 1:]
    for line in lines:
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
        *root_ipaths,
    ):
    idaes = module.get_fpath("idaes")
    pyomo = module.get_fpath("pyomo")
    module_fpaths = []
    for ipath in root_ipaths:
        fpath = module.get_fpath(ipath)
        module_fpaths.extend(
            fpath.rglob("*.py")
        )

    collect(sorted(module_fpaths))



if __name__ == '__main__':
    # main("idaes", "pyomo")
    idaes = Path("/opt/conda/envs/dev-watertap/lib/python3.8/site-packages/idaes")
    fpath = idaes/"surrogate/surrogate_block.py"
    # print(get_module_deprs(fpath, "deprecation_warning", root_fpath=idaes))
    print(get_module_deprs("idaes"))
    # pyomo = Path("/opt/conda/envs/dev-watertap/lib/python3.8/site-packages/pyomo")
    # sn = get_valid_snippet(
    #     idaes / "models/unit_models/tests/test_separator.py",
    #     2859,
    # )
    # print(sn)
