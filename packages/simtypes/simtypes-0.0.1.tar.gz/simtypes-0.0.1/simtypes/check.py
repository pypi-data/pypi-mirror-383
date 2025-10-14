from inspect import isclass

try:
    from types import UnionType  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    from typing import Union as UnionType  # type: ignore[assignment]

from typing import Type, Union, Any, get_args, get_origin


def check(type: Type[Any], value: Any) -> bool:
    if type is Any:
        return True

    elif type is None:
        return value is None

    origin_type = get_origin(type)

    if origin_type is Union or origin_type is UnionType:
        return any(check(argument, value) for argument in get_args(type))

    else:
        if origin_type is not None:
            return isinstance(value, origin_type)

        if not isclass(type):
            raise ValueError('Type must be a valid type object.')

        return isinstance(value, type)
