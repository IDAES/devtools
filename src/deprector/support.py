from . import (
    registry,
    depr,
)


def idaes():
    return (
        registry.CallsitesRegistry()
        .add_deprecator_calls("idaes")
        .add_module("idaes.core.base.process_block", 98, 125, 140)
    )


if __name__ == '__main__':
    matcher = idaes()
    for src in [
        depr.Source(
            filename="/opt/conda/envs/dev-watertap/lib/python3.8/site-packages/idaes/core/base/process_block.py",
            lineno=123,
            message="The default argument for the ProcessBlock class is deprecated. Arguments can now be passed directly as keyword arguments."
        ),
        depr.Source(
            filename="/opt/conda/envs/dev-watertap/lib/python3.8/site-packages/idaes/core/base/process_block.py",
            lineno=125,
            message="The default argument for the ProcessBlock class is deprecated. Arguments can now be passed directly as keyword arguments."
        ),
    ]:
        print(src in matcher)
        # print(src)
