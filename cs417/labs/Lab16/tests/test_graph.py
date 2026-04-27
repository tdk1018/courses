"""
Tests for Lab 16: Graphs — BFS and DFS

Run: pytest -v
"""

import pytest
from graph import Graph, build_lab_graph, bfs, dfs, find_path


# ── Task 1: Build the Graph ───────────────────────────────────────

class TestBuildGraph:
    """Verify the lab graph has the correct nodes and edges."""

    def test_has_all_nodes(self):
        g = build_lab_graph()
        for label in ["A", "B", "C", "D", "E", "F"]:
            assert g.has_node(label), f"Missing node {label}"

    def test_node_count(self):
        g = build_lab_graph()
        assert len(g.nodes()) == 6

    def test_a_neighbors(self):
        g = build_lab_graph()
        assert sorted(g.get_neighbors("A")) == ["B", "C"]

    def test_b_neighbors(self):
        g = build_lab_graph()
        assert sorted(g.get_neighbors("B")) == ["A", "D"]

    def test_c_neighbors(self):
        g = build_lab_graph()
        assert sorted(g.get_neighbors("C")) == ["A", "E"]

    def test_d_neighbors(self):
        g = build_lab_graph()
        assert sorted(g.get_neighbors("D")) == ["B", "F"]

    def test_e_neighbors(self):
        g = build_lab_graph()
        assert sorted(g.get_neighbors("E")) == ["C", "F"]

    def test_f_neighbors(self):
        g = build_lab_graph()
        assert sorted(g.get_neighbors("F")) == ["D", "E"]


# ── Task 2: BFS ───────────────────────────────────────────────────

class TestBFS:
    """Breadth-first search: level-by-level traversal."""

    def test_bfs_from_a(self):
        g = build_lab_graph()
        result = bfs(g, "A")
        assert result == ["A", "B", "C", "D", "E", "F"]

    def test_bfs_visits_all_nodes(self):
        g = build_lab_graph()
        result = bfs(g, "A")
        assert set(result) == {"A", "B", "C", "D", "E", "F"}

    def test_bfs_no_duplicates(self):
        g = build_lab_graph()
        result = bfs(g, "A")
        assert len(result) == len(set(result)), "BFS visited a node more than once"

    def test_bfs_from_f(self):
        g = build_lab_graph()
        result = bfs(g, "F")
        # F's neighbors are D and E, then their neighbors, etc.
        assert result[0] == "F"
        assert set(result[1:3]) == {"D", "E"}
        assert set(result) == {"A", "B", "C", "D", "E", "F"}

    def test_bfs_single_node(self):
        g = Graph()
        g.add_node("X")
        assert bfs(g, "X") == ["X"]

    def test_bfs_two_nodes(self):
        g = Graph()
        g.add_edge("X", "Y")
        assert bfs(g, "X") == ["X", "Y"]


# ── Task 3: DFS ───────────────────────────────────────────────────

class TestDFS:
    """Depth-first search: deep exploration before backtracking."""

    def test_dfs_from_a(self):
        g = build_lab_graph()
        result = dfs(g, "A")
        assert result == ["A", "C", "E", "F", "D", "B"]

    def test_dfs_visits_all_nodes(self):
        g = build_lab_graph()
        result = dfs(g, "A")
        assert set(result) == {"A", "B", "C", "D", "E", "F"}

    def test_dfs_no_duplicates(self):
        g = build_lab_graph()
        result = dfs(g, "A")
        assert len(result) == len(set(result)), "DFS visited a node more than once"

    def test_dfs_from_f(self):
        g = build_lab_graph()
        result = dfs(g, "F")
        assert result[0] == "F"
        assert set(result) == {"A", "B", "C", "D", "E", "F"}

    def test_dfs_single_node(self):
        g = Graph()
        g.add_node("X")
        assert dfs(g, "X") == ["X"]

    def test_dfs_two_nodes(self):
        g = Graph()
        g.add_edge("X", "Y")
        assert dfs(g, "X") == ["X", "Y"]


# ── Task 4: Find Path ────────────────────────────────────────────

class TestFindPath:
    """BFS-based shortest path finding."""

    def test_path_a_to_f(self):
        g = build_lab_graph()
        path = find_path(g, "A", "F")
        assert path == ["A", "B", "D", "F"]

    def test_path_length_is_shortest(self):
        g = build_lab_graph()
        path = find_path(g, "A", "F")
        # Shortest path from A to F is 3 edges (4 nodes)
        assert len(path) == 4

    def test_path_a_to_a(self):
        g = build_lab_graph()
        assert find_path(g, "A", "A") == ["A"]

    def test_path_a_to_b(self):
        g = build_lab_graph()
        assert find_path(g, "A", "B") == ["A", "B"]

    def test_path_f_to_a(self):
        g = build_lab_graph()
        path = find_path(g, "F", "A")
        assert path[0] == "F"
        assert path[-1] == "A"
        assert len(path) == 4  # shortest is 3 edges

    def test_no_path_disconnected(self):
        g = Graph()
        g.add_node("X")
        g.add_node("Y")
        assert find_path(g, "X", "Y") == []

    def test_path_through_diamond(self):
        """Both A-B-D-F and A-C-E-F are valid shortest paths."""
        g = build_lab_graph()
        path = find_path(g, "A", "F")
        assert len(path) == 4
        assert path[0] == "A"
        assert path[-1] == "F"
