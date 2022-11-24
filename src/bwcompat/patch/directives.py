from collections import defaultdict
from contextlib import contextmanager
from dataclasses import (
    dataclass,
    field,
)
import fnmatch
from functools import (
    singledispatch,
    singledispatchmethod,
)
import importlib.metadata
import importlib.util
import logging
import sys
from types import ModuleType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)
from . import (
    base,
)
import bwcompat.util


_logger = logging.getLogger(__name__)


@dataclass
class ProxyModule(base.Directive):
    module: str
    replacement: str
    origin: Any = None

    @classmethod
    def from_mapping(cls, mapping: dict, **kwargs) -> list:
        return [
            cls(module=key, replacement=val, **kwargs)
            for key, val in mapping.items()
        ]


@dataclass
class ProxyModuleAttr(base.Directive):
    module: str
    name: str
    replacement: Any
    origin: Any = None
    _parser_cls: ClassVar[type] = bwcompat.util.EntrypointLike

    def __post_init__(self):
        if isinstance(self.replacement, str):
            try:
                parsed = self._parser_cls(self.replacement)
            except ValueError as err:
                _logger.debug("Unable to parse %s as entrypoint-like: %s", self.replacement, repr(err))
            else:
                self.replacement = parsed

    @classmethod
    def with_no_replacement(cls, spec: dict, **kwargs) -> list:
        return [
            cls(module=mod, name=name, replacement=None)
            for mod, names in spec.items()
            for name in names
        ]

    @classmethod
    def parse(cls, spec: str, **kwargs):
        module, name = cls._parser_cls(spec).parts
        return cls(
            module=module,
            name=name,
            **kwargs
        )

    @classmethod
    def from_mapping(cls, mapping: dict, **kwargs) -> list:
        return [
            cls.parse(key, replacement=val, **kwargs)
            for key, val in mapping.items()
        ]

    @classmethod
    def for_modules(cls, spec: dict):
        return [
            cls(module=mod, name=name, replacement=val)
            for mod, val_by_name in spec.items()
            for name, val in val_by_name.items()
        ]

@dataclass
class OverwriteModuleAttr(base.Directive):
    module: str
    name: str
    replacement: Any
    origin: Any = None


def _module_join(*parts, sep=".") -> str:
    to_join = [
        str(part).strip(sep).rstrip(sep)
        for part in parts
    ]
    return sep.join(to_join)


@singledispatch
def get_attribute_value(obj: Any, directive: base.Directive = None, **kwargs):
    return obj


@get_attribute_value.register(importlib.metadata.EntryPoint)
@get_attribute_value.register(bwcompat.util.EntrypointLike)
def _for_loadable(obj, **kwargs):
    print(obj)
    print(obj.load())
    return obj.load()


@singledispatch
def get_module_spec(name: str, directive: base.Directive = None, **kwargs):
    return importlib.util.find_spec(name)
