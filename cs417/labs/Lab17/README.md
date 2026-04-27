# Lab 17: DAGs and Task Scheduling

## Bridge from Lab 16

In Lab 16, we built general graphs with adjacency lists and explored BFS/DFS traversal. Those graphs allowed cycles — you could follow edges in a loop forever.

This lab narrows the focus: **directed acyclic graphs (DAGs)**. Same idea as a directed graph, but with one hard constraint — **no cycles allowed**. That constraint is what makes DAGs useful for modeling dependencies.

## Background: What is a DAG?

A **directed acyclic graph** is a graph where:
- Every edge has a direction (A → B doesn't mean B → A)
- There are no cycles (you can never follow edges and end up where you started)

DAGs show up everywhere:
- **Task scheduling**: "Task B depends on Task A finishing first"
- **Build systems**: Make, Gradle — compile dependencies before the things that need them
- **Course prerequisites**: CS 417 requires CS 315 requires CS 115
- **Spreadsheets**: Cell B2 depends on A1 and A3 — evaluated in dependency order

The key operation on a DAG is **topological sort** — finding an order where every node comes after all its dependencies. If you can topo-sort it, it's a valid DAG. If you can't, there's a cycle.

## Your Task

You'll build a `DAGNode` class that represents a task with dependencies. No wrapper class needed — nodes know their own dependencies and can detect cycles.

### The `DAGNode` Class

Each node has:
- A **name** (string) — the task identifier
- A **dependencies** set — other `DAGNode` objects this task depends on

### What You Implement

Open `src/dag.py`. You'll find the class skeleton with four tasks marked `TODO`:

| Task | Method | What It Does |
|------|--------|-------------|
| 1 | `__init__` | Initialize a node with a name and empty dependency set |
| 2 | `add_dependency(node)` | Add a dependency, rejecting self-loops |
| 3 | `has_ancestor(target)` | Check if `target` is reachable by walking up the dependency chain (DFS) |
| 4 | `add_dependency` (upgrade) | Upgrade `add_dependency` to reject **any** cycle, not just self-loops |

### How the Tasks Build on Each Other

- **Tasks 1-2** get the basic structure working. You can wire up dependencies.
- **Task 3** is the engine — `has_ancestor` walks the dependency graph to see if a node is reachable. This is DFS from Lab 16, applied to dependencies.
- **Task 4** ties it together — `add_dependency` uses `has_ancestor` to reject cycles *before* they happen.

### How Testing Works

The tests build task-scheduling scenarios using your `DAGNode` class, then run **topological sort** on the result to verify the structure is valid. You don't implement topo sort — the tests do. Your job is to make sure the graph they build is actually a DAG.

## Key Concepts

| Concept | What It Means |
|---------|--------------|
| DAG | Directed graph with no cycles |
| Dependency | "A depends on B" = edge from A to B |
| Topological sort | Ordering where every node comes after its dependencies |
| Cycle detection | Checking if adding an edge would create a loop |
| Self-loop | A node depending on itself (simplest cycle) |
| Ancestor | Any node reachable by following dependencies transitively |

## Running the Tests

```bash
cd Lab17
python -m pytest tests/ -v
```

Work through the tasks in order. Earlier tests will pass before later ones.
