"""Solution A — Top-K most frequent items."""
from __future__ import annotations

import heapq
from collections import Counter


def top_k_frequent(items: list[str], k: int) -> list[tuple[str, int]]:
    """Return the k most frequent items in `items`, paired with their counts,
    ordered most-frequent-first.

    Ties are broken by first-appearance order in `items` (the item that first
    appeared earlier wins). Returns [] if k <= 0.
    """
    if k <= 0:
        return []

    counts = Counter(items)
    # Counter preserves first-appearance order, so enumerating it gives a
    # stable index we can use for tiebreaking.
    indexed = [(count, -i, item) for i, (item, count) in enumerate(counts.items())]

    # nlargest by tuple compare: (count, -first_index, item).
    # Higher count wins; on ties, larger -first_index (i.e. smaller first_index,
    # i.e. earlier first appearance) wins.
    top = heapq.nlargest(k, indexed)
    return [(item, count) for count, _, item in top]
