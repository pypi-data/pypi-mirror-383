import pathlib

import tomli
from packaging.version import Version

PYPROJECT_FILE = pathlib.Path(__file__).parent.parent / "pyproject.toml"


def get_version() -> Version:
    """
    Get the current version of the project from pyproject.toml.

    :return: The current version of the project.
    :rtype: str
    """
    return Version(tomli.loads(PYPROJECT_FILE.read_text())["project"]["version"])


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 1:
        print("Usage: python get_version.py")
        sys.exit(1)

    sys.stdout.write(str(get_version()))
