from pyomo.common.config import ConfigBlock
from pyomo.common.deprecation import deprecation_warning


def _process_kwargs_supporting_default(o, kwargs):
    from idaes.core.base.process_block import (
        _rule_default,
        _get_pyomo_block_kwargs,
    )
    _pyomo_block_keywords = _get_pyomo_block_kwargs()

    kwargs.setdefault("rule", _rule_default)
    o._block_data_config_initialize = ConfigBlock(implicit=True)
    o._block_data_config_initialize.set_value(kwargs.pop("initialize", None))
    o._idx_map = kwargs.pop("idx_map", None)
    _default = kwargs.pop("default", None)
    if _default is not None:
        deprecation_warning(
            "The default argument for the ProcessBlock class is deprecated. "
            "Arguments must now be passed directly as keyword arguments.",
            version="1.13.0",
        )
    _block_data_config_default = _default
    _pyomo_kwargs = {}
    for arg in _pyomo_block_keywords:
        if arg in kwargs:
            _pyomo_kwargs[arg] = kwargs.pop(arg)
    if kwargs:
        # left over args for IDAES
        if _block_data_config_default is None:
            _block_data_config_default = kwargs
        else:
            deprecation_warning(
                "Do not supply both keyword arguments and the "
                "'default' argument to ProcessBlock init. Default is deprecated.",
                version="1.13.0",
            )
    o._block_data_config_default = _block_data_config_default
    return _pyomo_kwargs


def register_convergence_class_with_disambiguation(name):
    from idaes.core.util.convergence.convergence_base import convergence_classes
    if name in convergence_classes:
        num_existing = len([k for k in convergence_classes if name in k])
        name = f"{name}_{num_existing}"
    def _register_convergence_class(cls):
        if name in convergence_classes:
            raise KeyError(f"Convergence class {name} already registered.")
        convergence_classes[name] = ".".join([cls.__module__, cls.__name__])
        return cls

    return _register_convergence_class
