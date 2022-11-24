from dataclasses import (
    dataclass,
    field,
)
from functools import (
    singledispatchmethod,
)
from importlib.metadata import EntryPoint
import importlib.abc
import importlib.util
import logging
import sys
from typing import (
    Callable,
    Container,
    Dict,
    List,
    Mapping,
    Optional,
)
from types import (
    ModuleType,
)

from .directives import (
    ProxyModule,
    ProxyModuleAttr,
    OverwriteModuleAttr,
    get_attribute_value,
    get_module_spec,
)
from . import (
    hooks,
    base,
)


_logger = logging.getLogger(__name__)





class _MonkeypatchMixin:

    @property
    def monkeypatch(self):
        if not hasattr(self, "_monkeypatch"):
            from pytest import MonkeyPatch
            self._monkeypatch = MonkeyPatch()
        return self._monkeypatch

    def setattr_(self, *args, **kwargs):
        self.monkeypatch.setattr(*args, **kwargs)

    def uninstall(self):
        self.monkeypatch.undo()


@dataclass
class ProxyModulePatcher(base.Patcher, importlib.abc.MetaPathFinder):

    directives: Mapping[str, ProxyModule] = field(default_factory=dict)

    def populate(self, registry: base.Registry):
        self.directives = {}
        for module, for_module in registry.by_module(ProxyModule):
            if len(for_module) == 1:
                self.directives[module] = for_module[0]
            else:
                raise ValueError(f"Expected 1 directive for {module}, instead found {for_module}")
        return self

    def __getitem__(self, key):
        return self.directives[key]

    def find_spec(self, name, path, *args):
        try:
            redirect = self[name]
        except KeyError:
            return None
        _logger.debug("Finding spec for %s using %s", name, redirect)
        hooks.on_activation(redirect, caller=self)
        target_spec = get_module_spec(redirect.replacement, directive=redirect)
        _logger.debug("target spec: %s", target_spec)

        return importlib.util.spec_from_file_location(
            name, location=target_spec.origin,
        )

    def install(self):
        sys.meta_path.append(self)

    def uninstall(self):
        sys.meta_path.remove(self)


@dataclass
class _ModuleGetattr:
    directives: Mapping[str, ProxyModuleAttr]
    module: str

    def __getitem__(self, key):
        return self.directives[key]

    def __call__(self, attr_name):
        try:
            directive = self[attr_name]
        except KeyError:
            raise AttributeError(attr_name)

        hooks.on_activation(directive)
        return get_attribute_value(directive.replacement, directive=directive)


@dataclass
class ProxyModuleAttrsPatcher(_MonkeypatchMixin, base.Patcher):
    directives: Mapping[str, List[ProxyModuleAttr]] = field(default_factory=dict)

    def populate(self, registry: base.Registry, **kwargs):
        self.directives = dict(registry.by_module(ProxyModuleAttr))
        return self

    @singledispatchmethod
    def get_handler(self, module: str):
        for_module = self.directives.get(module, [])
        if not for_module:
            return None
        by_name = {}
        for drc in for_module:
            name = drc.name
            if name in by_name:
                raise ValueError(f"Duplicate directive for module {module}, attribute {name}: {drc}")
            by_name[name] = drc
        
        return _ModuleGetattr(by_name, module=module)

    @get_handler.register
    def _(self, module: ModuleType):
        return self.get_handler(module.__name__)

    def install(self):
        def _patched_exec_module(loader: importlib.abc.Loader, module: ModuleType):
            super(type(loader), loader).exec_module(module)
            attr_handler_for_module = self.get_handler(module)
            if not attr_handler_for_module:
                return
            self.setattr_(module, "__getattr__", attr_handler_for_module, raising=False)

        self.setattr_("_frozen_importlib_external.SourceFileLoader.exec_module", _patched_exec_module)


@dataclass
class OverwriteAttrsPatcher(_MonkeypatchMixin, base.Patcher):
    directives: List[OverwriteModuleAttr] = field(default_factory=list)

    def populate(self, registry: base.Registry):
        self.directives = list(registry.select(OverwriteModuleAttr))
        return self

    def __iter__(self):
        return iter(self.directives)

    def install(self):
        for drc in self:
            hooks.on_activation(drc)
            attr_value = get_attribute_value(drc.replacement, directive=drc)
            self.setattr_(f"{drc.module}.{drc.name}", attr_value, raising=False)
