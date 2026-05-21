# Greedy vs DP

## The Core Distinction

Both greedy and DP make a sequence of decisions to build an optimal solution. The difference is whether the locally best decision is always globally safe.

| | Greedy | DP |
|---|---|---|
| Decision at each step | Take the local optimum | Evaluate all options |
| Revisit past decisions? | Never | No, but explores all branches |
| Subproblems after a choice | Equivalent value regardless of choice | Different values depending on choice made |
| Choice interaction | Independent | Coupled |
| Table needed? | No — rolling variable suffices | Yes (unless greedy collapse applies) |

**The key question:** does picking the locally best option now *foreclose* a better global outcome?

- If **no** → greedy choice property holds → greedy works
- If **yes** → choices interact → need DP

---

## Why Greedy Fails When Choices Interact

```
Coin change: coins = [1, 3, 4], amount = 6

Greedy picks 4 (largest ≤ 6) → remainder 2 → only 1s fit → 4+1+1 = 3 coins
DP tries all:
  6-4=2 → dp[2]=2  → 3 coins
  6-3=3 → dp[3]=1  → 2 coins  ← optimal
  6-1=5 → dp[5]=2  → 3 coins
```

Picking `4` *looked* best locally but locked you into a hard remainder. The subproblems left behind each choice (remainder 2 vs 3 vs 5) have **different difficulties** — you can't know which coin was right without solving all the remainders. That's exactly what DP does.

In contrast, interval scheduling (greedy) works because picking the earliest-ending interval leaves *the maximum possible remaining time* regardless of which specific interval you chose — the subproblems are equivalent in value.

---

## The Greedy Collapse: When 1D DP Becomes Greedy

Some DP problems have the greedy choice property — the DP table reduces to a single rolling variable. This is the greedy collapse.

**Kadane's algorithm (max subarray):**

```python
# Full DP recurrence
dp[i] = max(nums[i], dp[i-1] + nums[i])

# Greedy collapse — dp[i] only depends on dp[i-1], single variable suffices
cur = max(n, cur + n)
```

Why it collapses: once `cur < 0`, extending it *always* makes the next number worse — there's no future scenario where dragging a negative subarray pays off. The local decision (reset vs extend) is always globally safe. No branching needed.

**The collapse is possible when:**
- `dp[i]` depends only on `dp[i-1]` (1D, window of 1)
- The local choice is provably always part of the global optimum (greedy choice property)

**It does NOT collapse when:**
- `dp[i]` depends on multiple prior states (`dp[i-3]`, `dp[j]` for all `j < i`)
- Different choices lead to subproblems of different value

---

## 1D DP vs 2D DP

The dimensionality of the DP table reflects how many independent axes of state the problem has.

### 1D DP
One changing variable — typically position in an array or a target value.

```
dp[i] = best answer considering the first i elements (or reaching value i)
```

Examples: max subarray, coin change, climbing stairs, house robber.

```python
# House Robber — dp[i] = max money robbing houses 0..i
dp[i] = max(dp[i-1], dp[i-2] + nums[i])
#            skip i    rob i (can't rob i-1)
```

### 2D DP
Two changing variables — typically two sequences, or items + capacity.

```
dp[i][j] = best answer considering first i of one input and first j of another
```

Examples: LCS, edit distance, 0/1 knapsack, unique paths.

```python
# LCS — dp[i][j] = length of LCS of s[:i] and t[:j]
if s[i-1] == t[j-1]:
    dp[i][j] = dp[i-1][j-1] + 1
else:
    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
```

2D DP cannot collapse to greedy — there are two independent dimensions of state that both matter, so no single local rule can replace evaluating all options.

---

## Decision Tree

```
Can you prove the greedy choice property?
(local optimum is always part of global optimum)
        │
       Yes → Greedy — O(N) or O(N log N)
        │
        No
        │
Does dp[i] depend only on dp[i-1]?
        │
       Yes → 1D DP — check if greedy collapse applies
        │
        No
        │
Does dp[i] depend on a fixed prior window?
        │
       Yes → 1D DP O(N), O(k) space
        │
        No — two input sequences, or items + capacity
        │
       Yes → 2D DP — O(M·N) time, O(min(M,N)) space with row compression
```

---

## Summary Table

| Problem | Type | Why |
|---|---|---|
| Max subarray (Kadane's) | 1D DP / greedy collapse | Local reset decision always safe |
| Coin change | 1D DP | Different coins leave different remainders |
| House robber | 1D DP | Skip/rob decision depends on dp[i-2] |
| Interval scheduling | Greedy | Earliest-end always part of optimal solution |
| Fractional knapsack | Greedy | Items divisible — best ratio always safe |
| 0/1 Knapsack | 2D DP | Item inclusion affects remaining capacity |
| LCS / Edit distance | 2D DP | Two sequences, both axes matter |
| Coin change (count ways) | 1D DP | Same structure as min-coins variant |
