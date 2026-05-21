# Longest Increasing Subsequence (LC 300)

> Given an integer array `nums`, return the length of the longest strictly increasing subsequence.

---

## Key Insight

Define `dp[i]` as the length of the LIS that **ends at index `i`** (i.e., `nums[i]` is the last element chosen).

To extend to index `i`, look back at all `j < i` where `nums[j] < nums[i]` — any of those can be the predecessor. Take the best one.

---

## Approach 1 — O(N²) DP

### Define the subproblem

`dp[i]` = length of the longest increasing subsequence ending at `nums[i]`

### Recurrence

```
dp[i] = max(dp[j] + 1)   for all j < i where nums[j] < nums[i]
dp[i] = 1                if no such j exists  (nums[i] starts a new subsequence alone)
```

### Base cases

Every element alone is a valid subsequence of length 1: initialise `dp[i] = 1` for all `i`.  
No separate base case is needed — the recurrence naturally falls back to 1 when no valid `j` exists.

### Fill order

`dp[i]` only depends on `dp[j]` for `j < i` — strictly earlier indices.  
Fill **left to right**: when computing `dp[i]`, all `dp[j]` for `j < i` are already done.

### Full trace for `[10, 9, 2, 5, 3, 7, 101, 18]`

```
i=0: nums[0]=10,  no j < 0                                          → dp[0]=1  [10]
i=1: nums[1]=9,   10 > 9, no valid j                                → dp[1]=1  [9]
i=2: nums[2]=2,   9,10 > 2, no valid j                              → dp[2]=1  [2]
i=3: nums[3]=5,   j=2: 2<5 → dp[2]+1=2                             → dp[3]=2  [2,5]
i=4: nums[4]=3,   j=2: 2<3 → dp[2]+1=2                             → dp[4]=2  [2,3]
i=5: nums[5]=7,   j=2: 2<7→2, j=3: 5<7→3, j=4: 3<7→3              → dp[5]=3  [2,5,7]
i=6: nums[6]=101, all j valid; best is j=5: dp[5]+1=4               → dp[6]=4  [2,5,7,101]
i=7: nums[7]=18,  j=5: 7<18→4, j=6: 101>18 skip                    → dp[7]=4  [2,5,7,18]

dp = [1, 1, 1, 2, 2, 3, 4, 4]
Answer: max(dp) = 4
```

### Implementation

```python
def lengthOfLIS(nums: list[int]) -> int:
    n = len(nums)
    # dp[i] = length of LIS ending at index i
    # base: each element alone is a subsequence of length 1
    dp = [1] * n

    for i in range(1, n):
        # No rolling/collapsing possible: dp[i] can depend on ANY dp[j] where j < i
        # and nums[j] < nums[i]. The lookback is unbounded and value-conditional —
        # a future element may skip over large values and extend from dp[0].
        # Unlike House Robber (fixed 2-state window), the full array must be kept.
        for j in range(i):
            # nums[j] < nums[i]: nums[i] can extend the LIS that ends at j
            # dp[j] + 1: take that LIS and append nums[i]
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    # LIS can end anywhere — take the best
    return max(dp)
```

**Time** O(N²) — inner loop scans all j < i for each i  
**Space** O(N) — the dp array

---

## Approach 2 — O(N log N) Patience Sorting

Maintain a `tails` array where:

> `tails[k]` = the **smallest tail element** among all increasing subsequences of length `k+1` seen so far

For each `num`:
- If `num` > all tails → extend the longest subsequence (append)
- Otherwise → binary search for the leftmost `tails[pos] >= num` and replace it

Replacing with a smaller value keeps `tails` as small as possible, maximising future extension chances.

### Trace for `[10, 9, 2, 5, 3, 7, 101, 18]`

```
10  → tails = [10]              extend
9   → tails = [9]               replace 10 (pos=0, 9 < 10)
2   → tails = [2]               replace 9  (pos=0, 2 < 9)
5   → tails = [2, 5]            extend
3   → tails = [2, 3]            replace 5  (pos=1, 3 < 5)
7   → tails = [2, 3, 7]         extend
101 → tails = [2, 3, 7, 101]    extend
18  → tails = [2, 3, 7, 18]     replace 101 (pos=3, 18 < 101)

len(tails) = 4  ✓
```

> **Note:** `tails` is **not** the actual LIS. It's a synthetic structure tracking only the length.  
> The elements in `tails` may not form a valid increasing subsequence together (here they happen to, but that's coincidental).

### Implementation

```python
import bisect

def lengthOfLIS(nums: list[int]) -> int:
    tails = []

    for num in nums:
        # bisect_left: find leftmost pos where tails[pos] >= num
        # For strict increase we replace the first tail that is >= num
        # (not just >, because equal values don't extend a *strictly* increasing sequence)
        pos = bisect.bisect_left(tails, num)

        if pos == len(tails):
            tails.append(num)   # num larger than all tails — new longest subsequence
        else:
            tails[pos] = num    # replace: smaller tail = better odds for future elements

    # length of tails == length of LIS
    return len(tails)
```

**Time** O(N log N) — one binary search per element  
**Space** O(N) — tails array

---

## Comparison

| | O(N²) DP | O(N log N) Patience Sort |
|---|---|---|
| Time | O(N²) | O(N log N) |
| Space | O(N) | O(N) |
| Conceptual complexity | straightforward recurrence | non-obvious `tails` invariant |
| Reconstruct actual LIS | yes — trace back through `dp` | requires extra bookkeeping |
| Preferred when | N ≤ 2500, or clarity needed | N large, only length needed |

---

*See also: [dynamic-programming.md](dynamic-programming.md) — subproblem design and fill order*
