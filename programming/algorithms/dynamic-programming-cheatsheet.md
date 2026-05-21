# Dynamic Programming — Cheatsheet

> Condensed reference. Full detail: [dynamic-programming.md](dynamic-programming.md)

---

## Two Conditions

| Condition | Meaning |
|---|---|
| **Optimal substructure** | Optimal answer built from optimal sub-answers |
| **Overlapping subproblems** | Same sub-inputs recur from different paths |

---

## Identify a DP Problem

- "Maximum / minimum over all ways"
- "Count the number of ways"
- "Can you achieve X?" (feasibility)
- Choices at each step affect future choices → not independent → not greedy

**Count = DP. List all = Backtracking.**

---

## Two Implementations

| | Top-down | Bottom-up |
|---|---|---|
| Style | Recursion + `@lru_cache` | Iterative table |
| Natural for | Writing the recurrence first | Performance, large N |
| Downside | Python recursion limit (~1000) | Less intuitive to set up |
| Cache | Dict (scattered, slower) | Array (sequential, cache-friendly) |

---

## Recursion Direction

| Frame | Recurse toward | Example |
|---|---|---|
| `dp(i)` = answer *to reach* i | 0 (backward) | Fib, climbing stairs, coin change |
| `dp(i)` = answer *from* i to end | end (forward) | Grid min path sum |

---

## Space Optimisation

When `dp[i]` depends on only the last k states, drop the table:

```python
# fib: k=2
a, b = 0, 1
for _ in range(n):
    a, b = b, a + b
```

---

## Recurrences — Quick Reference

| Problem | Recurrence | Space |
|---|---|---|
| Fibonacci | `dp[i] = dp[i-1] + dp[i-2]` | O(1) |
| Climbing Stairs | `dp[i] = dp[i-1] + dp[i-2]` | O(1) |
| Min Cost Climbing Stairs | `dp[i] = cost[i] + min(dp[i-1], dp[i-2])` | O(1) |
| House Robber | `dp[i] = max(dp[i-1], dp[i-2] + nums[i])` | O(1) |
| Max Subarray (Kadane's) | `dp[i] = max(nums[i], dp[i-1] + nums[i])` | O(1) |
| Coin Change (min coins) | `dp[a] = min(dp[a-c]+1)` for each coin c | O(amount) |
| LCS | match: `dp[i-1][j-1]+1`, else: `max(dp[i-1][j], dp[i][j-1])` | O(min(M,N)) |
| 0/1 Knapsack | `dp[i][w] = max(skip, dp[i-1][w-wt]+val)` | O(W) |

---

## Complexity

| Dimension | Time | Space | Optimised space |
|---|---|---|---|
| 1D, window 1 | O(N) | O(N) | O(1) |
| 1D, window k | O(N) | O(N) | O(k) |
| 2D | O(M·N) | O(M·N) | O(min(M,N)) |

---

## DP vs Backtracking vs Greedy

| | DP | Backtracking | Greedy |
|---|---|---|---|
| Returns | Scalar (count/min/max) | Collection of results | Scalar |
| Explores | All options, caches | All options, prunes | Local best only |
| Correct | Always | Always | Only if greedy choice property holds |
| Speed | Polynomial | Exponential | Fastest |

---

## Worked Examples (condensed)

**Climbing Stairs (LC 70)** — ways to reach n stairs (1 or 2 at a time)
```python
a, b = 1, 1          # a=dp[0]=1, b=dp[1]=1 (b already at step 1)
for _ in range(n - 1):  # advance n-1 times to reach dp[n]
    a, b = b, a + b
return b
```

**Min Cost Climbing Stairs (LC 746)** — min cost to exit array
```python
for i in range(2, len(cost)): cost[i] += min(cost[i-1], cost[i-2])
return min(cost[-1], cost[-2])
```

**House Robber (LC 198)** — max loot, no two adjacent
```python
prev2 = prev1 = 0
for n in nums: prev2, prev1 = prev1, max(prev1, prev2 + n)
return prev1
```

**Coin Change (LC 322)** — min coins for amount
```python
dp = [float('inf')] * (amount + 1); dp[0] = 0
for a in range(1, amount + 1):
    for c in coins:
        if c <= a: dp[a] = min(dp[a], dp[a-c] + 1)
return dp[amount] if dp[amount] != float('inf') else -1
```
