# Lab 16: Graphs — BFS and DFS

## Overview

You've spent the last few labs inside trees — traversals, recursion, heaps. Trees have a comforting rule: every node has exactly one parent, and there are no cycles. You can walk a tree without worrying about getting stuck in a loop.

Graphs drop those rules. A node can connect to any other node. Paths can loop back on themselves. The same node might be reachable from three different directions. This changes everything about how you search.

In this lab, you'll implement the two fundamental graph traversal algorithms: **breadth-first search (BFS)** and **depth-first search (DFS)**. You won't build them from scratch — you'll get scaffolding that handles the structure, and your job is to fill in the key decisions: how to track where you've been, how to choose where to go next, and how to reconstruct the path you took.

Here's the thing that makes this worth doing by hand: BFS and DFS are almost the same algorithm. The difference is a single data structure swap. But that swap completely changes the behavior — and if you're ever directing an AI to search a space, you need to understand *which* search to ask for and *why*.

**Starter files:** `graph.py`, `test_graph.py`, `conftest.py`
**Test command:** `pytest -v` (from your Lab16 root)

## Part 1: Project Setup

```
Lab16/
├── README.md
├── conftest.py
├── src/
│   └── graph.py
└── tests/
    └── test_graph.py
```

1. Create the `src/` and `tests/` directories
2. Move files into their places
3. Verify: `pytest -v` — all tests should **fail**

```bash
git add -A && git commit -m "Lab 16: Organize project structure"
```

## Background: What's a Graph?

A **graph** is a set of **nodes** (also called vertices) connected by **edges**. Unlike a tree, there's no root, no parent/child hierarchy, and connections can go in any direction.

Here's a small graph:

```
  X --- Y
   \   /
    \ /
     Z
```

Three nodes, three edges: X-Y, X-Z, Y-Z. Notice that unlike a tree, there's a cycle — you can go X → Y → Z → X and end up back where you started.

### Adjacency Lists

The most common way to represent a graph in code is an **adjacency list**: for each node, store a list of its neighbors.

```python
{
    "X": ["Y", "Z"],
    "Y": ["X", "Z"],
    "Z": ["X", "Y"],
}
```

This is an **undirected** graph — if X connects to Y, then Y connects to X. Every edge appears twice in the adjacency list.

You'll use a `Graph` class that manages this for you. It handles adding nodes, adding edges (in both directions), and looking up neighbors. Your job isn't to build the data structure — it's to *traverse* it.

### The Problem with Cycles

In a tree, you can traverse without thinking about where you've been — every path leads somewhere new. In a graph, you can end up going in circles:

```
A → B → D → F → E → C → A → B → D → ...
```

That's an infinite loop. To prevent it, graph traversals track which nodes they've **visited**. Before exploring a node, you check: have I been here before? If yes, skip it. This is the piece that makes graph traversal different from tree traversal.

## Part 2: Build a Graph

### Task 1: Construct the Graph

Open `src/graph.py`. The `Graph` class is already complete — read through it and understand the API:

- `add_node(label)` — add a node
- `add_edge(a, b)` — connect two nodes (both directions)
- `get_neighbors(label)` — get a node's connections
- `has_node(label)` — check if a node exists

Now find the `build_lab_graph()` function at the bottom. Your job: build the graph from the diagram above. Add all six nodes and all six edges.

```
    A
   / \
  B   C
  |   |
  D   E
   \ /
    F
```

The edges are: A-B, A-C, B-D, C-E, D-F, E-F.

```bash
pytest -v -k "TestBuildGraph"
git add -A && git commit -m "Lab 16: Build the graph"
```

## Background: Two Ways to Search

Imagine you're standing at node A and you want to visit every node in the graph. You maintain a **frontier** — a collection of nodes you've discovered but haven't visited yet. Each step, you:

1. Take a node from the frontier
2. If you haven't visited it, mark it as visited and record it
3. Add its unvisited neighbors to the frontier

That's it. That's both BFS and DFS. The *only* difference is what kind of container the frontier is:

- **BFS uses a queue** (first in, first out). You process nodes in the order you discovered them. This explores the graph level by level — all neighbors first, then neighbors of neighbors.
- **DFS uses a stack** (last in, first out). You always explore the most recently discovered node. This dives deep down one path before backtracking.

Same loop. Same visited check. Different container. Completely different traversal order.

## Part 3: Breadth-First Search

### Task 2: Implement `bfs`

Find the `bfs(graph, start)` function in `graph.py`. The scaffolding gives you the overall structure — a frontier, a visited set, a results list. You need to fill in four pieces:

1. **Initialize** — add the start node to the frontier and mark it visited
2. **Dequeue** — get the next node from the front of the queue
3. **Record** — add the current node to the traversal order
4. **Explore neighbors** — for each unvisited neighbor, mark it visited and add it to the queue

BFS uses `collections.deque` as its queue. The key operations:
- `deque.append(x)` — add to the back
- `deque.popleft()` — remove from the front

Notice that you mark nodes as visited **when you add them to the queue**, not when you process them. This prevents the same node from being added to the queue multiple times.

Starting from A on our graph, BFS visits: **A, B, C, D, E, F** — level by level.

```bash
pytest -v -k "TestBFS"
git add -A && git commit -m "Lab 16: Implement BFS"
```

## Part 4: Depth-First Search

### Task 3: Implement `dfs`

Find the `dfs(graph, start)` function. The scaffolding looks almost identical to BFS. But there are two critical differences:

1. **The frontier is a stack**, not a queue. Use a regular Python list with `append()` and `pop()`.
2. **You check visited when you pop**, not when you push. This is because multiple paths might add the same node to the stack — you only want to process it once.

Fill in the pieces:

1. **Initialize** — add the start node to the stack
2. **Pop** — get the next node from the top of the stack
3. **Visit check** — if this node has already been visited, skip it. Otherwise, mark it and record it.
4. **Explore neighbors** — add all neighbors to the stack (even if some are visited — the check on pop will handle it)

Starting from A on our graph, DFS visits: **A, C, E, F, D, B** — diving deep before backtracking.

Take a moment after you pass the tests. Look at your `bfs` and `dfs` functions side by side. The structure is nearly identical. The difference is `deque` vs `list`, `popleft` vs `pop`, and *when* you check visited. That's it. That's the whole thing.

```bash
pytest -v -k "TestDFS"
git add -A && git commit -m "Lab 16: Implement DFS"
```

## Part 5: Finding a Path

### Task 4: Implement `find_path`

Traversal is useful on its own, but the real power is **pathfinding**. Can you get from node A to node F? And if so, what's the route?

Find the `find_path(graph, start, goal)` function. This is BFS with one addition: a **parent map**. Every time you add a neighbor to the queue, you record *which node you came from*. When you reach the goal, you trace back through the parent map to reconstruct the path.

Fill in the pieces:

1. **Initialize** — set up the queue, visited set, and parent map. The start node has no parent.
2. **Goal check** — when you dequeue a node, check if it's the goal. If yes, reconstruct and return the path.
3. **Track parents** — when you add a neighbor to the queue, record `parent[neighbor] = current`.
4. **Reconstruct** — trace back from the goal to the start using the parent map, then reverse.

If no path exists, return an empty list.

Why BFS for pathfinding? Because BFS explores level by level, the first time it reaches the goal is guaranteed to be via the **shortest path** (fewest edges). DFS might find *a* path, but it could be a long, winding one.

On our graph, `find_path(graph, "A", "F")` returns: **["A", "B", "D", "F"]** — one of the two shortest paths (3 edges).

```bash
pytest -v -k "TestFindPath"
git add -A && git commit -m "Lab 16: Implement find_path"
```

## Key Concepts

| Concept | What it means |
|---------|--------------|
| **Graph** | A set of nodes connected by edges — no root, no hierarchy, cycles allowed |
| **Adjacency list** | Representing a graph as a dictionary: each node maps to a list of its neighbors |
| **Visited set** | Tracks which nodes have been processed — prevents infinite loops in cyclic graphs |
| **Frontier** | The collection of discovered-but-not-yet-visited nodes |
| **BFS** | Breadth-first search — uses a queue, explores level by level, finds shortest paths |
| **DFS** | Depth-first search — uses a stack, explores deeply before backtracking |
| **Parent map** | Records how you reached each node — used to reconstruct the path after BFS |
| **Queue vs Stack** | The only structural difference between BFS and DFS — changes the entire traversal order |

## Submission

Push your completed code and submit your repo URL.

Your commit history should look something like:
```
Lab 16: Organize project structure
Lab 16: Build the graph
Lab 16: Implement BFS
Lab 16: Implement DFS
Lab 16: Implement find_path
```

```bash
git push
```
