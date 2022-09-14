import rich

from . import (
    registry,
    depr,
)


def idaes():
    return (
        registry.CallsitesRegistry()
        .add_function_calls(
            "idaes",
            function_names=[
                "deprecation_warning",
                "relocated_module_attribute",
                "_process_kwargs",
            ]
        )
    )


if __name__ == '__main__':
    for make_matcher in [
        idaes
    ]:
        rich.print(make_matcher)
        matcher = make_matcher()
        rich.print(matcher.data)
