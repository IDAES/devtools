import collections
import contextlib
from dataclasses import field, asdict
import importlib
import inspect
import logging
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


_logger = logging.getLogger(__name__)

Message = str


@dataclass
class DeprecatorSpec:
    module: module.Name
    name: str
    orig_object: object = None

    def load_module(self):
        mod = importlib.import_module(self.module)
        self.orig_object = getattr(mod, self.name)
        return mod


DEPRECATOR = DeprecatorSpec(
    module="pyomo.common.deprecation",
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
            mod = spec.load_module()
            assert spec.module in sys.modules
            _logger.debug("orig_object: %s", spec.orig_object)
            self._monkeypatch.setattr(mod, spec.name, self)
            _logger.debug("getattr(mod, %s): %s", spec.name, getattr(mod, spec.name))

    def deactivate(self):
        self._monkeypatch.undo()

    @contextlib.contextmanager
    def activated(self):
        self.activate()

        try:
            yield self
        finally:
            self.deactivate()

    def __call__(self, msg: str, *args, calling_frame=None, **kwargs):
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


def collect_during_module_import(mod: module.Name) -> Tuple[List[Record], List]:
    # mod = module.Name(mod)
    errors = []
    root_paths = list(mod.submodules_search_paths or [mod.origin])
    with Collector(root_paths=root_paths).activated() as dp:
        try:
            mod.import_module()
        except Exception as e:
            errors.append(e)
    return list(dp), errors


def get_import_deprs(mod: module.Name) -> List[Record]:
    modules_before = list(sys.modules)
    res, errors = util.run_in_subprocess(collect_during_module_import, args=(mod,))
    modules_after = list(sys.modules)
    added = set(modules_after) - set(modules_before)
    assert mod not in added
    return res
