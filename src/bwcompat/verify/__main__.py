from pathlib import Path
import sys

import pytest


def main(args=None):
    args = list(args or sys.argv[1:])
    file_path = Path(args[0])
    pytest.main(
        [
            str(file_path),
            f"--bwcompat-importables={file_path}",
            *args[1:],
        ],
    )


main()
