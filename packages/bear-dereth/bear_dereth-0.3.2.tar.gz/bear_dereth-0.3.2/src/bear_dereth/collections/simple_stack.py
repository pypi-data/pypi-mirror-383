"""A Simple Stack implementation."""

from collections.abc import Iterator


class SimpleStack[T]:
    """A simple stack implementation."""

    def __init__(self, data: T) -> None:
        """Initialize an empty stack."""
        self._stack: list[T] = [data] if data is not None else []

    def push(self, item: T) -> None:
        """Push an item onto the stack."""
        self._stack.append(item)

    def pop(self) -> T:
        """Pop an item off the stack. Returns None if the stack is empty."""
        if self.empty:
            raise IndexError("pop from empty stack")
        return self._stack.pop()

    def peek(self) -> T:
        """Peek at the top item of the stack without removing it. Returns None if the stack is empty."""
        if self.empty:
            raise IndexError("peek from empty stack")
        return self._stack[-1]

    @property
    def empty(self) -> bool:
        """Check if the stack is empty."""
        return len(self._stack) == 0

    @property
    def not_empty(self) -> bool:
        """Check if the stack is not empty."""
        return len(self._stack) > 0

    def size(self) -> int:
        """Get the current size of the stack."""
        return len(self._stack)

    def clear(self) -> None:
        """Clear all items from the stack."""
        self._stack.clear()

    def __len__(self) -> int:
        """Get the current size of the stack using len()."""
        return len(self._stack)

    def __bool__(self) -> bool:
        """Check if the stack is non-empty using bool()."""
        return self.not_empty

    def __iter__(self) -> Iterator[T]:
        """Iterate over the stack from bottom to top."""
        return iter(self._stack)
