"""Hard test suite for Lab 22.

DO NOT RUN THESE BEFORE COMPLETING PART 1 AND PART 2.

These tests are designed to expose differences between solutions that the basic
suite hides. Edge cases (k=0, k > unique items, empty input), tie semantics at
the boundary, and a mild stress test that any reasonable implementation handles
in well under a second.

The huge-input timing comparison lives in benchmark.py, not here.

Run: pytest -v tests/test_hard.py
"""

import pytest

from solution_a import top_k_frequent as top_k_a
from solution_b import top_k_frequent as top_k_b
from solution_c import top_k_frequent as top_k_c


SOLUTIONS = [
    pytest.param(top_k_a, id="solution_a"),
    pytest.param(top_k_b, id="solution_b"),
    pytest.param(top_k_c, id="solution_c"),
]


@pytest.mark.parametrize("top_k", SOLUTIONS)
class TestEdgeCases:
    """Inputs the basic suite did not cover."""

    def test_empty_input(self, top_k):
        assert top_k([], 5) == []

    def test_k_is_zero(self, top_k):
        assert top_k(["a", "b", "c"], 0) == []

    def test_k_greater_than_unique_count(self, top_k):
        items = ["a", "b", "a"]
        # Only 2 unique items; asking for 5 should return what we have.
        assert top_k(items, 5) == [("a", 2), ("b", 1)]

    def test_all_unique_items(self, top_k):
        items = ["a", "b", "c", "d", "e"]
        # All have count 1; first-appearance order wins.
        assert top_k(items, 3) == [("a", 1), ("b", 1), ("c", 1)]

    def test_negative_k(self, top_k):
        # Treat negative k like zero.
        assert top_k(["a", "b"], -1) == []


@pytest.mark.parametrize("top_k", SOLUTIONS)
class TestModerateStress:
    """A mild stress test. Any reasonable implementation finishes quickly here.
    The really revealing timing differences live in benchmark.py."""

    def test_moderate_input_correctness(self, top_k):
        # Build a 5,000-item input where 'hot' appears 1000x and the rest are
        # mostly unique noise.
        items = ["hot"] * 1000 + [f"noise_{i}" for i in range(4000)]
        result = top_k(items, 1)
        assert result == [("hot", 1000)]
