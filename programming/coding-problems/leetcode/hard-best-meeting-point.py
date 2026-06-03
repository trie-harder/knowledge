"""
LeetCode 296 - Best Meeting Point
---------------------------------

Problem:
Given a binary grid where 1 represents a home/friend and 0 represents empty space,
find a meeting point that minimizes the total Manhattan distance from all homes.
Return the minimum total distance.

Key question:
- In the original LeetCode 296 problem, the meeting point can be ANY grid cell.
  It does not have to be an empty cell.

--------------------------------------------------
1D -> 2D Derivation
--------------------------------------------------

1D from first principles:

1) Two friends at positions a <= b:
- Cost at meeting point x is:

    |x - a| + |x - b|

- If a <= x <= b, this becomes:

    (x - a) + (b - x) = b - a

- So ANY x in [a, b] is optimal.

2) Three friends at positions p0 <= p1 <= p2:
- If x < p1, moving right by 1 helps at least two terms and hurts at most one,
  so total cost goes down.
- If x > p1, moving left by 1 helps at least two terms and hurts at most one,
  so total cost goes down.
- Therefore x = p1 (the middle point) is optimal.

3) Four friends at positions q0 <= q1 <= q2 <= q3:
- For x in [q1, q2], there are two points on each side, so moving inside this
  interval creates equal increase/decrease in total distance.
- So every x in [q1, q2] is optimal.

4) General n friends at sorted positions f0 <= f1 <= ... <= f(n-1):
- We minimize:

    sum_i |x - fi|

- If n is odd, unique optimum is the middle friend f[n//2].
- If n is even, every x inbetween median friends [f[n/2 - 1], f[n/2]] is optimal.
- This is why "the median" is the optimizer for absolute-distance sums.

2D case:
- Manhattan distance between (r1, c1) and (r2, c2) is:

      |r1 - r2| + |c1 - c2|

- So total distance to meeting point (r, c) is:

      sum(|ri - r| + |ci - c|)
    = sum(|ri - r|) + sum(|ci - c|)

- This separates cleanly into TWO independent 1D problems:
  - choose best row using the median of all home rows
  - choose best col using the median of all home cols

So in 2D, solve two 1D median problems independently:
- row* = any median row of home rows
- col* = any median col of home cols

Then (row*, col*) is an optimal meeting point.

--------------------------------------------------
Original LC 296 Solution
--------------------------------------------------

Approach:
1. Collect all row indices containing a home.
2. Collect all column indices containing a home.
3. Pick median row and median column.
4. Sum distances to those medians.

Complexity:
- Time: O(m * n)
- Space: O(k), where k is the number of homes

Why O(m * n) without sorting?
- Rows are collected in sorted order naturally by scanning row by row.
- Cols are collected in sorted order naturally by scanning column by column.

"""

from typing import List


class Solution:
    def minTotalDistance(self, grid: List[List[int]]) -> int:
        rows = []
        cols = []

        m, n = len(grid), len(grid[0])

        # First pass: collect row coordinates in sorted order.
        for r in range(m):
            for c in range(n):
                if grid[r][c] == 1:
                    rows.append(r)

        # Second pass: collect column coordinates in sorted order.
        # We need this separate pass because row-major traversal does not keep
        # all column indices globally sorted, and median requires sorted order.
        for c in range(n):
            for r in range(m):
                if grid[r][c] == 1:
                    cols.append(c)

        # Median minimizes sum of absolute distances in 1D.
        # Because each friend contributes one entry, duplicates naturally encode
        # per-row/per-col weights (equivalent to a weighted median).
        row_median = rows[len(rows) // 2]
        col_median = cols[len(cols) // 2]

        total_distance = 0
        for r in rows:
            total_distance += abs(r - row_median)
        for c in cols:
            total_distance += abs(c - col_median)

        return total_distance


"""
--------------------------------------------------
If the Meeting Point MUST Be an Empty Cell
--------------------------------------------------

Then the pure median shortcut no longer directly solves the problem.

Why?
- The unconstrained optimum may land on a home cell.
- If only empty cells are legal, that median location may be invalid.
- The nearest empty cell is not always guaranteed by a simple local rule.

What still remains true:
- Manhattan distance still separates by rows and cols.
- So we can precompute:
  - row_cost[r] = total row distance to row r
  - col_cost[c] = total col distance to col c
- Then for every EMPTY cell (r, c), compute:

      row_cost[r] + col_cost[c]

- Return the minimum among legal empty cells.

That gives:
- Time: O(m * n + k * (m + n)) depending on how row/col costs are built
- Space: O(m + n + k)

Follow-up note (vs naive brute force):
- This is not the naive approach of checking every empty cell against every home.
- Naive brute force is O(E * k), worst-case O(m * n * k), where E = #empty cells.
- Here we reuse precomputed row/col costs, so each empty cell is O(1) to evaluate.

Simple implementation below.
"""


def min_total_distance_empty_only(grid: List[List[int]]) -> int:
    rows = []
    cols = []

    m, n = len(grid), len(grid[0])

    for r in range(m):
        for c in range(n):
            if grid[r][c] == 1:
                rows.append(r)
                cols.append(c)

    if not rows:
        return 0

    row_cost = [0] * m
    col_cost = [0] * n

    # Precompute total distance from each row to all homes.
    for r in range(m):
        total = 0
        for home_r in rows:
            total += abs(home_r - r)
        row_cost[r] = total

    # Precompute total distance from each col to all homes.
    for c in range(n):
        total = 0
        for home_c in cols:
            total += abs(home_c - c)
        col_cost[c] = total

    best = float("inf")
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 0:
                best = min(best, row_cost[r] + col_cost[c])

    return best if best != float("inf") else -1


if __name__ == "__main__":
    solution = Solution()

    grid = [
        [1, 0, 0, 0, 1],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
    ]
    assert solution.minTotalDistance(grid) == 6, "LC 296 test failed"

    # Empty-only variant example.
    grid2 = [
        [1, 0, 1],
        [0, 0, 0],
        [0, 1, 0],
    ]
    assert min_total_distance_empty_only(grid2) == 4, "Empty-only variant test failed"

    print("All tests passed")
