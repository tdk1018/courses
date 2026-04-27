"""Basic test suite for Lab 22.

These tests are designed so that ALL THREE solutions pass. Run them first,
before doing any ranking. The fact that all three pass is the whole point of
the lab — passing the basic suite does NOT mean the solutions are equally good.

Run: pytest -v tests/test_basic.py
"""

import pytest


# Import all three solutions under their own names so we can parametrize over them.
from solution_a import top_k_frequent as top_k_a
from solution_b import top_k_frequent as top_k_b
from solution_c import top_k_frequent as top_k_c


SOLUTIONS = [
    pytest.param(top_k_a, id="solution_a"),
    pytest.param(top_k_b, id="solution_b"),
    pytest.param(top_k_c, id="solution_c"),
]


@pytest.mark.parametrize("top_k", SOLUTIONS)
class TestTopKBasic:
    """Small, well-behaved inputs — all three solutions should pass."""

    def test_simple_distinct_counts(self, top_k):
        items = ["a", "b", "a", "c", "a", "b"]
        # a:3, b:2, c:1
        assert top_k(items, 2) == [("a", 3), ("b", 2)]

    def test_k_equals_one(self, top_k):
        items = ["x", "y", "x", "z", "x"]
        assert top_k(items, 1) == [("x", 3)]

    def test_k_equals_unique_count(self, top_k):
        items = ["a", "b", "c", "a", "b", "a"]
        # a:3, b:2, c:1 — k == number of distinct items
        assert top_k(items, 3) == [("a", 3), ("b", 2), ("c", 1)]

    def test_ties_use_first_appearance(self, top_k):
        items = ["b", "a", "c", "a", "b", "c"]
        # a:2, b:2, c:2 — all tied; first-appearance order is b, a, c.
        assert top_k(items, 3) == [("b", 2), ("a", 2), ("c", 2)]

    def test_single_item(self, top_k):
        items = ["only"]
        assert top_k(items, 1) == [("only", 1)]

    def test_repeats_of_one_item(self, top_k):
        items = ["x", "x", "x", "x"]
        assert top_k(items, 1) == [("x", 4)]
