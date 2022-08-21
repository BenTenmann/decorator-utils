import enum
from typing import Callable, Type, Union

from . import core, util


@core.decorator_factory(decorate=lambda e: not isinstance(e, str))
def add_docstring(fn, docstring: str = ""):
    """
    Extend the docstring of `fn` with additional `docstring`.

    Parameters
    ----------
    fn: Any
        Python object for which the docstring should be extended.
    docstring: str
        The additional docs for `fn`.

    Returns
    -------
    out: Any
        `fn` with additional docstring.

    Examples
    --------

    >>> @add_docstring("Some more docs!!")
    ... def f():
    ...     ...

    """
    fn.__doc__ = (fn.__doc__ or "") + docstring
    return fn


@core.decorator_factory
def cast_to_enum(fn, enumerator: Type[enum.Enum], argnum: int = 0) -> Callable:
    """
    Cast a given string identifier function argument to its enumerator equivalent.

    Parameters
    ----------
    fn: Callable
        Function to be decorated.
    enumerator: Type[enum.Enum]
        The enumeration of the options.
    argnum: int
        The positional index of the argument to be converted.

    Returns
    -------
    out: Callable
        The decorated function which implicitly maps the string argument to an enumeration. The function will raise an
        exception if the string does not match an enumeration option.

    Examples
    --------

    >>> class Option(enum.Enum):
    ...     ONE = 0
    ...     TWO = 1
    >>>
    >>> @cast_to_enum(enumerator=Option, argnum=0)
    ... def f(option):
    ...     ...

    """
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
    """
    Raise an error when a set of columns is not in a dataframe argument.

    Parameters
    ----------
    fn: Callable
        Function to be decorated.
    columns: list
        A list of string column identifiers which are to be required.
    argnum: int
        The positional index of the argument to be checked.

    Returns
    -------
    out: Callable
        The decorated function.

    Examples
    --------

    >>> @required_columns(["name", "value"])
    ... def f(df):
    ...     ...

    """
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
@cast_to_enum(enumerator=Cast, argnum=1)
def to_pandas(fn, when: Union[str, Cast], from_spark: bool = False):
    pass
