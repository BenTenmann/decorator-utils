import os
from pathlib import Path

from setuptools import setup, find_packages

from decorator_utils import get_version

PROJECT_NAME = os.environ.get("PROJECT_NAME", "decorator_utils")


def get_workdir() -> Path:
    directory = Path(__file__).parent
    return directory


def get_long_description(directory: Path) -> str:
    try:
        description = (directory / "README.md").read_text()
    except FileNotFoundError:
        description = ""

    return description


def main():
    directory = get_workdir()
    setup(
        name=PROJECT_NAME,
        version=get_version(directory),
        long_description=get_long_description(directory),
        packages=find_packages()
    )


if __name__ == '__main__':
    main()
