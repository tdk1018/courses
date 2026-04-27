"""Benchmark script for Lab 22.

Measures wall-clock time for each solution on increasing input sizes.
Students RUN this script (they don't write or modify it). Output goes to
stdout; copy the table into your writeup.

Run: python3 benchmark.py

The point of this script is to surface complexity differences that the basic
test suite hides. If one solution takes ~milliseconds at every size and another
takes seconds, that gap is your evidence.
"""

from __future__ import annotations

import random
import time
from typing import Callable

from src.solution_a import top_k_frequent as top_k_a
from src.solution_b import top_k_frequent as top_k_b
from src.solution_c import top_k_frequent as top_k_c


def make_input(n: int, vocab_size: int, seed: int = 0) -> list[str]:
    """Generate n items drawn from a vocabulary of `vocab_size` distinct strings."""
    rng = random.Random(seed)
    return [f"item_{rng.randrange(vocab_size)}" for _ in range(n)]


def time_one(fn: Callable[[list[str], int], list[tuple[str, int]]],
             items: list[str],
             k: int) -> float:
    """Run fn(items, k) once and return elapsed seconds."""
    start = time.perf_counter()
    fn(items, k)
    return time.perf_counter() - start


def run_table(label: str, sizes: list[int], vocab_for: Callable[[int], int], k: int) -> None:
    print(f"=== {label} ===")
    print(f"{'n':>10} | {'unique':>8} | {'A (heap)':>12} | {'B (sort)':>12} | {'C (loop)':>12}")
    print("-" * 72)
    for n in sizes:
        v = vocab_for(n)
        items = make_input(n, v)
        ta = time_one(top_k_a, items, k)
        tb = time_one(top_k_b, items, k)
        tc = time_one(top_k_c, items, k)
        print(f"{n:>10,} | {v:>8,} | {ta*1000:>10.2f}ms | {tb*1000:>10.2f}ms | {tc*1000:>10.2f}ms")
    print()


def main() -> None:
    k = 5

    # Regime 1: small fixed vocabulary. Unique count is bounded — most workloads
    # in the wild look something like this (e.g., counting status codes, US states).
    run_table(
        "Regime 1 — small fixed vocabulary (50 distinct items)",
        sizes=[100, 1_000, 10_000, 100_000],
        vocab_for=lambda n: 50,
        k=k,
    )

    # Regime 2: vocabulary scales with n. Unique items grow with input size — this
    # is the workload that exposes O(n * unique) blow-up. Think: counting URL paths
    # or user IDs in a log file where most are nearly-unique.
    run_table(
        "Regime 2 — vocabulary scales with n (unique ≈ n/2)",
        sizes=[100, 1_000, 10_000, 50_000],
        vocab_for=lambda n: max(1, n // 2),
        k=k,
    )

    print("How to read the tables:")
    print("  - Per-row: 10x more input. If a column's time grows ~10x, that's linear.")
    print("    If it grows ~100x, that's roughly quadratic.")
    print("  - Compare across regimes: which solutions are sensitive to unique-count?")
    print("    Which are insensitive? Which workload would you choose each for?")


if __name__ == "__main__":
    main()
