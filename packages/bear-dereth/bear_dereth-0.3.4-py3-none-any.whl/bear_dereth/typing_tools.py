"""A set of type aliases and utility functions for type validation and inspection."""

from abc import ABC, abstractmethod
import builtins as _builtins
from collections.abc import Callable, Mapping, MutableMapping
from contextlib import suppress
import datetime
import keyword as _keyword
from pathlib import Path
from types import NoneType
from typing import TYPE_CHECKING, Any, Literal, NoReturn, TypeGuard, get_args

from bear_dereth.exceptions import ObjectTypeError
from bear_dereth.lazy_imports import lazy

LitInt = Literal["int"]
LitFloat = Literal["float"]
LitStr = Literal["str"]
LitBool = Literal["bool"]

LitFalse = Literal[False]
LitTrue = Literal[True]

OptInt = int | None
OptFloat = float | None
OptStr = str | None
OptBool = bool | None
OptStrList = list[str] | None
OptStrDict = dict[str, str] | None

NoReturnCall = Callable[..., NoReturn]

ast = lazy("ast")


def num_type_params(cls: type) -> int:
    """Get the number of type parameters of a subclass that inherits from a generic class.

    Args:
        cls (object): The class object from which to retrieve the number of type parameters.

    Returns:
        int: The number of type parameters.

    Raises:
        TypeError: If the class does not have type parameters.
        AttributeError: If the class does not have the expected type parameters.
    """
    try:
        args: tuple[Any, ...] = get_args(cls.__orig_bases__[0])
    except (AttributeError, TypeError):
        raise TypeError(f"{cls.__name__} does not have type parameters.") from None
    return len(args)


def type_param(cls: type, index: int = 0) -> type:
    """Get the type parameter of a subclass that inherits from a generic class.

    Args:
        cls (object): The class object from which to retrieve the type parameter.
        index (int): The index of the type parameter to retrieve. Defaults to 0.

    Returns:
        type: The type parameter at the specified index.

    Raises:
        IndexError: If the specified index is out of range for the type parameters.
        TypeError: If the class does not have type parameters.
        AttributeError: If the class does not have the expected type parameters.
    """
    try:
        args: tuple[Any, ...] = get_args(cls.__orig_bases__[0])
    except IndexError:
        raise IndexError(f"Index {index} is out of range for type parameters of {cls.__name__}.") from None
    except (AttributeError, TypeError):
        raise TypeError(f"{cls.__name__} does not have type parameters.") from None
    if args[index] is NoneType:
        raise TypeError(f"Type parameter at index {index} is NoneType for {cls.__name__}.")
    return args[index]


def mapping_to_type[T](mapping: Mapping, key: str, to_type: Callable[[Any], T], default: Any = None) -> T:
    """Get a value from a mapping and coerce it to the specified type if possible.

    Args:
        mapping (Mapping): The mapping from which to retrieve the value.
        key (str): The key of the value to retrieve.
        to_type (type): The type to which the value should be coerced.
        default (Any): The default value to return if the key is not found. Defaults to None.

    Returns:
        Any: The coerced value.

    Raises:
        ValueError: If the value cannot be coerced to the specified type.
    """
    if key not in mapping:
        if default is not None:
            return coerce_to_type(val=default, to_type=to_type)
        raise KeyError(f"Key {key} not found in mapping and no default provided.")
    return coerce_to_type(val=mapping[key], to_type=to_type)


def validate_type(val: Any, expected: type, exception: type[ObjectTypeError] | None = None) -> None:
    """Validate the type of the given value.

    Args:
        val (Any): The value to validate.
        expected (type): The expected type of the value.
        exception (type[ObjectTypeError] | None): The exception to raise if the type
            does not match. If None, a TypeError is raised.
    """
    if not isinstance(val, expected):
        if exception is None:
            raise TypeError(f"Expected object of type {expected.__name__}, but got {type(val).__name__}.")
        raise exception(expected=expected, received=type(val))


def TypeHint[T](hint: type[T]) -> type[T]:  # noqa: N802
    """Add type hints from a specified class to a base class:

    >>> class Foo(TypeHint(Bar)):
    ...     pass

    This would add type hints from class ``Bar`` to class ``Foo``.
    """
    if TYPE_CHECKING:
        return hint  # This adds type hints for type checkers

    class _TypeHintBase: ...

    return _TypeHintBase


class ArrayLike(ABC):
    """A protocol representing array-like structures (list, tuple, set)."""

    @abstractmethod
    def __iter__(self) -> Any: ...

    @classmethod
    @abstractmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        return hasattr(subclass, "__iter__") and subclass in (list, tuple, set)


class JSONLike(ABC):
    """A protocol representing JSON-like structures (dict, list)."""

    @abstractmethod
    def __setitem__(self, key: Any, value: Any) -> None: ...

    @abstractmethod
    def get(self, key: Any, default: Any = None) -> Any:
        """Get a value by key with an optional default."""

    @classmethod
    @abstractmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        return hasattr(subclass, "__setitem__") and subclass in (dict, list)


def is_json_like(instance: Any) -> TypeGuard[JSONLike]:
    """Check if an instance is JSON-like (dict or list)."""
    return isinstance(instance, (dict | list))


def is_array_like(instance: Any) -> TypeGuard[ArrayLike]:
    """Check if an instance is array-like (list, tuple, set)."""
    return isinstance(instance, (list | tuple | set))


def is_mapping(doc: Any) -> TypeGuard[MutableMapping]:
    """Check if a document is a mutable mapping (like a dict)."""
    return isinstance(doc, MutableMapping) or (hasattr(doc, "__getitem__") and hasattr(doc, "__setitem__"))


def is_object(doc: Any) -> TypeGuard[object]:
    """Check if a document is a non-mapping object."""
    return (
        isinstance(doc, object)
        and not isinstance(doc, MutableMapping)
        and not isinstance(doc, (int | float | str | bool | list | tuple | set))
    )


def a_or_b(a: Callable, b: Callable) -> Callable[..., None]:
    """Return a function that applies either a or b based on the type of the document."""

    def wrapper(doc: Any) -> None:
        if is_mapping(doc):
            a(doc)
        elif is_object(doc):
            b(doc)

    return wrapper


def str_to_bool(val: str) -> bool:
    """Convert a truthy string to a boolean value.

    Args:
        val (str): The string to convert.

    Returns:
        bool: The boolean value.
    """
    return str(val).strip().lower() in {"true", "1", "yes"}


def coerce_to_type[T](val: Any, to_type: Callable[[Any], T]) -> T:
    """Coerce a value to the specified type if possible.

    Args:
        val (Any): The value to coerce.
        to_type (type): The type to which the value should be coerced.

    Returns:
        Any: The coerced value.

    Raises:
        ValueError: If the value cannot be coerced to the specified type.
    """
    try:
        return to_type(val)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot coerce value {val} of type {type(val).__name__} to {to_type.__name__}.") from e


def infer_type(value: Any) -> str:
    """Infer the type of a value and return it as a string.

    Args:
        value: The value to infer the type of.

    Returns:
        A string representing the inferred type.
    """
    if str_to_bool(value):
        return "bool"

    with suppress(Exception):
        v = ast.literal_eval(value)
        if v is None:
            return "None"
        if isinstance(v, tuple):
            return "tuple"
        if isinstance(v, list):
            return "list"
        if isinstance(v, dict):
            return "dict"
        if isinstance(v, set):
            return "set"
        if isinstance(v, int):
            return "int"
        if isinstance(v, float):
            return "float"
        if isinstance(v, bytes):
            return "bytes"
    with suppress(Exception):
        path_test = Path(value)
        if path_test.exists() and (path_test.is_file() or path_test.is_dir()):
            return "Path"
    if isinstance(value, str):
        return "str"
    if isinstance(value, str):
        return "str"
    return "Any"


def str_to_type(str_type: str, default: Any = str) -> type:
    """Convert a string representation of a type to an actual type.

    Args:
        str_type (str): The string representation of the type.

    Returns:
        type: The corresponding Python type, or Any if not found.
    """
    type_map: dict[str, Any] = {
        "EpochTimestamp".lower(): int,
        "datetime": str,  # Keep as string; Pydantic handles datetime parsing at model level
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "path": Path,
        "bytes": bytes,
        "set": set,
        "frozenset": frozenset,
        "none": NoneType,
        "nonetype": NoneType,
        "any": Any,
    }
    return type_map.get(str_type.lower(), default)


def type_to_str(tp: type, arb_types_allowed: bool = False) -> str:
    """Convert a Python type to its string representation.

    Args:
        tp (type): The Python type to convert.
        arb_types_allowed (bool): Whether to allow arbitrary types. Defaults to False.

    Returns:
        str: The string representation of the type.
    """
    type_map: dict[Any, str] = {
        str: "str",
        int: "int",
        float: "float",
        bool: "bool",
        list: "list",
        dict: "dict",
        tuple: "tuple",
        Path: "path",
        bytes: "bytes",
        set: "set",
        frozenset: "frozenset",
        datetime: "datetime",
    }
    matching: str | None = type_map.get(tp)
    if matching is None and not arb_types_allowed:
        raise TypeError(f"Type {tp} is not supported.")
    return matching or "Any"


def check_for_conflicts(
    name: str,
    modifier: Callable | None = None,
    fallback: str = "{name}_",
) -> str:
    """Check if a name conflicts with Python built-ins or keywords.

    If there is a conflict, append an underscore to the name.

    Args:
        name (str): The name to check.
        modifier (Callable | None): Optional function to modify the name if there is a conflict.
        fallback (str): The format string to use if there is a conflict and no modifier is provided.

    Returns:
        str: The original name or the name with an appended underscore if there was a conflict.
    """
    if _keyword.iskeyword(name) or hasattr(_builtins, name):
        name = modifier(name) if modifier else fallback.format(name=name)
    return name


def format_default_value(value: Any) -> str:
    """Format a default value for string representation in code.

    Args:
        value (Any): The value to format.

    Returns:
        str: The formatted string representation of the value.
    """
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int | float)):
        return str(value)
    return repr(value)


if __name__ == "__main__":
    test = "(1, 2, 3)"
    test2 = "[1, 2, 3]"

    print(infer_type(test))
    print(infer_type(test2))
