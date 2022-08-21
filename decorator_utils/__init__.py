"""
decorator_utils
===============

Python package providing utilities for creating decorators and decorator factories. It also offers some convenient,
pre-defined decorators which perform IO type-checking, schema validation, type casting etc.

Examples
--------

Most users will be happy using the pre-defined decorators, as they provide a lot of useful functionality out of the box:
>>> import pandas as pd
>>> from decorator_utils.misc import required_columns
>>>
>>> @required_columns(["id", "name", "value"])
>>> def some_func(df: pd.DataFrame) -> pd.DataFrame:
...     return df[["id", "name", "value"]].describe()
>>>
>>> some_func(pd.DataFrame(columns=["id", "name", "value", ...]))  # no error
>>> some_func(pd.DataFrame(columns=["id", "name"]))  # error! missing column

"""

import re
from pathlib import Path


def get_version(directory: Path) -> str:
    # convenience function to get the current version of the package
    try:
        changelog = (directory / "CHANGELOG.md").read_text()
        version, *_ = re.findall(r"\[([\d.]+)]", changelog)
    except (ValueError, FileNotFoundError):
        version = "0.1.0"

    return version


__version__ = get_version(Path(__file__).parent.parent)
