import enum
from typing import Callable, Type, Union

import pandas as pd
from pyspark.sql import DataFrame as SparkDataFrame

from . import core, types, util


@core.decorator_factory(check_fn=lambda e: not isinstance(e, str))
def add_docstring(fn, docstring: str = ""):
    fn.__doc__ = (fn.__doc__ or "") + docstring
    return fn


@core.decorator_factory
def cast_to_enum(fn, enumerator: Type[enum.Enum], argnum: int = 0) -> Callable:
    argument_info = core.get_argument_info(fn, argnum)

    def _fn(*args, **kwargs):
        argument, argument_type = core.get_argument(argument_info, args, kwargs)
        argument = util.get_enumerator_from_identifier(argument, enumerator)
        args, kwargs = core.put_argument(argument, argument_info, argument_type, args, kwargs)
        out = fn(*args, **kwargs)
        return out

    return _fn


@core.decorator_factory
def required_columns(fn, columns: list, argnum: int = 0) -> Callable:
    argument_info = core.get_argument_info(fn, argnum)

    def _fn(*args, **kwargs):
        df, _ = core.get_argument(argument_info, args, kwargs)
        missing = set(columns).difference(df.columns)
        if missing:
            msg = ", ".join(map(repr, missing))
            raise ValueError(f"missing columns for dataframe `{argument_info.argname}`: {msg}")
        out = fn(*args, **kwargs)
        return out

    return _fn


class Cast(enum.Enum):
    INPUT = 0
    OUTPUT = 1
    BOTH = 2


@util.not_implemented
@core.decorator_factory
@cast_to_enum(enumerator=Cast, argnum=0)
def to_pandas(fn, when: Union[str, Cast], from_spark: bool = False):
    pass
