"""Itertools-like functions."""

from __future__ import annotations

from collections import defaultdict
from itertools import zip_longest
from typing import TYPE_CHECKING, Any

from bear_dereth.sentinels import NO_DEFAULT

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator, Sequence


REQUIRED_NUM: int = 2


def length(seq: Sequence) -> int:
    """Get the length of a sequence, or count items in an iterable.

    If the input has a __len__ method, it will be used to be lazy-evaluate the length.
    Otherwise, the function will iterate through the input to count the items.

    Args:
        seq (Sequence): The sequence or iterable to get the length of.

    Returns:
        int: The length of the sequence or count of items in the iterable.

    Example:
        >>> length([1, 2, 3, 4])
        4
        >>> length((x for x in range(5)))
        5
    """
    if hasattr(seq, "__len__"):
        return len(seq)
    return sum(1 for i in seq)


def freq(seq: Sequence) -> dict[str, int]:
    """Count the frequency of each item in a sequence.

    Args:
        seq (Sequence[str]): The sequence to count frequencies in.

    Returns:
        dict[str, int]: A dictionary mapping each item to its frequency.

    Example:
        >>> freq(["apple", "banana", "apple", "orange", "banana", "apple"])
        {'apple': 3, 'banana': 2, 'orange': 1}
    """
    d: defaultdict[str, int] = defaultdict(int)
    for item in seq:
        d[item] += 1
    return dict(d)


def diff(*seqs, **kwargs) -> Generator[tuple[Any, ...], Any]:
    """Return those items that differ between sequences

    Args:
        *seqs: Two or more sequences to compare.
        **kwargs: Optional keyword arguments:
            - min_size (int): Minimum number of sequences required (default: 2).
            - default: Value to use for missing items in shorter sequences (default: no_default).
            - key: Optional function to apply to each item before comparison (default: None).

    Yields:
        Tuples of items that differ between the sequences.

    Example:
        >>> list(diff([1, 2, 3], [1, 2, 4], [1, 3, 3]))
        [(2, 2, 3), (3, 4, 3)]
        >>> list(diff([1, 2], [1, 2, 3], default=0))
        [(0, 3)]
    """
    default: Any = kwargs.get("default", NO_DEFAULT)
    key: Any = kwargs.get("key")

    n: int = length(seqs)
    if n == 1 and isinstance(seqs[0], list):
        seqs = seqs[0]
        n = length(seqs)
    if n < REQUIRED_NUM:
        raise TypeError("Too few sequences given (min 2 required)")

    iters = zip(*seqs, strict=False) if default == NO_DEFAULT else zip_longest(*seqs, fillvalue=default)

    if key is None:
        for items in iters:
            if items.count(items[0]) != n:
                yield items
    else:
        for items in iters:
            vals: tuple[Any, ...] = tuple(map(key, items))
            if vals.count(vals[0]) != n:
                yield items


def pairwise(seq: Sequence) -> Generator[tuple[Any, Any], Any]:
    """Generate pairs of consecutive items from a sequence.

    Args:
        seq (Sequence): The sequence to generate pairs from.

    Yields:
        Tuples of consecutive items.

    Example:
        >>> list(pairwise([1, 2, 3, 4]))
        [(1, 2), (2, 3), (3, 4)]
        >>> list(pairwise("hello"))
        [('h', 'e'), ('e', 'l'), ('l', 'l'), ('l', 'o')]
    """
    if length(seq) < REQUIRED_NUM:
        return
    a: Any = seq[0]
    for b in seq[1:]:
        yield (a, b)
        a = b


def window(seq: Sequence, size: int) -> Generator[tuple[Any, ...], Any]:
    """Generate overlapping windows of a specified size from a sequence.

    Args:
        seq (Sequence): The sequence to generate windows from.
        size (int): The size of each window.

    Yields:
        Tuples representing each window.

    Example:
        >>> list(window([1, 2, 3, 4, 5], 3))
        [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
        >>> list(window("abcdef", 4))
        [('a', 'b', 'c', 'd'), ('b', 'c', 'd', 'e'), ('c', 'd', 'e', 'f')]
    """
    if size < 1:
        raise ValueError("Window size must be at least 1")
    if length(seq) < size:
        return
    it: Iterator[Any] = iter(seq)
    window_tuple: tuple[Any, ...] = tuple(next(it) for _ in range(size))
    yield window_tuple
    for x in it:
        window_tuple = (*window_tuple[1:], x)
        yield window_tuple


if __name__ == "__main__":
    seq1: list[int] = [1, 2, 3, 4]
    seq2: list[int] = [1, 2, 4, 4]
    seq3: list[int] = [1, 3, 3, 4]

    print("Diffs:")
    for diff_items in diff(seq1, seq2, seq3):
        print(diff_items)

    print("\nPairwise:")
    for pair in pairwise(seq1):
        print(pair)

    print("\nWindow:")
    for win in window(seq1, 3):
        print(win)
