from typing import (
    Any,
    Iterable,
)


class Directive:
    module: str
    origin: Any = None


class Registry(Iterable[Directive]):
    def add(self, *args, **kwargs): pass
    def enable(self, *args, **kwargs): pass
    def activate(self): pass
    def deactivate(self): pass


class Patcher:
    def populate(self, registry: Registry):
        "This should always clear any previously populated state"
        return self

    def install(self):
        raise NotImplementedError

    def uninstall(self):
        raise NotImplementedError
