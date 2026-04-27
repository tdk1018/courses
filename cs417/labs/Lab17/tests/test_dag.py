"""
Tests for Lab 17: DAGs and Task Scheduling.

Tests build task-scheduling scenarios using DAGNode, then run
topological sort to validate the resulting structure is a true DAG.
"""

import pytest
from dag import DAGNode, CycleError


# ---------- helpers ----------

def topo_sort(nodes):
    """Kahn's algorithm — returns a valid topological ordering.

    Raises ValueError if the graph has a cycle (not all nodes placed).
    Students don't implement this; it validates their DAG structure.
    """
    # Count in-degrees
    in_degree = {n: 0 for n in nodes}
    for n in nodes:
        if hasattr(n, 'dependencies') and n.dependencies:
            for dep in n.dependencies:
                if dep in in_degree:
                    in_degree[n] += 0  # n depends on dep
    # Recount: for each node, how many nodes depend on it?
    # Actually: in_degree[n] = number of n's dependencies
    in_degree = {}
    for n in nodes:
        deps = n.dependencies if hasattr(n, 'dependencies') and n.dependencies else set()
        in_degree[n] = len([d for d in deps if d in set(nodes)])

    queue = [n for n in nodes if in_degree[n] == 0]
    order = []

    while queue:
        node = queue.pop(0)
        order.append(node)
        for n in nodes:
            if hasattr(n, 'dependencies') and n.dependencies and node in n.dependencies:
                in_degree[n] -= 1
                if in_degree[n] == 0:
                    queue.append(n)

    if len(order) != len(nodes):
        raise ValueError("Cycle detected — not a valid DAG")
    return order


def assert_valid_topo_order(order, nodes):
    """Verify that order respects all dependency constraints."""
    position = {node: i for i, node in enumerate(order)}
    for node in nodes:
        deps = node.dependencies if hasattr(node, 'dependencies') and node.dependencies else set()
        for dep in deps:
            assert position[dep] < position[node], (
                f"{dep.name} should come before {node.name} "
                f"(dependency), but got position {position[dep]} >= {position[node]}"
            )


# ========== Task 1: __init__ ==========

class TestInit:
    """Test that DAGNode initializes correctly."""

    def test_name_stored(self):
        node = DAGNode("compile")
        assert node.name == "compile"

    def test_dependencies_empty(self):
        node = DAGNode("compile")
        assert isinstance(node.dependencies, set)
        assert len(node.dependencies) == 0

    def test_different_names(self):
        a = DAGNode("test")
        b = DAGNode("deploy")
        assert a.name == "test"
        assert b.name == "deploy"

    def test_nodes_are_independent(self):
        a = DAGNode("a")
        b = DAGNode("b")
        assert a.dependencies is not b.dependencies


# ========== Task 2: add_dependency (basic) ==========

class TestAddDependency:
    """Test basic dependency wiring and self-loop rejection."""

    def test_single_dependency(self):
        cook = DAGNode("cook")
        chop = DAGNode("chop")
        cook.add_dependency(chop)
        assert chop in cook.dependencies

    def test_multiple_dependencies(self):
        deploy = DAGNode("deploy")
        build = DAGNode("build")
        test = DAGNode("test")
        deploy.add_dependency(build)
        deploy.add_dependency(test)
        assert build in deploy.dependencies
        assert test in deploy.dependencies
        assert len(deploy.dependencies) == 2

    def test_self_loop_rejected(self):
        node = DAGNode("task")
        with pytest.raises(CycleError):
            node.add_dependency(node)

    def test_self_loop_no_side_effect(self):
        node = DAGNode("task")
        try:
            node.add_dependency(node)
        except CycleError:
            pass
        assert len(node.dependencies) == 0

    def test_duplicate_dependency_idempotent(self):
        a = DAGNode("a")
        b = DAGNode("b")
        a.add_dependency(b)
        a.add_dependency(b)  # adding again is fine
        assert len(a.dependencies) == 1

    def test_topo_sort_linear_chain(self):
        """Three tasks in a chain: c depends on b depends on a."""
        a = DAGNode("a")
        b = DAGNode("b")
        c = DAGNode("c")
        b.add_dependency(a)
        c.add_dependency(b)
        nodes = [a, b, c]
        order = topo_sort(nodes)
        assert_valid_topo_order(order, nodes)

    def test_topo_sort_diamond(self):
        """Diamond shape: d depends on b,c; b,c depend on a."""
        a = DAGNode("a")
        b = DAGNode("b")
        c = DAGNode("c")
        d = DAGNode("d")
        b.add_dependency(a)
        c.add_dependency(a)
        d.add_dependency(b)
        d.add_dependency(c)
        nodes = [a, b, c, d]
        order = topo_sort(nodes)
        assert_valid_topo_order(order, nodes)


# ========== Task 3: has_ancestor ==========

class TestHasAncestor:
    """Test ancestor detection via dependency chain walking."""

    def test_direct_dependency_is_ancestor(self):
        a = DAGNode("a")
        b = DAGNode("b")
        a.add_dependency(b)
        assert a.has_ancestor(b) is True

    def test_no_dependency_not_ancestor(self):
        a = DAGNode("a")
        b = DAGNode("b")
        assert a.has_ancestor(b) is False

    def test_transitive_ancestor(self):
        """a → b → c: c is an ancestor of a."""
        a = DAGNode("a")
        b = DAGNode("b")
        c = DAGNode("c")
        b.add_dependency(c)
        a.add_dependency(b)
        assert a.has_ancestor(c) is True

    def test_not_reverse_direction(self):
        """a → b: a is NOT an ancestor of b (wrong direction)."""
        a = DAGNode("a")
        b = DAGNode("b")
        a.add_dependency(b)
        assert b.has_ancestor(a) is False

    def test_deep_chain(self):
        """a → b → c → d → e: e is ancestor of a."""
        nodes = [DAGNode(str(i)) for i in range(5)]
        for i in range(1, 5):
            nodes[i - 1].add_dependency(nodes[i])
        assert nodes[0].has_ancestor(nodes[4]) is True
        assert nodes[0].has_ancestor(nodes[2]) is True
        assert nodes[3].has_ancestor(nodes[0]) is False

    def test_diamond_ancestors(self):
        """d depends on b,c; both depend on a. a is ancestor of d."""
        a = DAGNode("a")
        b = DAGNode("b")
        c = DAGNode("c")
        d = DAGNode("d")
        b.add_dependency(a)
        c.add_dependency(a)
        d.add_dependency(b)
        d.add_dependency(c)
        assert d.has_ancestor(a) is True
        assert d.has_ancestor(b) is True
        assert a.has_ancestor(d) is False

    def test_self_not_ancestor(self):
        a = DAGNode("a")
        assert a.has_ancestor(a) is False

    def test_unconnected_not_ancestor(self):
        """Parallel nodes with shared dependency aren't ancestors of each other."""
        root = DAGNode("root")
        left = DAGNode("left")
        right = DAGNode("right")
        left.add_dependency(root)
        right.add_dependency(root)
        assert left.has_ancestor(right) is False
        assert right.has_ancestor(left) is False


# ========== Task 4: cycle rejection ==========

class TestCycleRejection:
    """Test that add_dependency rejects edges that would create cycles."""

    def test_direct_cycle_rejected(self):
        """a → b, then b → a would create a cycle."""
        a = DAGNode("a")
        b = DAGNode("b")
        a.add_dependency(b)
        with pytest.raises(CycleError):
            b.add_dependency(a)

    def test_transitive_cycle_rejected(self):
        """a → b → c, then c → a would create a cycle."""
        a = DAGNode("a")
        b = DAGNode("b")
        c = DAGNode("c")
        b.add_dependency(a)
        c.add_dependency(b)
        with pytest.raises(CycleError):
            a.add_dependency(c)

    def test_cycle_rejection_no_side_effect(self):
        """Rejected edge shouldn't modify dependencies."""
        a = DAGNode("a")
        b = DAGNode("b")
        a.add_dependency(b)
        try:
            b.add_dependency(a)
        except CycleError:
            pass
        assert a not in b.dependencies

    def test_valid_edge_after_rejection(self):
        """Can still add valid edges after a rejection."""
        a = DAGNode("a")
        b = DAGNode("b")
        c = DAGNode("c")
        a.add_dependency(b)
        with pytest.raises(CycleError):
            b.add_dependency(a)
        # This is fine — c has no path to a
        b.add_dependency(c)
        assert c in b.dependencies

    def test_complex_dag_topo_sorts(self):
        """Build a realistic task schedule, verify topo sort works.

        Schedule:
            gather_ingredients
            chop_vegetables  → gather_ingredients
            boil_water       → gather_ingredients
            cook_pasta       → boil_water
            make_sauce       → chop_vegetables
            combine          → cook_pasta, make_sauce
            serve            → combine
        """
        gather = DAGNode("gather_ingredients")
        chop = DAGNode("chop_vegetables")
        boil = DAGNode("boil_water")
        pasta = DAGNode("cook_pasta")
        sauce = DAGNode("make_sauce")
        combine = DAGNode("combine")
        serve = DAGNode("serve")

        chop.add_dependency(gather)
        boil.add_dependency(gather)
        pasta.add_dependency(boil)
        sauce.add_dependency(chop)
        combine.add_dependency(pasta)
        combine.add_dependency(sauce)
        serve.add_dependency(combine)

        nodes = [gather, chop, boil, pasta, sauce, combine, serve]
        order = topo_sort(nodes)
        assert_valid_topo_order(order, nodes)

        # gather must be first (only node with no deps)
        assert order[0].name == "gather_ingredients"
        # serve must be last (nothing depends on it)
        assert order[-1].name == "serve"

    def test_complex_cycle_rejected(self):
        """Long chain cycle: a → b → c → d, then d → a."""
        nodes = [DAGNode(name) for name in ["a", "b", "c", "d"]]
        nodes[1].add_dependency(nodes[0])
        nodes[2].add_dependency(nodes[1])
        nodes[3].add_dependency(nodes[2])
        with pytest.raises(CycleError):
            nodes[0].add_dependency(nodes[3])
