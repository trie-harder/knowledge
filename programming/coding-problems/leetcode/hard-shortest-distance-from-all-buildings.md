# LeetCode 317 — Shortest Distance from All Buildings

**Problem:**
Given a grid of values 0 (empty land), 1 (building), and 2 (obstacle), find the empty land cell such that the sum of the shortest distances from all buildings to that cell is minimized. Return the minimum sum, or -1 if it is not possible for all buildings to reach an empty land.

---

## Step-by-step Intuition

1. **Multi-source BFS:**
   - For each building, perform BFS to compute the shortest distance from that building to every reachable empty land cell.
   - Accumulate the total distance for each empty land cell across all buildings.
   - Also track how many buildings can reach each empty land cell.

2. **Result:**
   - After processing all buildings, for each empty land cell that is reachable from all buildings, check the total distance.
   - Return the minimum such distance. If no such cell exists, return -1.

---

## Solution (Python)

```python
from collections import deque

def shortestDistance(grid):
    if not grid or not grid[0]:
        return -1
    m, n = len(grid), len(grid[0])
    total_dist = [[0]*n for _ in range(m)]
    reach = [[0]*n for _ in range(m)]
    num_buildings = 0
    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    # BFS from each building
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 1:
                num_buildings += 1
                visited = [[False]*n for _ in range(m)]
                queue = deque([(r, c, 0)])
                visited[r][c] = True
                while queue:
                    x, y, dist = queue.popleft()
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < m and 0 <= ny < n and not visited[nx][ny]:
                            if grid[nx][ny] == 0:
                                total_dist[nx][ny] += dist + 1
                                reach[nx][ny] += 1
                                queue.append((nx, ny, dist + 1))
                                visited[nx][ny] = True
                            elif grid[nx][ny] == 1 or grid[nx][ny] == 2:
                                visited[nx][ny] = True
    # Find the minimum distance
    res = float('inf')
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 0 and reach[r][c] == num_buildings:
                res = min(res, total_dist[r][c])
    return res if res != float('inf') else -1
```

---

## Complexity Analysis
- **Time Complexity:** $O(B \cdot m \cdot n)$, where $B$ is the number of buildings, and $m$, $n$ are the grid dimensions. Each BFS visits each cell at most once per building.
- **Space Complexity:** $O(m \cdot n)$ for distance and reach matrices, plus BFS queue and visited matrix.

---

## Key Points
- Use BFS from each building to compute distances to all empty lands.
- Only consider empty lands reachable from all buildings.
- Track both total distance and reach count for each cell.

---

## Related Problems
- LeetCode 286: Walls and Gates
- LeetCode 542: 01 Matrix
- LeetCode 317: Shortest Distance from All Buildings (this problem)
