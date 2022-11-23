from pathlib import Path
import sys

import pytest

from . import (
    ImportablesPlugin,
)


def main(args=None):
    args = list(args or sys.argv[1:])
    file_path = Path(args[0])
    pytest.main(
        [
            str(file_path),
            *args[1:],
        ],
        plugins=[
            ImportablesPlugin(file_name=file_path.name),
        ]
    )


main()
