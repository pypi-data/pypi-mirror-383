"""Factory for creating field operations that work for both mappings and objects."""

from __future__ import annotations

from threading import RLock
from typing import TYPE_CHECKING, overload

from bear_dereth.di import Singleton
from bear_dereth.introspection import get_function_signature
from bear_dereth.typing_tools import LitFalse, LitTrue, is_mapping

if TYPE_CHECKING:
    from collections.abc import Callable
    from inspect import BoundArguments, Signature

PARAM_NAMES: set[str] = {"container", "ctx", "accessor", "transformer"}
PARAM_OPS: set[str] = {"getter", "setter", "deleter"}

_lock = RLock()


class FuncContainer[T]:
    """Container for getter and setter functions for a specific field."""

    _singleton: Singleton[FuncContainer] | None = None

    def __init__(self, doc: T | None = None) -> None:
        """Container for getter and setter functions for a specific field.

        Args:
            doc: The document (mapping or object) to operate upon.
        """
        self.doc: T = doc  # type: ignore[assignment]

    def update(self, doc: T) -> None:
        """Update the document being operated on."""
        self.doc = doc

    def getter[V](self, f: str) -> V:  # type: ignore[override]
        """Get the value of the specified field from a mapping or object."""
        if is_mapping(self.doc):
            return self.doc[f]
        return getattr(self.doc, f)

    @overload
    def setter[V](self, f: str, v: V, return_val: LitTrue) -> V: ...

    @overload
    def setter[V](self, f: str, v: V, return_val: LitFalse = False) -> None: ...  # type: ignore[override]

    def setter[V](self, f: str, v: V, return_val: bool = False) -> V | None:
        """Set the value of the specified field in a mapping or object."""
        reval = None
        if is_mapping(self.doc):
            self.doc[f] = v
            if return_val:
                reval = self.doc[f]
        else:
            setattr(self.doc, f, v)
            if return_val:
                reval = getattr(self.doc, f)
        return reval

    def deleter(self, f: str) -> None:
        """Delete the specified field from a mapping or object."""
        if is_mapping(self.doc):
            del self.doc[f]
        else:
            delattr(self.doc, f)

    @classmethod
    def get_singleton(cls) -> FuncContainer[T]:
        """Get the singleton instance of FuncContainer."""
        with _lock:
            if cls._singleton is None:
                cls._singleton = Singleton(cls)
            return cls._singleton.get()


def uses_func_container(sig: Signature, bound: BoundArguments, container: FuncContainer) -> BoundArguments:
    """Check if a function signature uses FuncContainer in its parameters and return bound arguments."""
    for param in sig.parameters:
        if sig.parameters[param].annotation is FuncContainer and param not in bound.arguments:
            bound.arguments[param] = container
    return bound


def is_func_container(sig: Signature, bound: BoundArguments) -> bool:
    """Check if a function signature uses FuncContainer in its parameters and return bound arguments."""
    for param in sig.parameters:
        if sig.parameters[param].annotation is FuncContainer and param not in bound.arguments:
            return True
    return False


def inject_ops(op_func: Callable) -> Callable[..., Callable[..., None]]:
    """Create a field operation that works for both mappings and objects."""

    def op_factory[T](*args, **kwargs) -> Callable[..., None]:
        def transform(doc: T) -> None:
            container: FuncContainer[T] = FuncContainer.get_singleton()
            container.update(doc)
            s: Signature = get_function_signature(op_func)
            b: BoundArguments = s.bind_partial(*args, **kwargs)
            for param in PARAM_OPS:
                if param in s.parameters and param not in b.arguments:
                    b.arguments[param] = container
            for param in PARAM_NAMES:
                if param in s.parameters and param not in b.arguments:
                    b.arguments[param] = container
            if is_func_container(s, b):
                b = uses_func_container(s, b, container)
            b.apply_defaults()

            op_func(**b.arguments)

        return transform

    return op_factory


# if __name__ == "__main__":

#     @inject_field_op
#     def lower_field(field: str, c: FuncContainer) -> None:
#         """Lowercase a string field."""
#         value = c.getter(field)
#         if isinstance(value, str):
#             c.setter(field, value.lower())
#         else:
#             raise TypeError(f"Field '{field}' is not a string.")

#     @dataclass
#     class SampleClass:

#         name: str
#         age: int

#     doc1: dict[str, Any] = {"name": "Alice", "age": 30}
#     doc2 = SampleClass(name="Bob", age=25)

#     lower_name: Callable[..., None] = lower_field("name")
#     lower_name(doc1)
#     lower_name(doc2)
#     print(doc1)  # {'name': 'alice', 'age': 30}
#     print(doc2)  # SampleClass(name='bob', age=25)
