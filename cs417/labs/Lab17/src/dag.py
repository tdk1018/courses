"""
Lab 17: DAGs and Task Scheduling

Build a DAGNode class that represents a task with dependencies.
Nodes track their own dependencies and enforce the acyclic constraint.
"""


class CycleError(Exception):
    """Raised when adding a dependency would create a cycle."""
    pass


class DAGNode:
    """A node in a directed acyclic graph.

    Each node represents a task that may depend on other tasks.
    Dependencies are other DAGNode objects that must complete
    before this task can run.

    Example:
        cook = DAGNode("cook")
        chop = DAGNode("chop_vegetables")
        cook.add_dependency(chop)  # must chop before cooking
    """

    def __init__(self, name: str):
        """Initialize a DAGNode with a name and empty dependency set.

        TODO (Task 1): Store the name and create an empty set
        for dependencies.

        Args:
            name: Identifier for this task.
        """
        # TODO: Store name and initialize dependencies
        pass

    def add_dependency(self, node: "DAGNode") -> None:
        """Add a dependency to this node.

        TODO (Task 2): Add the given node to this node's dependencies.
        Raise CycleError if the node is self (a self-loop).

        TODO (Task 4 — upgrade): After implementing has_ancestor,
        come back and also reject any dependency that would create
        a cycle. Hint: if *this* node is an ancestor of the node
        we're adding, adding it would create a cycle.

        Args:
            node: The DAGNode that this task depends on.

        Raises:
            CycleError: If adding this dependency would create a cycle.
        """
        # TODO: Reject self-loops (Task 2)
        # TODO: Reject cycles using has_ancestor (Task 4)
        # TODO: Add the dependency
        pass

    def has_ancestor(self, target: "DAGNode") -> bool:
        """Check if target is an ancestor of this node.

        An ancestor is any node reachable by walking up the dependency
        chain. If A depends on B and B depends on C, then B and C are
        both ancestors of A.

        TODO (Task 3): Use DFS (or BFS) to walk the dependency graph.
        Start from this node's dependencies and search for target.

        Think about:
        - What's your starting set?
        - How do you avoid visiting the same node twice?
        - When do you return True vs False?

        Args:
            target: The node to search for.

        Returns:
            True if target is reachable via dependencies, False otherwise.
        """
        # TODO: Walk the dependency chain looking for target
        pass

    def __repr__(self):
        dep_names = sorted(d.name for d in self.dependencies) if hasattr(self, 'dependencies') else []
        return f"DAGNode({self.name!r}, deps={dep_names})"
