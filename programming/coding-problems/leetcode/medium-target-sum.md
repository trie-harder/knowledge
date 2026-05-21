# Target Sum (LC 494) — Medium

> Given `nums` and `target`, assign `+` or `-` to each number. Return the **number of ways** to reach `target`.

---

## Key Insight — Count signals DP

The problem asks *how many* ways — not *which* ways. That's the signal to use DP rather than backtracking (which would enumerate all assignments at O(2^N)).

State: track a map of `{reachable_sum → number_of_ways}` as you process each number. For each number, every currently reachable sum splits into two: add `+num` or `-num`.

---

## Subproblem

```
dp[s] = number of ways to reach sum s using nums processed so far
```

### Recurrence

For each new `num`, every old sum `s` with `dp[s]` ways branches into two new sums:

```
new_dp[s + num] += dp[s]   # assigned + to this num
new_dp[s - num] += dp[s]   # assigned - to this num
```

### Base case

```
dp = {0: 1}    before processing any numbers, sum=0 in exactly 1 way
```

### Answer

`dp[target]` after processing all numbers (0 if target was never reached).

Since each step only depends on the previous step's dict, this naturally rolls — no 2D table needed.

---

## Trace for `nums=[1,1,1,1,1], target=3`

```
start:    {0: 1}

num=1:    {+1: 1, -1: 1}
num=1:    {+2: 1, 0: 2, -2: 1}
num=1:    {+3: 1, +1: 3, -1: 3, -3: 1}
num=1:    {+4: 1, +2: 4, 0: 6, -2: 4, -4: 1}
num=1:    {+5: 1, +3: 5, +1: 10, -1: 10, -3: 5, -5: 1}

dp[3] = 5  ✓
```

---

## Implementation

```python
from collections import defaultdict

def findTargetSumWays(nums: list[int], target: int) -> int:
    # dp maps reachable sum → number of ways to reach it
    dp = defaultdict(int)
    dp[0] = 1   # base: before any numbers, sum=0 in 1 way

    for num in nums:
        next_dp = defaultdict(int)
        for s, count in dp.items():
            next_dp[s + num] += count   # assign + to num
            next_dp[s - num] += count   # assign - to num
        dp = next_dp

    return dp[target]
```

**Time** O(N × S) — N numbers, S = number of distinct reachable sums (at most 2×sum(nums)+1)  
**Space** O(S) — the dict at each step

---

## Alternative — Subset Sum Reduction

Let `P` = sum of numbers assigned `+`, `N` = sum of numbers assigned `-`.

```
P + N = total      (all numbers sum to total)
P - N = target     (we want this)
─────────────────
    2P = total + target
     P = (total + target) / 2
```

So the problem reduces to: **count subsets that sum to `(total + target) / 2`**.

This only applies when `(total + target)` is even and `P >= 0`.

```python
def findTargetSumWays(nums: list[int], target: int) -> int:
    total = sum(nums)
    # If (total + target) is odd or P would be negative, no solution
    if (total + target) % 2 != 0 or total + target < 0:
        return 0

    goal = (total + target) // 2

    # Count subsets summing to goal (0/1 knapsack count variant)
    # dp[s] = number of subsets that sum to s
    dp = defaultdict(int)
    dp[0] = 1

    for num in nums:
        # Iterate in reverse to avoid using num twice (0/1 knapsack)
        for s in range(goal, num - 1, -1):
            dp[s] += dp[s - num]

    return dp[goal]
```

---

## Comparison

| | Dict DP (direct) | Subset Sum reduction |
|---|---|---|
| Intuition | straightforward branching | requires the algebra |
| Handles negatives in `nums` | yes | no (reduction assumes positive) |
| Space | O(S) dict | O(goal) array |
| Preferred | general case | positive nums + want O(N×goal) array DP |

---

## Why not backtracking?

Backtracking would work but runs O(2^N) — it enumerates every assignment. DP merges all paths that reach the same sum, so it runs O(N × S). The distinction: backtracking is correct when you need the actual assignments; DP is correct (and fast) when you only need the count.

*See also: [dynamic-programming.md](../../algorithms/dynamic-programming.md) — DP vs backtracking: scalar return = DP, collection return = backtracking*
