"""
Lab 16: Graphs — BFS and DFS

Graph class (complete — read and use it) and traversal functions (your job).
"""

from collections import deque


# ── Graph Class (provided) ─────────────────────────────────────────

class Graph:
    """An undirected graph using an adjacency list."""

    def __init__(self):
        self._adj = {}  # {label: [neighbor, ...]}

    def add_node(self, label):
        """Add a node to the graph. Does nothing if it already exists."""
        if label not in self._adj:
            self._adj[label] = []

    def add_edge(self, a, b):
        """Add an undirected edge between nodes a and b.

        Creates the nodes if they don't exist yet.
        """
        self.add_node(a)
        self.add_node(b)
        if b not in self._adj[a]:
            self._adj[a].append(b)
        if a not in self._adj[b]:
            self._adj[b].append(a)

    def get_neighbors(self, label):
        """Return the list of neighbors for the given node.

        Returns an empty list if the node doesn't exist.
        """
        return self._adj.get(label, [])

    def has_node(self, label):
        """Return True if the node exists in the graph."""
        return label in self._adj

    def nodes(self):
        """Return a list of all node labels."""
        return list(self._adj.keys())

    def __repr__(self):
        return f"Graph({dict(self._adj)})"


# ── Task 1: Build the Graph ───────────────────────────────────────

def build_lab_graph():
    """Build and return the lab graph.

    The graph looks like this:

        A
       / \\
      B   C
      |   |
      D   E
       \\ /
        F

    Edges: A-B, A-C, B-D, C-E, D-F, E-F
    """
    g = Graph()

    # TODO: Add all six nodes (A through F)
    # TODO: Add all six edges

    return g


# ── Task 2: Breadth-First Search ──────────────────────────────────

def bfs(graph, start):
    """Traverse the graph in breadth-first order starting from `start`.

    Returns a list of node labels in the order they were visited.
    """
    visited = set()
    order = []
    frontier = deque()

    # TODO: Add `start` to the frontier and mark it as visited

    while frontier:
        # TODO: Dequeue the next node from the front of the queue

        # TODO: Add the current node to the traversal order

        for neighbor in graph.get_neighbors(current):
            pass
            # TODO: If this neighbor hasn't been visited,
            #        mark it as visited and add it to the frontier

    return order


# ── Task 3: Depth-First Search ────────────────────────────────────

def dfs(graph, start):
    """Traverse the graph in depth-first order starting from `start`.

    Returns a list of node labels in the order they were visited.
    Uses an iterative approach with a stack (not recursion).
    """
    visited = set()
    order = []
    stack = []

    # TODO: Add `start` to the stack

    while stack:
        # TODO: Pop the next node from the top of the stack

        # TODO: If `current` has already been visited, skip it (continue).
        #        Otherwise, mark it as visited and add it to the order.

        for neighbor in graph.get_neighbors(current):
            pass
            # TODO: Add the neighbor to the stack

    return order


# ── Task 4: Find Path ────────────────────────────────────────────

def find_path(graph, start, goal):
    """Find the shortest path from `start` to `goal` using BFS.

    Returns a list of node labels representing the path (including both
    start and goal). Returns an empty list if no path exists.
    """
    if start == goal:
        return [start]

    visited = set()
    frontier = deque()
    parent = {}

    # TODO: Add `start` to the frontier, mark it as visited.
    #        The start node has no parent — you don't need to add it
    #        to the parent map.

    while frontier:
        # TODO: Dequeue the next node

        # TODO: Check if `current` is the goal. If yes:
        #        - Trace back through `parent` from goal to start
        #        - Reverse the path and return it
        #        (Hint: build a list by following parent[node] until
        #         you reach start, then reverse)

        for neighbor in graph.get_neighbors(current):
            pass
            # TODO: If the neighbor hasn't been visited:
            #        - Mark it as visited
            #        - Record its parent: parent[neighbor] = current
            #        - Add it to the frontier

    return []  # No path found
