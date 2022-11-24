from collections import defaultdict
import fnmatch
from functools import (
    singledispatch,
    singledispatchmethod,
)
from importlib.metadata import EntryPoint
import logging
from typing import (
    Any,
    Iterable,
    List,
    Tuple,
    Union,
)
from bwcompat import (
    util,
)
from . import (
    base,
)
from .directives import (
    ProxyModuleAttr,
    ProxyModule,
)


_logger = logging.getLogger(__name__)


class Registry:
    Registrable = Union[base.Directive, EntryPoint, str, List["Registrable"]]

    def __init__(self, *items: Iterable[Registrable]):
        self._directives = []

        self.add(list(items))

    @singledispatchmethod
    def add(self, item: object, **kwargs):
        raise TypeError(f"{type(item)} not supported: {item}")

    @add.register
    def _(self, drc: base.Directive, origin: Any = None):
        if origin and not drc.origin:
            drc.origin = origin
        _logger.debug("adding directive %s", drc)
        self._directives.append(drc)
        return self

    @add.register
    def _(self, items: list, **kwargs):
        for item in items:
            self.add(item, **kwargs)
        return self

    @add.register
    def _(self, ep: EntryPoint, sep: str = ":"):
        to_add = []
        dest_spec = ep.name
        module, found_sep, name = dest_spec.partition(sep)
        if found_sep and name:
            # we interpret it as a ProxyModuleAttr directive
            to_add = ProxyModuleAttr(
                module=module,
                name=name,
                replacement=ep,
            ),
        elif sep not in ep.value:
            to_add = ProxyModule(
                module=module,
                replacement=str(ep.value),
            )
        else:
            # assume ep points to a ready-made registerable object
            to_add = ep.load()

        self.add(to_add, origin=str(ep.name))
        return self

    @add.register
    def _(self, key: str, **kwargs):
        try:
            entry_points = util.get_entry_points(group_name=key)
        except Exception as e:
            _logger.exception("Could not load entry points from group %s", key)
            return self
        else:
            self.add(entry_points)

    def __iter__(self):
        return iter(self._directives)

    def select(self, key):
        if isinstance(key, type):
            selector = lambda x: isinstance(x, key)
        elif isinstance(key, str):
            selector = lambda x: fnmatch.fnmatch(x.module, key)
        else:
            raise TypeError(key)

        return [
            item
            for item in self
            if selector(item)
        ]

    def by_module(self, key) -> Iterable[Tuple[str, Iterable[base.Directive]]]:
        grouped = defaultdict(list)
        for drc in self.select(key):
            grouped[drc.module].append(drc)
        yield from grouped.items()

    def enable(self, *patchers: base.Patcher, **kwargs):
        self.patchers_ = list(patchers)

    def activate(self):
        for patcher in self.patchers_:
            _logger.info("Populating %s", patcher)
            patcher.populate(self)
            _logger.info("Installing %s", patcher)
            patcher.install()

    def deactivate(self):
        for patcher in self.patchers_:
            _logger.info("Uninstalling %s", patcher)
            patcher.uninstall()


@singledispatch
def load(obj: Any):
    assert isinstance(obj, base.Registry)
    return obj


@load.register
def _from_entry_point(name: str, group_name="bwcompat.registries"):
    by_name = {
        ep.name: ep
        for ep in util.get_entry_points(group_name)
    }

    try:
        ep = by_name[name]
        return ep.load()
    except KeyError:
        raise LookupError(f"Entry point name {name} not found within {group}. Available: {list(by_name)}")
