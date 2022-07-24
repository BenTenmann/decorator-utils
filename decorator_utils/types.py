from typing import Any, Callable, Type, Union

from . import core


@core.decorator_factory
def check_input_argument(
        fn,
        argnum: int,
        passes: Callable,
        raises: Type[Exception],
        message: str
) -> Callable:
    argument_info = core.get_argument_info(fn, argnum)

    def _fn(*args, **kwargs):
        argument, _ = core.get_argument(argument_info, args, kwargs)
        if not passes(argument):
            raise raises(message)
        out = fn(*args, **kwargs)
        return out

    return _fn


@core.decorator_factory
def cast_argument_to_type(
        fn,
        argnum: int = 0,
        condition: Callable[[Any], bool] = lambda _: True,
        conversion: Callable[[Any], Any] = lambda e: e
) -> Callable:
    argument_info = core.get_argument_info(fn, argnum)

    def _fn(*args, **kwargs):
        argument, argument_type = core.get_argument(argument_info, args, kwargs)
        if condition(argument):
            argument = conversion(argument)
        args, kwargs = core.put_argument(argument, argument_info, argument_type, args, kwargs)
        out = fn(*args, **kwargs)

        return out

    return _fn


@core.decorator_factory
def cast_output_to_type(
        fn,
        output_index: Union[str, int],
        condition: Callable[[Any], bool] = lambda _: True,
        conversion: Callable[[Any], Any] = lambda e: e
) -> Callable:

    def _fn(*args, **kwargs):
        out = fn(*args, **kwargs)
        o_ = core.get_output(out, output_index)

        if condition(o_):
            o_ = conversion(o_)
            out = core.put_output(out, o_, output_index)
        return out

    return _fn
