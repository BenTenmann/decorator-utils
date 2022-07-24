import enum
from functools import wraps
from typing import Callable, Type

__all__ = [
    "format_enum_options",
    "get_enumerator_from_identifier",
    "not_implemented"
]


def format_enum_options(enumerator: Type[enum.Enum], formatter: Callable = lambda e: e.name) -> str:
    msg = ", ".join(map(formatter, enumerator))
    out = f"Must be one of: {msg}"
    return out


def get_enumerator_from_identifier(
        identifier: str,
        enumerator: Type[enum.Enum],
        identifier_transform: Callable = lambda identifier: identifier.strip().upper()
) -> enum.Enum:
    ident = identifier_transform(identifier)
    try:
        option = enumerator[ident]
    except KeyError:
        msg = format_enum_options(enumerator)
        raise ValueError(f"{ident!r} is not a valid identifier. {msg}")

    return option


def not_implemented(fn: Callable):

    @wraps(fn)
    def _fn(*args, **kwargs):
        raise NotImplementedError(f"{fn.__qualname__} is not implemented.")

    return _fn
