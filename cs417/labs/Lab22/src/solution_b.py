"""Solution B — Top-K most frequent items."""
from __future__ import annotations

from collections import Counter


def top_k_frequent(items: list[str], k: int) -> list[tuple[str, int]]:
    """Return the k most frequent items with their counts, most frequent first.

    Ties are broken by first-appearance order in `items`. Returns [] if k <= 0.
    """
    if k <= 0:
        return []

    counts = Counter(items)

    # Build (item, count, first_index) for every unique item and sort the whole
    # thing, then slice off the top k.
    entries = [(item, count, i) for i, (item, count) in enumerate(counts.items())]
    entries.sort(key=lambda e: (-e[1], e[2]))

    return [(item, count) for item, count, _ in entries[:k]]
