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
    signature = inspect.signature(fn)
    if not hasattr(fn, "__signature__"):
        fn.__signature__ = None

    fn.__signature__ = (fn.__signature__ or signature)
    return fn


ArgumentInfo = namedtuple("ArgumentInfo", ["argname", "argnum", "default"])


def _update_argnum(params, argnum: int) -> int:
    if argnum < 0:
        return argnum + len(params)
    return argnum


def get_argument_info(fn: Callable, argnum: int) -> ArgumentInfo:
    params = inspect.signature(fn).parameters
    argname = list(params)[argnum]
    argnum = _update_argnum(params, argnum)

    out = ArgumentInfo(argname, argnum, params[argname].default)
    return out


class Argument(enum.Enum):
    POSITIONAL = 0
    KEYWORD = 1
    DEFAULT = 2


def get_argument(argument_info: ArgumentInfo, args: tuple, kwargs: dict) -> Tuple[Any, Argument]:
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


def decorator_factory(deco_factory: Callable = None, check_fn: Callable[[Any], bool] = callable):
    if check_fn != inspect.signature(decorator_factory).parameters["check_fn"].default:
        return update_wrapper(partial(decorator_factory, check_fn=check_fn), decorator_factory)

    @wraps(deco_factory)
    def _deco_factory(fn, *args, **kwargs):
        if not check_fn(fn):
            argname = list(inspect.signature(deco_factory).parameters)[1]
            kwargs[argname] = fn
            out = update_wrapper(partial(deco_factory, *args, **kwargs), deco_factory)
        else:
            out = deco_factory(fn, *args, **kwargs)
            fn = set_function_signature(fn)
            out = wraps(fn)(out)

        return out

    return _deco_factory
