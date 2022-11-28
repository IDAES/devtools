import inspect
import logging
import sys

from pyomo.common.deprecation import (
    deprecation_warning,
)
from bwcompat.patch import (
    Registry,
    directives as d,
    patchers,
    hooks,
)

from .directives import (
    packages,
    module_attrs,
    overwrites,
)

_logger = logging.getLogger(__name__)


@d.get_module_spec.register(type(None))
def for_none(val, **kwargs):
    return d.get_module_spec("bwcompat.empty")


@d.get_attribute_value.register(type(None))
def for_none(val, directive, **kwargs):
    msg = f"The '{directive.name} attribute of {directive.module} is not available anymore."

    class _MissingAttrProxy:
        def __getattr__(self, name):
            deprecation_warning(msg, logger=__name__)
        def __call__(self, *args, **kwargs):
            deprecation_warning(msg, logger=__name__)

    return _MissingAttrProxy()


@hooks.on_activation.register
def _(drc: d.ProxyModuleAttr, **kwargs):
    msg = f"{drc.name!r} cannot be imported from module {drc.module!r} anymore. "
    if drc.replacement:
        msg += f"Instead, use {drc.replacement}"
    deprecation_warning(msg, logger=__name__)


@hooks.on_activation.register
def _(drc: d.ProxyModule, **kwargs):
    what = f"The module {drc.module}"
    if drc.replacement:
        msg = f"{what} must now be imported as {drc.replacement}"
    else:
        msg = f"{what} has been removed and no direct replacement is available."
    relevant_frame = inspect.stack()[-1]
    deprecation_warning(msg, logger=__name__, calling_frame=relevant_frame.frame)


registry = Registry()

registry.add([
    *packages.surr,
    *packages.generic,
    *packages.dmf_ui,
    *packages.core,
    *packages.properties,
    *packages.powergen,
    *packages.convergence,
    *packages.control,
    *packages.costing,
    *packages.util,
])

registry.add([
    *module_attrs.core_util,
    *module_attrs.dmf,
    *module_attrs.ui,
    *module_attrs.mea,
    *module_attrs.powergen,
    *module_attrs.generic,
    *module_attrs.convergence,
    *module_attrs.costing,
    *module_attrs.core_other,
    *module_attrs.pure_props,
    *module_attrs.unc_prop,
    *module_attrs.util_system,
    *module_attrs.helmholtz_iapws95_swco2,
    *module_attrs.gas_solid_contactors,
])

registry.add([
    overwrites.enable_process_block_kwargs_through_default,
    overwrites.convergence_base,
])


registry.enable(
    patchers.ModuleAttrsPatcher(),
    patchers.ProxyModulePatcher(),
)


def activate(subject: str = "Backward compatibility with IDAES v1 API"):
    _logger.warning("%s is being activated", subject)
    for drc in registry:
        _logger.debug(drc)
    registry.activate()
    _logger.warning("%s is now active", subject)


def deactivate():
    registry.deactivate()
