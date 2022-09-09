from importlib.metadata import entry_points


def get_callsites_registry(key: str):
    ep_group = entry_points()["deprector.callsites"]
    by_ep_name = {ep.name: ep for ep in ep_group}
    ep = by_ep_name[key]
    factory = ep.load()
    registry = factory()
    return registry
