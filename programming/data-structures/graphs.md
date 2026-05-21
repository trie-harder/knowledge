# Graphs

A **graph** is a set of **vertices** (nodes) connected by **edges**. Unlike trees, graphs can have cycles, disconnected components, and edges in both directions.

```
Undirected graph:        Directed graph (digraph):

   1 --- 2                  1 --> 2
   |   / |                  |     |
   |  /  |                  v     v
   3 --- 4                  3 <-- 4
```

---

## Terminology

| Term | Meaning |
|---|---|
| **Vertex / Node** | A point in the graph |
| **Edge** | A connection between two vertices |
| **Directed** | Edges have direction (A→B ≠ B→A) |
| **Undirected** | Edges are bidirectional |
| **Weighted** | Edges have an associated cost/distance |
| **Degree** | Number of edges connected to a vertex |
| **In-degree / Out-degree** | Directed: edges coming in / going out |
| **Path** | Sequence of vertices where each consecutive pair shares an edge |
| **Simple path** | Path with no repeated vertices |
| **Cycle** | Path that starts and ends at the same vertex |
| **Simple cycle** | Cycle with no repeated vertices (except start = end) |
| **DAG** | Directed Acyclic Graph — directed, no cycles |
| **Connected** | Every vertex reachable from every other (undirected) |
| **Disconnected** | At least one vertex unreachable from another — graph has multiple components |
| **Strongly connected** | Directed: every vertex reachable from every other vertex following edge directions |
| **Weakly connected** | Directed: connected if you ignore edge directions |
| **Component** | A maximal connected subgraph — no edges link it to the rest |
| **Strongly connected component (SCC)** | Maximal subgraph where every vertex can reach every other (directed) |
| **Bridge** | An edge whose removal disconnects the graph |
| **Articulation point** | A vertex whose removal disconnects the graph |
| **Tree** | Connected undirected graph with no cycles — always has exactly V-1 edges |
| **Forest** | Collection of trees (disconnected, acyclic) |
| **Spanning tree** | A tree that includes all vertices of a connected graph |
| **Minimum spanning tree (MST)** | Spanning tree with minimum total edge weight |
| **Bipartite** | Vertices split into two sets; edges only go between sets, never within |
| **Complete graph** | Every pair of vertices is connected — E = V(V-1)/2 |
| **Dense graph** | E ≈ V² — many edges relative to vertices |
| **Sparse graph** | E << V² — few edges; most real-world graphs |
| **Self-loop** | Edge from a vertex to itself |
| **Multi-edge** | Multiple edges between the same pair of vertices |
| **Simple graph** | No self-loops, no multi-edges |
| **Topological order** | Linear ordering of vertices such that for every directed edge u→v, u comes before v. Only exists in DAGs. |

### Connectivity — Visual Summary

```
Connected (undirected):    Disconnected:        Strongly connected (directed):

  1 - 2 - 3                1 - 2   4 - 5         1 → 2
      |                                           ↑   ↓
      4                    3       6              4 ← 3
  (one component)        (3 components)    (every node reachable from every other)
```

```
Bipartite:                 Tree (connected, acyclic, V-1 edges):

  A - 1                         1
  |   |                        / \
  B - 2                       2   3
  |                           |
  C - 3                       4
(sets {A,B,C} and {1,2,3})
```

---

## Valid Tree

A valid tree requires **three conditions**:

1. **Undirected**
2. **Connected** — every node reachable from every other
3. **Acyclic** — no cycles

These together produce the invariant: a tree of V nodes has **exactly V-1 edges**.

Any two conditions imply the third:

| Given | Implies |
|---|---|
| Connected + acyclic | Exactly V-1 edges |
| Connected + V-1 edges | Acyclic |
| Acyclic + V-1 edges | Connected |

**Why acyclic alone isn't enough:**
```
1 - 2    3 - 4     ← no cycles, but disconnected — not a tree
```

**Why connected alone isn't enough:**
```
1 - 2 - 3
|       |
└ - - - ┘         ← connected, but has a cycle — not a tree
```

### Validating a tree (LC 261 pattern)

```python
def valid_tree(n, edges):
    if len(edges) != n - 1:     # wrong edge count → immediately invalid
        return False             # too many = cycle, too few = disconnected
    # check connectivity via BFS/DFS/Union-Find
    # connected + V-1 edges guarantees a valid tree
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    visited = set()
    def dfs(node):
        visited.add(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                dfs(neighbour)
    dfs(0)
    return len(visited) == n
```

The `len(edges) != n - 1` guard eliminates both failure modes before traversal — O(1) early exit for most invalid inputs.

---

## Cycle Detection

| | Directed graph | Undirected graph |
|---|---|---|
| **DFS approach** | Tricolor (WHITE/GRAY/BLACK) — cycle = back edge to a GRAY node | Parent-tracking DFS — cycle = neighbour already visited that isn't your parent |
| **BFS approach** | Kahn's algorithm — cycle = processed node count < V | BFS with parent tracking — cycle = visited neighbour that isn't your parent |
| **Union-Find** | Not suitable (direction makes set-merging ambiguous) | ✓ — cycle = `union(u, v)` where u and v already share a root |
| **Key signal** | Back edge to an in-progress (GRAY) ancestor | Any edge to an already-visited non-parent node |
| **Topo sort side effect** | ✓ (DFS post-order and Kahn's both produce it) | ✗ (undirected graphs have no topological order) |
| **Complexity** | O(V+E) | O(V+E) or O(V·α(V)) with Union-Find |

**Quick rule of thumb:**
- Directed + need topo sort → Kahn's
- Directed + already in DFS → tricolor
- Undirected + simple → parent-tracking DFS
- Undirected + dynamic edges / disjoint sets problem → Union-Find

---

## Representations

### Adjacency List

Store a list of neighbours for each vertex. Standard choice for most problems.

```python
# Undirected graph
graph = {
    1: [2, 3],
    2: [1, 3, 4],
    3: [1, 2, 4],
    4: [2, 3]
}

# Directed graph
graph = {
    1: [2, 3],
    2: [4],
    3: [4],
    4: []
}

# Weighted (store tuples)
graph = {
    1: [(2, 5), (3, 1)],   # (neighbour, weight)
    2: [(4, 2)],
    3: [(4, 8)],
    4: []
}
```

### Adjacency Matrix

2D array where `matrix[i][j] = 1` (or weight) if edge exists.

```python
# 4 vertices, 0-indexed
matrix = [
    [0, 1, 1, 0],   # vertex 0 connects to 1, 2
    [1, 0, 1, 1],   # vertex 1 connects to 0, 2, 3
    [1, 1, 0, 1],
    [0, 1, 1, 0]
]
```

### Edge List

Just a list of `(u, v)` or `(u, v, weight)` pairs. Useful for algorithms that iterate over all edges (Kruskal's, Bellman-Ford).

```python
edges = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4)]
```

---

## Representation Comparison

| | Adjacency List | Adjacency Matrix | Edge List |
|---|---|---|---|
| Space | O(V + E) | O(V²) | O(E) |
| Check edge (u,v) | O(degree(u)) | **O(1)** | O(E) |
| Get all neighbours | **O(degree(u))** | O(V) | O(E) |
| Add edge | O(1) | O(1) | O(1) |
| Best for | Sparse graphs (most problems) | Dense graphs, fast edge lookup | Edge-centric algorithms |

Most graphs in practice are **sparse** (E << V²), so adjacency list is the default.

---

## Building from Edge Input

```python
from collections import defaultdict

def build_graph(n, edges, directed=False):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        if not directed:
            graph[v].append(u)
    return graph

# Example
edges = [[0,1],[1,2],[2,0]]
g = build_graph(3, edges)
# g = {0: [1, 2], 1: [0, 2], 2: [1, 0]}
```

---

## Complexity Summary

| Operation | Adj List | Adj Matrix |
|---|---|---|
| Space | O(V + E) | O(V²) |
| BFS / DFS | O(V + E) | O(V²) |
| Dijkstra (min-heap) | O((V + E) log V) | O(V²) |
| Bellman-Ford | O(V · E) | O(V³) |
| Floyd-Warshall (all pairs) | O(V³) | O(V³) |

### Why BFS / DFS is O(V + E)

Each vertex is processed at most once — once added to `visited`, it's never re-enqueued or re-entered: **O(V)** total vertex work.

Each edge is examined when iterating over a vertex's neighbour list. Summed across all vertices, total neighbour iterations = sum of all degrees = **2E** (undirected) or **E** (directed).

This is the **handshaking lemma**: every edge has two endpoints, so counting degrees across all vertices counts each edge twice.

```
Graph:  1 -- 2
        |  /
        3

Edges: (1,2), (1,3), (2,3)   → E = 3

Degrees:
  vertex 1: 2   vertex 2: 2   vertex 3: 2
  sum = 6 = 2E
```

Total work = O(V) vertex processing + O(E) edge scanning = **O(V + E)**.

An adjacency matrix forces O(V²) for BFS/DFS because you scan all V columns per row to find neighbours — even if most entries are 0. The adjacency list avoids this by only storing actual edges.

---

## Common Graph Problem Patterns

| Problem | Algorithm | Key idea |
|---|---|---|
| Shortest path (unweighted) | BFS | Level-order = min hops |
| Shortest path (weighted, no negative) | Dijkstra | Greedy min-heap |
| Shortest path (negative edges) | Bellman-Ford | Relax all edges V-1 times |
| All-pairs shortest path | Floyd-Warshall | DP over intermediate vertices |
| Cycle detection (undirected) | DFS + parent tracking | Back-edge to non-parent = cycle |
| Cycle detection (directed) | DFS tricolor (two-set) | GRAY = on current path; BLACK = safe |
| Topological sort (DFS) | Tricolor post-order | Append on BLACK, reverse result |
| Topological sort (BFS) | Kahn's algorithm | Process in-degree 0 nodes first; cycle if `len(order) < n` |
| Connected components | DFS/BFS per unvisited node | Count how many traversals needed |
| Minimum spanning tree | Kruskal's or Prim's | Greedy edge/vertex selection |
| Bipartite check | BFS 2-coloring | Colour alternately; conflict = not bipartite |

See [graph-traversal.md](../algorithms/graph-traversal.md) for BFS and DFS implementations.
