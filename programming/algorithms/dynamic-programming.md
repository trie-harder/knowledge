# Dynamic Programming

## Why DP Was Invented

Richard Bellman coined the term in the 1950s while working at RAND Corporation. The name was deliberate obfuscation — "programming" meant *planning* (not code), and "dynamic" sounded impressive enough to shield the work from bureaucratic scrutiny. The underlying principle predates him, but Bellman formalised it as the **principle of optimality**: an optimal solution must consist of optimal sub-solutions.

The problem DP solves is straightforward: naive recursion recomputes identical subproblems exponentially many times. `fib(40)` without memoisation makes ~2.7 billion calls. With memoisation it makes 40. That gap — exponential to polynomial — is the entire motivation.

### Benefits
- Converts exponential brute-force to polynomial time by storing subproblem results
- **Correct** — unlike greedy, it explores all options and picks the best
- Systematic: once you identify the recurrence, the code follows mechanically

### Tradeoffs
- **Space cost**: storing the DP table adds O(N) to O(N²) memory
- **Harder to design**: requires identifying subproblem structure and recurrence — non-trivial for 2D problems
- **Python recursion limit**: top-down hits Python's default ~1000 frame limit; use bottom-up or `sys.setrecursionlimit` for large N
- Overkill when a greedy choice property exists — greedy is simpler and faster

---

## What is Dynamic Programming?

DP solves problems by breaking them into overlapping subproblems, solving each subproblem once, and reusing the result. The key insight is that the same subproblem appears repeatedly — without memoisation you'd recompute it exponentially many times.

Two conditions must hold:

**1. Optimal substructure**
The optimal solution to the problem can be constructed from optimal solutions to its subproblems.

**2. Overlapping subproblems**
The same subproblems recur — not just divide-and-conquer's independent splits, but the same sub-inputs hit repeatedly from different paths.

---

## Forward-Looking vs Backward-Looking DP

How you *define* `dp[i]` determines the dependency direction, which in turn determines the fill order.

**Backward-looking**: `dp[i]` = "best answer considering elements 0 through i"
- Depends on smaller indices: `dp[i-1]`, `dp[i-2]`
- Fill left → right (0 → N)
- Base cases at the **start**

**Forward-looking**: `dp[i]` = "best answer from element i to the end"
- Depends on larger indices: `dp[i+1]`, `dp[i+2]`
- Fill right → left (N → 0)
- Base cases at the **end**

### Same problem, two valid framings — House Robber

| | Backward-looking | Forward-looking |
|---|---|---|
| Definition | `dp[i]` = max loot from house 0 to i | `dp[i]` = max loot from house i to end |
| Recurrence | `dp[i] = max(dp[i-1], dp[i-2] + nums[i])` | `dp[i] = max(dp[i+1], dp[i+2] + nums[i])` |
| Base cases | `dp[0]=nums[0]`, `dp[1]=max(nums[0],nums[1])` | `dp[N]=0`, `dp[N-1]=nums[N-1]` |
| Fill order | 0 → N | N → 0 |
| Return | `dp[N-1]` | `dp[0]` |

```python
# backward-looking (fill forward)
dp[0] = nums[0]                      # base: one house, rob it
dp[1] = max(nums[0], nums[1])        # base: two houses, rob the better one
for i in range(2, N):
    dp[i] = max(dp[i-1], dp[i-2] + nums[i])
return dp[N-1]

# forward-looking (fill backward)
# dp[N] = 0 is cleaner than dp[N-1]/dp[N-2] as explicit bases because:
#   1. "past the end = no loot = 0" is a natural sentinel — no special-casing
#   2. the first loop iteration (i=N-2) computes dp[N-2] = max(dp[N-1], dp[N] + nums[N-2])
#      = max(nums[N-1], nums[N-2]) automatically, so you don't hardcode it
#   3. handles len(nums)==1 without an early return
dp[N] = 0                            # sentinel: no houses left, no loot
dp[N-1] = nums[N-1]                  # base: one house left, rob it
for i in range(N-2, -1, -1):
    dp[i] = max(dp[i+1], dp[i+2] + nums[i])
return dp[0]
```

Climbing Stairs and Min Cost Climbing Stairs are naturally backward-looking (`dp[i]` = ways/cost to reach step `i`). House Robber can be either. The forward-looking framing matches the recursive top-down solution (`robFrom(i)` = "what can I rob from here?") more directly; the backward-looking framing rolls into the compact `prev2, prev1` pattern more cleanly.

**The rule**: fill direction must match dependency direction — if `dp[i]` uses larger indices, fill backward; if it uses smaller indices, fill forward.

---

## Recursion Direction

The direction of the recursion is determined by how you frame the subproblem.

**`dp(i)` = "answer for the first i things / to reach state i"** → recurse *backward* to `dp(i-1)`
```python
# fib, climbing stairs, coin change, house robber
dp(n) → dp(n-1), dp(n-2)   # n shrinks toward base case 0
```

**`dp(i)` = "answer starting from position i going forward"** → recurse *forward* to `dp(i+1)`

Grid minimum path sum is the clearest example — `dp(0,0)` calls `dp(1,0)` and `dp(0,1)`, indices increase, base case is at the end:

```python
@lru_cache(maxsize=None)
def dp(i, j):                          # "min cost from (i,j) to end"
    if i == m-1 and j == n-1:
        return grid[i][j]              # base case is at the END
    if i == m-1: return grid[i][j] + dp(i, j+1)
    if j == n-1: return grid[i][j] + dp(i+1, j)
    return grid[i][j] + min(dp(i+1, j), dp(i, j+1))

return dp(0, 0)                        # starts at (0,0), recurses toward (m-1,n-1)
```

Both directions break a *large* problem into *smaller* ones — "size" just means different things:

| Frame | "Size" of problem | Recurse toward | Base case |
|---|---|---|---|
| "cost to reach i" | distance from start | 0 (n → 0) | `dp(0)` = given |
| "cost from i to end" | distance to end | end (0 → n) | `dp(end)` = given |

Use whichever framing feels more natural. Most 1D problems fit the "to reach i" frame (recurse backward). Grid and path problems often fit the "from i to end" frame (recurse forward). Both memoize equally well.

---

## Two Implementations

### Top-down (memoisation)
Write the natural recursion, cache results as they're computed.

```python
from functools import lru_cache

def fib(n):
    @lru_cache(maxsize=None)
    def dp(i):
        if i <= 1:
            return i
        return dp(i - 1) + dp(i - 2)
    return dp(n)
```

Intuitive — mirrors the recurrence directly. Downside: recursive call stack overhead; Python hits recursion limits on large inputs.

### Bottom-up (tabulation)
Fill a table iteratively in dependency order — no recursion.

```python
def fib(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]
```

Usually faster in practice — no function call overhead, better cache locality.

---

## Cache Locality and DP

Bottom-up DP fills a contiguous array sequentially. Modern CPUs load memory in cache lines (~64 bytes), so reading `dp[i-1]` when computing `dp[i]` almost always hits L1 cache — the value is already loaded. This is **spatial locality**.

Top-down memoisation stores results in a hash map (`lru_cache` uses a dict internally). Dict lookups scatter memory access and add pointer-chasing overhead, defeating prefetching.

```
Bottom-up 1D:   dp[0] dp[1] dp[2] dp[3] ...   ← sequential, cache-friendly
Top-down dict:  {0: v0, 2: v2, 1: v1, ...}     ← scattered heap allocations
```

For 2D DP this matters more. Row-major traversal (iterate columns in the inner loop) keeps accesses within the same row contiguous:

```python
# cache-friendly: row by row
for i in range(m):
    for j in range(n):        # dp[i][j-1] is adjacent in memory
        dp[i][j] = ...

# cache-unfriendly: column by column
for j in range(n):
    for i in range(m):        # dp[i-1][j] is a full row away
        dp[i][j] = ...
```

In practice the difference is small for typical LC input sizes, but for large 2D tables (image DP, sequence alignment) it can be 2–5× wall-clock time.

---

## Space Optimisation

When `dp[i]` only depends on a fixed number of previous states, you can discard the full table and keep rolling variables.

```python
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

This is the DP → greedy collapse: when only one state matters, the "table" reduces to a single variable. Kadane's algorithm (max subarray) is the canonical example.

---

## Identifying DP Problems

Ask: *"does the optimal solution to a larger input use the optimal solution to a smaller input of the same shape?"*

Common signals:
- "Maximum / minimum" over all ways to do something
- "Count the number of ways"
- "Can you achieve X?" (boolean feasibility)
- Choices at each step that affect what's available later (if independent → consider greedy first)

---

## Worked Examples

### Easy — Climbing Stairs (LC 70)

> n stairs, each move can climb 1 or 2 steps. How many distinct ways to reach the top?

**Insight**: to reach stair `n` you came from `n-1` (took 1 step) or `n-2` (took 2 steps). The number of ways to reach `n` is the sum of ways to reach each of those. This is Fibonacci with shifted base cases.

```
Recurrence:  dp[n] = dp[n-1] + dp[n-2]
Base cases:  dp[1] = 1,  dp[2] = 2

n=4 trace:
  dp[1]=1  dp[2]=2  dp[3]=3  dp[4]=5
```

```python
def climbStairs(n: int) -> int:
    if n <= 2:
        return n
    a, b = 1, 2           # a=dp[1]=1, b=dp[2]=2 (b already at step 2)
    for _ in range(n - 2):  # n-2 more advances to reach dp[n]
        a, b = b, a + b
    return b
```

Time O(N), space O(1) — only the previous two values are needed so the table collapses to two variables. `range(n-2)` because `b` starts pre-loaded at step 2 and needs `n-2` more steps to reach step `n`.

---

### Easy — Min Cost Climbing Stairs (LC 746)

> `cost[i]` is the cost paid when leaving step `i`. You can start at index 0 or 1. Reach past the last index with minimum cost.

**Insight**: the cheapest way to reach step `i` is the cheapest way to reach step `i-1` or `i-2`, plus the cost of that step.

```
Recurrence:  dp[i] = cost[i] + min(dp[i-1], dp[i-2])
Answer:      min(dp[-1], dp[-2])   ← can step off from either of the last two

cost = [10, 15, 20]
  i=2: cost[2] += min(cost[1], cost[0]) = min(15,10) = 10  → cost[2]=30
  answer: min(cost[-1], cost[-2]) = min(30, 15) = 15
```

```python
def minCostClimbingStairs(cost: list[int]) -> int:
    for i in range(2, len(cost)):   # base cases cost[0], cost[1] are the input itself
        cost[i] += min(cost[i - 1], cost[i - 2])
    return min(cost[-1], cost[-2])  # step off from either of the last two
```

Mutates `cost` in-place — use a copy if that matters. Time O(N), space O(1). Loop stops at `len(cost)-1` (not `len(cost)`) because we return `min` of the last two entries — there is no virtual top-floor index in this in-place formulation (contrast with the explicit table version which allocates `dp[len(cost)]` as the target).

**Difference from Climbing Stairs**: we now carry a *cost* at each step rather than counting paths, and the base cases are given by the input array, not hardcoded constants.

---

### Medium — House Robber (LC 198)

> Each house has a value. You cannot rob two adjacent houses. Maximise total loot.

**Insight**: at each house you make a binary choice — rob it (take `dp[i-2] + nums[i]`, skipping the previous) or skip it (carry `dp[i-1]`).

```
Recurrence:  dp[i] = max(dp[i-1], dp[i-2] + nums[i])

nums = [2, 7, 9, 3, 1]
  i=0: prev2=0, prev1=2
  i=1: max(2, 0+7)=7       prev2=2,  prev1=7
  i=2: max(7, 2+9)=11      prev2=7,  prev1=11
  i=3: max(11, 7+3)=11     prev2=11, prev1=11
  i=4: max(11, 11+1)=12    answer=12  (rob houses 0,2,4)
```

```python
def rob(nums: list[int]) -> int:
    prev2 = prev1 = 0
    for n in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + n)
    return prev1
```

Time O(N), space O(1). The adjacency constraint is the *only* difference from a plain max-sum scan — one extra state (`prev2`) captures it entirely.

---

## Classic Patterns

### 1D DP — Kadane's (Max Subarray)

```python
def max_subarray(nums):
    best = cur = nums[0]
    for n in nums[1:]:
        cur = max(n, cur + n)   # extend or restart
        best = max(best, cur)
    return best
```

Recurrence: `dp[i] = max(nums[i], dp[i-1] + nums[i])`

---

### 1D DP — Coin Change (Min Coins)

```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

Recurrence: `dp[a] = min(dp[a - c] + 1)` for each coin `c ≤ a`

---

### 2D DP — Longest Common Subsequence

```python
def lcs(s, t):
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
```

Recurrence:
- Match: `dp[i][j] = dp[i-1][j-1] + 1`
- No match: `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`

---

### 2D DP — 0/1 Knapsack

```python
def knapsack(capacity, weights, values):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]  # skip item i
            if weights[i - 1] <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - weights[i - 1]] + values[i - 1])
    return dp[n][capacity]
```

Recurrence: `dp[i][w] = max(skip item i, take item i)`

---

## Complexity

| Dimension | Time | Space | Space-optimised |
|---|---|---|---|
| 1D, window 1 | O(N) | O(N) | O(1) |
| 1D, window k | O(N) | O(N) | O(k) |
| 2D | O(M·N) | O(M·N) | O(min(M,N)) — keep one row |

---

## DP vs Backtracking

DP is most applicable when the return value is a **scalar** — count, min, max, or boolean feasibility. The same state always produces the same number, so caching is valid and saves real work.

Backtracking is the right tool when the return value is the **collection of results itself**. The output depends on the mutable path accumulated so far, making the full path part of the state — which is unique for every call, giving zero cache hits.

The word **"count"** is almost always the signal to reach for DP over backtracking:

| Problem | Approach | Complexity |
|---|---|---|
| List all subsets | Backtracking | O(N·2^N) |
| Count subsets summing to K | DP `dp[i][remaining]` | O(N·K) |
| List all permutations | Backtracking | O(N·N!) |
| Count distinct permutations | Bitmask DP `dp[mask]` | O(N·2^N) |
| List all paths in grid | Backtracking | O(2^(M+N)) |
| Count paths in grid | DP `dp[i][j]` | O(M·N) |

If the problem asks *"how many ways..."* → DP. If it asks *"list all ways..."* → backtracking.

---

## DP vs Greedy

Greedy is a special case of DP where the greedy choice property holds — the locally optimal choice is always globally safe, so the DP table collapses to a running variable. When choices interact (one decision changes what future decisions are worth), greedy breaks and DP is required.

See [greedy.md](greedy.md) for proofs of greedy correctness, and [greedy-vs-dp.md](greedy-vs-dp.md) for a detailed comparison including 1D vs 2D DP and the greedy collapse.
