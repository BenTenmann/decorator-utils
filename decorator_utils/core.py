"""
decorator_utils.core
====================

The core functionality to use for creating new decorators and decorator factories.

"""

import enum
import inspect
from collections import namedtuple
from functools import partial, update_wrapper, wraps, WRAPPER_ASSIGNMENTS
from typing import Any, Callable, Tuple, Union

from .util import format_enum_options

__all__ = [
    "wraps",
    "set_function_signature",
    "get_argument",
    "get_argument_info",
    "put_argument",
    "get_output",
    "put_output",
    "decorator",
    "decorator_factory"
]

CUSTOM_WRAPPER_ASSIGNMENTS = (*WRAPPER_ASSIGNMENTS, "__signature__")

wraps = update_wrapper(partial(wraps, assigned=CUSTOM_WRAPPER_ASSIGNMENTS), wraps)


def set_function_signature(fn: Callable) -> Callable:
    """
    Set the function signature as an attribute of the function (`__signature__`). This is a necessary step in the
    decorating process, as some third-party tools (e.g. PySpark) can cause errors when decorating a function.

    Parameters
    ----------
    fn: Callable
        An arbitrary callable for which one wants to set the `__signature__` attribute.

    Returns
    -------
    fn: Callable
        The input callable with the `__signature__` set.

    Examples
    --------

    >>> def f(a, b):
    ...     return a + b
    >>>
    >>> f = set_function_signature(f)
    >>> hasattr(f, "__signature__")
    True

    """
    signature = inspect.signature(fn)
    if not hasattr(fn, "__signature__"):
        fn.__signature__ = None

    fn.__signature__ = (fn.__signature__ or signature)
    return fn


ArgumentInfo = namedtuple("ArgumentInfo", ["argname", "argnum", "default"])


def _update_argnum(params, argnum: int) -> int:
    if argnum < 0:
        # In case negative indexing is used, we want to find the non-negative equivalent positional index.
        # Positive indexing should be enforced as otherwise the second condition in `get_argument` fails.
        return argnum + len(params)
    return argnum


def get_argument_info(fn: Callable, argnum: int) -> ArgumentInfo:
    """
    Get the necessary argument information for extracting an argument from when a set of args and kwargs.

    Parameters
    ----------
    fn: Callable
        An arbitrary callable for which we want to get the argument information for a given argument.
    argnum: int
        The positional index of the argument of interest in `fn`.

    Returns
    -------
    out: ArgumentInfo
        A namedtuple containing the `argname` (name of the argument), `argnum` (the positional index of the argument)
        and the `default` (the default value for the argument).

    Examples
    --------

    >>> def f(a, b=2):
    ...     return a ** b
    >>>
    >>> name, num, _ = get_argument_info(f, argnum=0)
    >>> name, num
    ('a', 0)
    >>> get_argument_info(f, argnum=-1)
    ArgumentInfo(argname='b', argnum=1, default=2)

    """
    params = inspect.signature(fn).parameters
    argname = list(params)[argnum]
    argnum = _update_argnum(params, argnum)

    out = ArgumentInfo(argname, argnum, params[argname].default)
    return out


class Argument(enum.Enum):
    # enumerate the types of ways an argument can be passed to a function
    POSITIONAL = 0
    KEYWORD = 1
    DEFAULT = 2


def get_argument(argument_info: ArgumentInfo, args: tuple, kwargs: dict) -> Tuple[Any, Argument]:
    """
    Get a specific argument from a set of args and kwargs. Only really useful inside a decorator.

    Parameters
    ----------
    argument_info: ArgumentInfo
        The information of the argument to be extracted.
    args: tuple
        An args tuple.
    kwargs: dict
        A kwargs dict.

    Returns
    -------
    out: Tuple[Any, Argument]
        Returns the argument value (contained in either args or kwargs) and the type of argument (i.e. positional,
        keyword or default).

    Examples
    --------

    Suppose we want to have a decorator factory where we can check if an argument is None and raise an error in that
    case:
    >>> @decorator_factory
    ... def raise_if_none(fn, argnum):
    ...     arg_info = get_argument_info(fn, argnum)
    ...
    ...     def _fn(*args, **kwargs):
    ...         arg, _ = get_argument(argument_info, args, kwargs)
    ...         if arg is None:
    ...             raise ValueError(f"{arg_info.argname!r} cannot be None.")
    ...         out = fn(*args, **kwargs)
    ...         return out
    ...
    ...     return _fn
    >>>
    >>> @raise_if_none(argnum=0)
    ... def f(a=None):
    ...     ...
    >>>
    >>> f()  # error!
    >>> f(None)  # error!
    >>> f(1)  # no error

    """
    if argument_info.argname in kwargs:
        return kwargs[argument_info.argname], Argument.KEYWORD
    if len(args) > argument_info.argnum:
        return args[argument_info.argnum], Argument.POSITIONAL
    return argument_info.default, Argument.DEFAULT


def put_argument(
        argument: Any,
        argument_info: ArgumentInfo,
        argument_type: Argument,
        args: tuple,
        kwargs: dict
) -> Tuple[tuple, dict]:
    """
    Put an (edited) argument back into args and kwargs.

    Parameters
    ----------
    argument: Any
        The (edited) argument or arbitrary object to be put into args or kwargs.
    argument_info: ArgumentInfo

    argument_type: Argument
        The type of the argument, i.e. whether it was a positional, keyword or default argument.
    args: tuple
        The args tuple.
    kwargs: dict
        The kwargs dict.

    Returns
    -------
    out: Tuple[tuple, dict]
        The updated args and kwargs.

    """
    if argument_type in (Argument.DEFAULT, Argument.KEYWORD):
        kwargs[argument_info.argname] = argument

    elif argument_type == Argument.POSITIONAL:
        args = tuple(arg if idx != argument_info.argnum else argument for idx, arg in enumerate(args))

    else:
        msg = format_enum_options(Argument, formatter=str)
        raise RuntimeError(f"{repr(argument_type)} is not a valid `Argument` option. {msg}")

    return args, kwargs


def get_output(output: Any, output_index: Union[str, int] = None) -> Any:
    if output_index is None:
        return output
    return output[output_index]


def put_output(output: Any, edited_output: Any, output_index: Union[str, int] = None) -> Any:
    if output_index is None:
        return edited_output
    if isinstance(output_index, int):
        return type(output)(out if idx != output_index else edited_output for idx, out in enumerate(output))
    output[output_index] = edited_output
    return output


def decorator(deco: Callable):

    @wraps(deco)
    def _deco(fn):
        fn = set_function_signature(fn)
        out = wraps(fn)(deco(fn))
        return out

    return _deco


def decorator_factory(deco: Callable = None, decorate: Callable[[Any], bool] = callable):
    """
    Make a decorator into a decorator factory.

    Parameters
    ----------
    deco: Callable
        A decorator which should be converted into a decorator factory.
    decorate: Callable[[Any], bool]
        A callable used to check whether the first argument to the decorator is the object which should be decorated. In
        the default case, it checks whether the first positional argument is a callable.

    Returns
    -------
    out: Callable
        Returns the decorator factory version of the original decorator.

    """

    if decorate != inspect.signature(decorator_factory).parameters["check_fn"].default:
        # in case an arbitrary check fn is passed, we need to return the factory so that it can be called again in the
        # decoration process
        return update_wrapper(partial(decorator_factory, check_fn=decorate), decorator_factory)

    @wraps(deco)
    def _deco_factory(fn, *args, **kwargs):
        if not decorate(fn):
            argname = list(inspect.signature(deco).parameters)[1]
            kwargs[argname] = fn
            out = update_wrapper(partial(deco, *args, **kwargs), deco)
        else:
            out = deco(fn, *args, **kwargs)
            fn = set_function_signature(fn)
            out = wraps(fn)(out)

        return out

    return _deco_factory
