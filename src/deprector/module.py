import importlib
from pathlib import Path

from . import (
    util
)


FPath = Path
"The filesystem path for a Python module"

IPath = str
"String representing dotted import path to a module"


def _ipath2fpath(ipath: IPath) -> Path:
    mod = importlib.import_module(ipath)
    try:
        return Path(mod.__path__[0])
    except AttributeError:
        return Path(mod.__file__)


def _fpath2ipath(fpath: FPath, root_fpath: FPath) -> IPath:
    relpath = (
         fpath
        .resolve()
        .relative_to(root_fpath.parent)
    )
    return ".".join(
        relpath
        .with_suffix("")
        .parts
    )


def get_ipath(fpath: FPath, root_fpath: FPath) -> IPath:
    return _fpath2ipath(fpath, root_fpath)


def get_fpath(ipath: IPath) -> Path:
    return util.run_in_subprocess(_ipath2fpath, args=(ipath,))


def get_root_ipath(ipath: IPath) -> IPath:
    return ipath.split(".")[0]


def get_root_fpath(ipath: IPath) -> FPath:
    root_ipath = get_root_ipath(ipath)
    return _ipath2fpath(root_ipath)
