# Graph Traversal

See [graphs.md](../data-structures/graphs.md) for graph representations and terminology.

---

## DFS (Depth-First Search)

Explore as deep as possible along each branch before backtracking. Uses the **call stack** (recursive) or an explicit stack (iterative).

```python
def dfs(graph, start):
    visited = set()

    def explore(node):
        visited.add(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                explore(neighbour)

    explore(start)
```

Iterative version (explicit stack — note: visits in reverse neighbour order vs recursive):

```python
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                stack.append(neighbour)
```

---

## BFS (Breadth-First Search)

Explore all neighbours at the current depth before moving deeper. Uses a **queue**. Guarantees shortest path in unweighted graphs.

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbour in graph[node]:
            if neighbour not in visited:
                visited.add(neighbour)      # mark BEFORE enqueue
                queue.append(neighbour)
```

---

## Why BFS Must Mark Visited Before Enqueuing

The queue holds many nodes simultaneously. If you mark visited only on dequeue, the same node can be enqueued multiple times from different neighbours before it's ever processed:

```
Graph: 1 -- 2 -- 3
            |
            1    (back-edge to 1)

Queue after visiting 1: [2]
Process 2 → enqueue 1 and 3  → queue: [3, 1]
Process 3 → enqueue 2 again  → queue: [1, 2]   ← duplicate!
Process 1 again              → infinite loop
```

**Mark at enqueue** to prevent duplicates entering the queue at all.

### Why DFS Does Not Have This Problem

The call stack holds only **one active path** at a time. A node can't appear twice on the current root-to-node path in a simple graph — there's only one active frame per node at any moment, and the recursion is sequential. No "waiting room" accumulates duplicates.

| | BFS | DFS |
|---|---|---|
| Data structure | Queue — many nodes waiting | Call stack — one active path |
| Duplicate risk | Same node enqueued from multiple neighbours | Not possible on a single path |
| Mark visited | **Before enqueue** | At entry to call |
| Cost of marking late | Exponential re-processing / infinite loop | Only redundant checks |

---

## Complexity

| | Time | Space |
|---|---|---|
| BFS | O(V + E) | O(V) — queue + visited |
| DFS (recursive) | O(V + E) | O(V) — call stack + visited |
| DFS (iterative) | O(V + E) | O(V) — explicit stack + visited |

V = vertices, E = edges. Every vertex and edge is visited at most once.

---

## BFS vs DFS — When to Use Which

| Use case | Algorithm | Why |
|---|---|---|
| Shortest path (unweighted) | BFS | Explores level by level — first time a node is reached is via shortest path |
| Detect cycle | Either | DFS is more natural — track current path |
| Topological sort | DFS | Natural post-order gives reverse topo order |
| Connected components | Either | Just need full traversal |
| Nearest neighbour / closest in hops | BFS | Level-order guarantees minimum hops |
| Path exists | Either | DFS often simpler recursively |
| Exhaustive search / backtracking | DFS | Stack naturally handles state restoration |

---

## BFS Shortest Path with Distance Tracking

```python
from collections import deque

def shortest_path(graph, start, end):
    visited = {start}
    queue = deque([(start, 0)])   # (node, distance)
    while queue:
        node, dist = queue.popleft()
        if node == end:
            return dist
        for neighbour in graph[node]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append((neighbour, dist + 1))
    return -1   # unreachable
```

---

## Cycle Detection and Topological Sort in Directed Graphs

### Why directed graphs need two sets

In a directed graph you must distinguish between two different reasons for encountering an already-seen node:

| Situation | Meaning | Cycle? |
|---|---|---|
| Node is on the **current active DFS path** | Back edge — we've looped back | **Yes** |
| Node was **fully explored in a prior DFS call** | Cross edge — safe, already confirmed no cycle | **No** |

A single `visited` set can't make this distinction. You need:
- **`inStack`** — nodes on the current active path (GRAY)
- **`visited`** — nodes fully explored and confirmed cycle-free (BLACK)

```
Graph:  1 → 3
        2 → 3 → 4

DFS from 1: explores 1 → 3 → 4. Marks 3, 4 as visited (BLACK).
DFS from 2: explores 2 → 3. Sees 3 is BLACK → stop. No cycle, skip.

Without BLACK, DFS from 2 would re-traverse 3 → 4 unnecessarily.
```

---

### Two-set approach

```python
def has_cycle_directed(graph):
    visited = set()    # BLACK — fully explored, confirmed safe
    in_stack = set()   # GRAY  — on current DFS path

    def dfs(node):
        in_stack.add(node)
        for neighbour in graph[node]:
            if neighbour in in_stack:       # back edge → cycle
                return True
            if neighbour not in visited:    # not yet fully explored
                if dfs(neighbour):
                    return True
        in_stack.remove(node)
        visited.add(node)                   # fully done, mark BLACK
        return False

    return any(dfs(n) for n in graph if n not in visited)
```

---

### Tricolor algorithm — same logic, one structure

Encode both sets as a single value per node:

| Color | Meaning | Equivalent |
|---|---|---|
| WHITE (0) | Never visited | not in visited, not in inStack |
| GRAY (1) | On current DFS path | inStack |
| BLACK (2) | Fully explored | visited |

```python
def has_cycle_tricolor(graph, n):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {i: WHITE for i in range(n)}

    def dfs(node):
        if color[node] == GRAY:     # back edge → cycle
            return True
        if color[node] == BLACK:    # already confirmed safe → skip
            return False
        color[node] = GRAY
        for neighbour in graph[node]:
            if dfs(neighbour):
                return True
        color[node] = BLACK
        return False

    return any(dfs(i) for i in range(n) if color[i] == WHITE)
```

Tricolor is preferred in interviews — it's cleaner and avoids managing two separate sets.

---

### Why `visited` (BLACK) is an optimisation, not a correctness requirement

Just `inStack` alone correctly detects cycles. BLACK is a memoization layer that prevents re-exploring subgraphs already confirmed safe.

**Without BLACK — worst case:**

```
Long chain: 1 → 2 → 3 → 4 → ... → N
            2 → 3 → 4 → ... → N
            3 → 4 → ... → N
            ...

DFS from 1: traverses N nodes and edges
DFS from 2: re-traverses N-1 nodes and edges
DFS from 3: re-traverses N-2 ...

Total = N + (N-1) + ... + 1 = O(N²) = O(V²)
```

Each re-entry into a node re-traverses all its outgoing edges and the full subgraph below it — both nodes AND edges are re-explored.

**With BLACK:** DFS from 2 hits node 3 (BLACK) → stops immediately. Each node and edge is processed exactly once across all DFS calls → **O(V + E)**.

| | Correctness | Time (iterating all nodes) |
|---|---|---|
| `inStack` only | ✓ | O(V · (V + E)) worst case |
| `inStack` + `visited` (BLACK) | ✓ | **O(V + E)** |

BLACK is essential when iterating over all nodes as starting points (disconnected graphs, course schedule pattern). For a single-source DFS on a connected graph, `inStack` alone is both correct and efficient.

---

### Topological Sort — natural extension of cycle detection

Topological sort is a linear ordering of vertices such that for every directed edge u → v, u comes before v. **Only valid for DAGs** (no cycles).

The DFS post-order gives topological sort for free — a node is appended to the result *after* all its descendants are fully explored (when it turns BLACK). Reversing the post-order gives the correct topological ordering.

```python
def topo_sort(graph, n):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {i: WHITE for i in range(n)}
    order = []

    def dfs(node):
        if color[node] == GRAY:     # cycle — no valid topo order
            return False
        if color[node] == BLACK:    # already processed
            return True
        color[node] = GRAY
        for neighbour in graph[node]:
            if not dfs(neighbour):
                return False
        color[node] = BLACK
        order.append(node)          # append on BLACK — post-order
        return True

    for i in range(n):
        if color[i] == WHITE:
            if not dfs(i):
                return []           # cycle detected, no topo order

    return order[::-1]              # reverse post-order = topological order
```

**Why post-order gives topological sort:**
When a node turns BLACK, every node reachable from it has already turned BLACK and is already in `order`. So in the reversed list, this node appears before all its descendants — exactly the topological requirement.

```
Graph:  A → C
        B → C → D

Post-order appends: D, C, A, B  (or D, C, B, A — both valid)
Reversed:           B, A, C, D  ← valid topo order (A and B before C, C before D)
```

**Why tricolor is optimal here:**
Cycle detection and topological sort are done in a single O(V + E) pass. GRAY catches cycles immediately without extra work. BLACK memoizes completed nodes so disconnected components and multi-source graphs stay O(V + E) total.

---

### Kahn's Algorithm — BFS Topological Sort

Process nodes with no remaining dependencies first. Repeatedly pull nodes with in-degree 0 into the queue. Fully iterative — no recursion limit risk.

```python
from collections import deque

def topo_sort_kahns(graph, n):
    in_degree = [0] * n
    for node in graph:
        for neighbour in graph[node]:
            in_degree[neighbour] += 1

    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph[node]:
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:
                queue.append(neighbour)

    # fewer nodes processed than exist → cycle
    return order if len(order) == n else []
```

### DFS Tricolor vs Kahn's — Which to Use

| | DFS / Tricolor | Kahn's (BFS) |
|---|---|---|
| Time | O(V + E) | O(V + E) |
| Space | O(V) color + O(V) call stack | O(V) in-degree + O(V) queue |
| Cycle detection | GRAY hit during DFS — early exit | `len(order) < n` after full traversal |
| Order produced | Reverse post-order (needs `[::-1]`) | Natural dependency order directly |
| Recursion limit risk | Yes | No — fully iterative |
| Early cycle termination | Yes | No |

**Prefer Kahn's** for most practical problems (course schedule, build order) — iterative, no reversal, cycle check is one line.

**Prefer tricolor** when you need early cycle detection, are already doing DFS for another reason, or need DFS traversal order specifically.

---

### Cycle Detection — Undirected Graph

Undirected graphs only need one `visited` set — track the parent to avoid treating the edge you came from as a back-edge.

```python
def has_cycle_undirected(graph):
    visited = set()

    def dfs(node, parent):
        visited.add(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                if dfs(neighbour, node):
                    return True
            elif neighbour != parent:   # back-edge to non-parent = cycle
                return True
        return False

    return any(dfs(n, -1) for n in graph if n not in visited)
```

No `inStack` needed — in an undirected graph, any back edge to a non-parent is a cycle by definition. There are no cross edges to worry about.
