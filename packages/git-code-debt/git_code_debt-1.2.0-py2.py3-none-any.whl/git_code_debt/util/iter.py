from __future__ import annotations

import itertools
from collections.abc import Generator
from collections.abc import Iterable
from typing import TypeVar

T = TypeVar('T')


def chunk_iter(
        iterable: Iterable[T],
        n: int,
) -> Generator[tuple[T, ...]]:
    """Yields an iterator in chunks

    For example you can do

    for a, b in chunk_iter([1, 2, 3, 4, 5, 6], 2):
        print('{} {}'.format(a, b))

    # Prints
    # 1 2
    # 3 4
    # 5 6

    Args:
        iterable - Some iterable
        n - Chunk size (must be greater than 0)
    """
    assert n > 0
    iterable = iter(iterable)

    chunk = tuple(itertools.islice(iterable, n))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(iterable, n))
