# LeetCode 1293 — Shortest Path in a Grid with Obstacles Elimination

**Problem:**
Given a grid with 0s (empty) and 1s (obstacles), find the shortest path from the top-left to the bottom-right, moving in 4 directions. You can eliminate up to k obstacles. Return the minimum number of steps, or -1 if impossible.

---

## Step-by-step Intuition

### 1. Brute Force (for intuition)
- Try all possible paths from (0,0) to (m-1,n-1), keeping track of how many obstacles you have eliminated so far (must not exceed k).
- For each cell, you can move up/down/left/right if in bounds.
- If you step on an obstacle, increment the count of obstacles eliminated.
- If you reach the end, record the path length if you have not exceeded k eliminations.
- **Why it's not feasible:** The number of possible paths is exponential in grid size and k. Too slow for real input.

### 2. BFS with State (Optimal)
- **Key insight:** This is a shortest path problem with an extra state: how many obstacles you have eliminated so far.
- Use BFS (breadth-first search) to guarantee the shortest path.
- Each BFS state is (row, col, obstacles_eliminated).
- For each move:
    - If the next cell is empty (0), move as usual.
    - If the next cell is an obstacle (1) and you have eliminations left, use one elimination and move.
- **Avoid revisiting worse states:**
    - If you reach (r, c) with fewer obstacles eliminated than before, it's a better state. Only revisit if you have more eliminations left than any previous visit to that cell.
- Use a queue for BFS and a 2D array (or dict) to track the minimum obstacles eliminated to reach each cell.

---

## Solution (Python, BFS)

```python
from collections import deque

def shortestPath(grid, k):
    m, n = len(grid), len(grid[0])
    # (row, col, obstacles_eliminated)
    queue = deque([(0, 0, 0, 0)])  # (r, c, steps, obstacles_eliminated)
    seen = dict()  # (r, c) -> min obstacles_eliminated
    seen[(0, 0)] = 0
    while queue:
        r, c, steps, obs = queue.popleft()
        if (r, c) == (m-1, n-1):
            return steps
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n:
                # Important: new_objs_eliminated must be local to each neighbor!
                # Do NOT mutate objs_eliminated in-place, or it will affect other directions.
                new_objs_eliminated = obs + grid[nr][nc]
                if new_objs_eliminated <= k:
                    # Only proceed if this path uses fewer eliminations than any previous path to (nr, nc)
                    if (nr, nc) not in seen or new_objs_eliminated < seen[(nr, nc)]:
                        seen[(nr, nc)] = new_objs_eliminated
                        queue.append((nr, nc, steps+1, new_objs_eliminated))
    return -1
```

### Complexity Analysis (BFS with State)

- **Time Complexity:** $O(m \times n \times k)$
    - Each cell $(r, c)$ can be visited up to $k+1$ times (for each possible number of obstacles eliminated from $0$ to $k$).
    - For each state, we process up to 4 neighbors, so the total number of BFS iterations is $O(m \times n \times k)$.

- **Space Complexity:** $O(m \times n \times k)$
    - The queue can hold up to $O(m \times n \times k)$ states in the worst case (every cell, for every possible number of eliminations used).
    - The `seen` dictionary also stores up to $O(m \times n)$ entries, each with up to $k+1$ possible elimination counts.

Where:
- $m$ = number of rows
- $n$ = number of columns
- $k$ = maximum obstacles that can be eliminated


## How this solution was derived
- **Brute force** is too slow, but it reveals that the only thing that matters is your position and how many obstacles you've eliminated so far.
- **BFS** is used because we want the shortest path (minimum steps). BFS explores all paths of length N before N+1, so the first time we reach the end, it's optimal.
- **State tracking**: We must track not just (row, col), but also how many obstacles we've eliminated to get there. This is because reaching the same cell with fewer eliminations left is strictly better (more flexibility for the future).
- **Pruning**: We avoid revisiting states that are strictly worse (more eliminations used to reach the same cell).

---

## Notes on Cycles and Revisiting Cells
- In this problem, you do not need to worry about trivial cycles (e.g., going back and forth between two cells) as long as you only revisit a cell if you arrive with strictly fewer obstacles eliminated than any previous visit.
- The state is (row, col, obstacles_eliminated). If you revisit a cell with the same or more eliminations used, it cannot lead to a better solution.
- If you revisit with fewer eliminations used, it’s a strictly better state and should be explored.
- This property prevents trivial cycles from causing inefficiency or infinite loops.

---

### Brute Force Pseudocode (cleaned up)

```python
# Try all possible paths from (0,0) to (m-1,n-1), keeping track of how many obstacles have been eliminated so far.
# At each step, you can move up, down, left, or right (if in bounds).
# If you step on an obstacle, increment the count of obstacles eliminated.
# If you reach the end, record the path length if you have not exceeded k eliminations.
# Use a visited set to avoid revisiting the same cell with the same or fewer eliminations left (optional for brute force, but helps avoid cycles).

def dfs(r, c, steps, eliminated):
    if (r, c) is out of bounds or eliminated > k:
        return float('inf')
    if (r, c) == (m-1, n-1):
        return steps
    min_steps = float('inf')
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r + dr, c + dc
        if grid[nr][nc] == 1:
            min_steps = min(min_steps, dfs(nr, nc, steps+1, eliminated+1))
        else:
            min_steps = min(min_steps, dfs(nr, nc, steps+1, eliminated))
    return min_steps

# Call dfs(0, 0, 0, 0). If result == float('inf'), return -1.
```

---

## Complexity
- **Time:** O(m * n * k) — each cell can be visited up to k+1 times (for each possible number of eliminations used).
- **Space:** O(m * n * k) — for the queue and the seen dictionary.

---

## Key phrases
- BFS with extra state (obstacles eliminated)
- Prune worse states (don't revisit with more eliminations used)
- State = (row, col, obstacles_eliminated)
- Shortest path in grid with constraints



# Important property:
- If you step onto an obstacle (cell == 1) and have eliminations left, it is always optimal to use an elimination.
- There is no benefit to "saving" an elimination for later if you are already on an obstacle—you must use it to proceed.
- The only time you cannot eliminate is when you have no eliminations left, in which case you cannot step onto an obstacle at all.
- This property simplifies the decision: always increment the elimination count when stepping onto a 1, if you have eliminations left.

---

## Note: Revisiting Cells in Modified BFS vs. Traditional BFS
- In traditional BFS, you mark a cell as visited the first time you reach it, regardless of the path taken, because all paths to that cell are equivalent in terms of cost.
- In this problem, the state includes not just the cell position but also the number of obstacle eliminations used so far.
- You can revisit a cell if you arrive with fewer obstacles eliminated (i.e., more eliminations available for future obstacles). This path may allow you to reach the target faster by removing more obstacles later.
- Thus, the "visited" check is not just on (row, col), but on (row, col, obstacles_eliminated). This is a key difference from standard BFS.

---

## Related LeetCode Problems with Modified BFS (Stateful Visited)
- **LeetCode 864: Shortest Path to Get All Keys**
  - Grid with walls, locks, and keys. State includes position and set of keys collected. You can revisit a cell if you have a different set of keys.
- **LeetCode 847: Shortest Path Visiting All Nodes**
  - On a graph, find the shortest path that visits every node. State includes current node and set of visited nodes (bitmask). You can revisit nodes if the set of visited nodes is different.
- **LeetCode 773: Sliding Puzzle**
  - BFS over board configurations. State is the board configuration; you revisit a configuration only if it hasn't been seen before.
- **LeetCode 542: 01 Matrix** (classic BFS, but for reference)
  - Each cell is visited only once, as all paths to a cell are equivalent (no extra state).
- **LeetCode 499: The Maze III**
  - State includes position and path so far; you may revisit a cell if you arrive with a shorter path.

**Key property:** In all these problems, the BFS state includes more than just the position—often a bitmask, set, or count. You may revisit a cell if the extra state is more optimal (e.g., more keys, fewer steps, more eliminations left).
