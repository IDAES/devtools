import collections
import contextlib
from dataclasses import field, asdict
import importlib
import inspect
import sys
from typing import (
    Callable,
    Container,
    Iterable,
    List,
    Optional,
    Protocol,
    Tuple,
)

import pytest
from pydantic.dataclasses import dataclass
import oyaml as yaml

from . import (
    util,
    module,
    source,
)


Message = str


@dataclass
class DeprecatorSpec:
    module_ipath: module.IPath
    name: str


DEPRECATOR = DeprecatorSpec(
    module_ipath="pyomo.common.deprecation",
    name="deprecation_warning"
)


@dataclass
class CallContext:
    filename: str
    lineno: int
    code: str = ""
    stack_index_relative: int = -1
    stack_index_absolute: int = -1

    @classmethod
    def from_frame_info(cls, info: inspect.FrameInfo, **kwargs):
        return cls(
            filename=info.filename.strip(),
            lineno=int(info.lineno),
            code="".join(info.code_context or []).strip(),
            **kwargs,
        )


@dataclass(frozen=True)
class Source:
    "Source of deprecation messages in the codebase"

    filename: str
    lineno: int
    message: Message


class SourceContainer(Protocol):

    def __contains__(self, source: Source) -> bool:
        ...


SourcePredicate = Callable[[Source], bool]


@dataclass
class Record:
    "A collected deprecation message plus context"
    message: Message
    args: tuple
    kwargs: dict
    collection_id: Optional[int] = None
    provenance: Optional[dict] = None
    call_contexts: Optional[List[CallContext]] = None


def get_primary_source(record: Record, skip: Optional[SourcePredicate] = None) -> Source:
    if skip is None:
        skip = (lambda s: False)
    call_contexts = sorted(
        record.call_contexts,
        key=lambda d: d.stack_index_relative
    )
    candidate_sources = [
        Source(
            filename=ctx.filename,
            lineno=ctx.lineno,
            message=record.message,
        )
        for ctx in call_contexts
    ]
    for cand in candidate_sources:
        if skip(cand): continue
        return cand


class Collector:

    def __init__(
            self,
            root_paths: Optional[List[str]] = None,
            deprecators: Optional[Iterable[DeprecatorSpec]] = (DEPRECATOR,),
        ):
        self.emitted_warnings = set()
        self._root_paths = list(root_paths or [])
        self._deprecators = list(deprecators)
        self._monkeypatch = pytest.MonkeyPatch()

        self._stored = []
        self._staged = []
        self._archived = collections.defaultdict(list)

    def register(self, *paths):
        self._root_paths.extend(paths)

    def activate(self):
        for spec in self._deprecators:
            mod = importlib.import_module(spec.module_ipath)
            self._monkeypatch.setattr(mod, spec.name, self)

    def deactivate(self):
        self._monkeypatch.undo()

    @contextlib.contextmanager
    def activated(self):
        self.activate()

        try:
            yield self
        finally:
            self.deactivate()

    def __call__(self, msg: str, *args, **kwargs):
        rec = Record(
            message=str(msg).strip(),
            args=args,
            kwargs=kwargs,
            collection_id=len(self),
        )

        rec.call_contexts = list(self.get_relevant_call_contexts())

        self.store(rec)

    def get_relevant_call_contexts(self):
        rel_idx = 0
        for abs_idx, frame_info in enumerate(inspect.stack()):
            filename = frame_info.filename.strip()
            # is_relevant = not _matches_any(filename, self._ignore_patterns)
            is_relevant = any(
                str(root) in filename
                for root in self._root_paths
            )
            if is_relevant:
                yield CallContext.from_frame_info(
                    frame_info,
                    stack_index_absolute=abs_idx,
                    stack_index_relative=rel_idx,
                )
                rel_idx += 1

    def __iter__(self):
        return iter(self._stored)

    def __len__(self):
        return len(self._stored)
        
    def items(self):
        return dict(self._archived).items()

    def store(self, depr):
        self._stored.append(depr)
        self._staged.append(depr)

    def archive(self, key):
        to_commit = []
        try:
            to_commit = list(self._staged)
            self._archived[key] = ...
        except TypeError:
            key = str(key)
        finally:
            self._archived[key] = to_commit
            self._staged.clear()
        return to_commit


def collect_during_module_import(ipath: module.IPath) -> Tuple[List[Record], List]:
    errors = []
    root_fpath = module.get_root_fpath(ipath)
    with Collector(root_paths=[root_fpath]).activated() as dp:
        try:
            importlib.import_module(ipath)
        except Exception as e:
            errors.append(e)
    return list(dp), errors


def get_import_deprs(ipath: module.IPath) -> List[Record]:
    modules_before = list(sys.modules)
    res, errors = util.run_in_subprocess(collect_during_module_import, args=(ipath,))
    modules_after = list(sys.modules)
    added = set(modules_after) - set(modules_before)
    assert ipath not in added
    return res


def get_deprecation_sites(*ipaths):
    module_fpaths = []
    for ipath in ipaths:
        fpath = module.get_fpath(ipath)
        globbable = fpath if fpath.is_dir() else fpath.parent
        module_fpaths.extend(
            sorted(globbable.rglob("*.py"))
        )
    
    module_fpaths
    for fpath in module_fpaths:
        found = source.get_deprecation_messages(fpath, func_name=DEPRECATOR.name)
        for msg, lineno in found:
            yield Source(
                filename=str(fpath),
                lineno=int(lineno),
                message=str(msg),
            )


if __name__ == '__main__':
    sites = list(get_deprecation_sites("idaes"))
    print(sites)