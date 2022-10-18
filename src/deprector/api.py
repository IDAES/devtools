from importlib.metadata import entry_points
from typing import (
    List,
    Dict,
)

from . import (
    module,
    source,
)


def get_callsites_registry(key: str):
    ep_group = entry_points()["deprector.callsites"]
    by_ep_name = {ep.name: ep for ep in ep_group}
    ep = by_ep_name[key]
    factory = ep.load()
    registry = factory()
    return registry


def get_function_calls_in_source(package: module.Name, function_names: List[str]) -> Dict[module.SourceFile, List[source.FunctionCall]]:
    collector = source.CollectFunctionCall(
        names=list(function_names)
    )
    fpaths = sorted(module.SourceFile.find_in_package(package))
    return source.collect(
        collector,
        fpaths=fpaths,
        drop_empty=True,
    )
