
# Backtracking

Backtracking is a recursive technique that builds a solution incrementally, abandoning ("pruning") a branch as soon as it's determined it can't lead to a valid answer.

The general shape:
```python
def backtrack(state):
    if is_solution(state):
        results.append(copy(state))
        return
    for choice in choices(state):
        apply(choice, state)
        backtrack(state)
        undo(choice, state)     # ← the "backtrack" step
```

---

## Two Approaches: Subsets as a Case Study

Generating all subsets of `[1, 2, 3]` illustrates the two main recursive patterns.

### Approach 1 — Take / No-Take (Binary Decision Tree)

At each index, make exactly two choices: include the element or skip it.
Results are collected only at the **leaves** (when all positions have been decided).

```python
def subsets(nums):
    def solve(start, current):
        if start == len(nums):
            results.append(current[:])   # only record at leaves
            return
        current.append(nums[start])
        solve(start + 1, current)        # take
        current.pop()
        solve(start + 1, current)        # skip

    results = []
    solve(0, [])
    return results
```

### Approach 2 — Backtracking with For Loop (Combination Tree)

Record the current subset immediately at every call, then branch into each remaining element.

```python
def subsets(nums):
    def backtrack(start, current):
        results.append(current[:])       # record at every node

        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()

    results = []
    backtrack(0, [])
    return results
```

---

## Recursive Tree Comparison (N=3)

```
APPROACH 1 (take/no-take)          APPROACH 2 (backtracking)
full binary tree, depth = N        combination tree, variable branching

         start=0                           []  ✓
        /        \                       / |  \
    take           skip             [1]✓ [2]✓ [3]✓
    /   \          /   \             / \     \
  s=1   s=1      s=1   s=1      [1,2]✓ [1,3]✓ [2,3]✓
  / \   / \      / \   / \        |
 s=2 s=2 s=2 s=2 ...          [1,2,3]✓

 ✓   ✓  ✓   ✓  ✓  ✓  ✓  ✓
 (results at leaves only)          (results at every node)
```

### Node count

| Depth | Approach 1 | Approach 2 | C(3,d) |
|-------|------------|------------|--------|
| 0     | 1          | 1          | 1      |
| 1     | 2          | 3          | 3      |
| 2     | 4          | 3          | 3      |
| 3     | 8          | 1          | 1      |
| **Total** | **15** | **8**  |        |
| Results   | 8      | 8      |        |
| Wasted    | 7      | 0      |        |

**Approach 1** is a full binary tree of depth N:
$$\text{total nodes} = 2^{N+1} - 1$$

Every path must reach depth N before recording — internal nodes are unavoidable overhead.

**Approach 2** is a combination tree:
$$\text{total nodes} = \sum_{d=0}^{N} \binom{N}{d} = 2^N$$

Records at every node, so each call corresponds to exactly one result — no wasted calls.

---

## Why Approach 2 Node Count is 2^N

**Combinatorial argument:** each node in the tree corresponds to exactly one unique subset, and there are exactly 2^N subsets of N elements — one per node.

**Algebraic proof via binomial theorem:** nodes at depth d = C(N,d) (choosing d elements from N):

$$\sum_{d=0}^{N} \binom{N}{d} = (1+1)^N = 2^N$$

---

## Time Complexity

Both are **O(N · 2^N)**:
- 2^N subsets generated
- Each `current[:]` copy costs O(N)

The 2x difference in call count (2^(N+1) vs 2^N) is a constant factor, absorbed into big-O.

In practice Approach 2 is faster — ~half the function calls, and Python function call overhead is significant. At N=20: ~1M vs ~2M calls.

---

## Which to Use

| | Approach 1 (take/no-take) | Approach 2 (backtracking) |
|---|---|---|
| Branching factor | Always 2 | Variable (N-d at depth d) |
| Results collected | Leaves only | Every node |
| Total calls | 2^(N+1) - 1 | 2^N |
| Wasted calls | ~2^N | 0 |
| Best for | 0/1 decisions (include/exclude) | Subsets, combinations, constrained search |
| Generalises to combinations (size K) | Awkward | Natural — add `if len(current) == k` |
| Generalises to pruning constraints | Possible | Natural — add condition in for loop |

**Prefer Approach 2** for most backtracking problems. The for-loop structure generalises cleanly to combinations, permutations, and problems with pruning conditions.

**Prefer Approach 1** when the problem is explicitly binary at each position — e.g. 0/1 knapsack, or problems where *every* element must be assigned one of two states.

---

## Pruning

The power of backtracking over brute force is pruning — skipping entire subtrees that can't yield valid solutions.

```python
def combination_sum(candidates, target):
    def backtrack(start, current, remaining):
        if remaining == 0:
            results.append(current[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:   # ← prune: no point going further
                break
            current.append(candidates[i])
            backtrack(i, current, remaining - candidates[i])
            current.pop()

    candidates.sort()                        # sort enables the pruning above
    results = []
    backtrack(0, [], target)
    return results
```

Without pruning this is O(N^(T/M)) where T=target, M=min candidate. Pruning cuts the tree dramatically in practice though worst-case is the same.

---

## When to Use Approach 1 Over Approach 2

Use approach 1 (take/no-take) when **every element must be assigned exactly one of two states** — there is no "skip" and no combinatorial selection, just a binary decision at each position.

**Target Sum (LC 494)** — assign `+` or `-` to every element to reach a target:

```python
def findTargetSumWays(nums, target):
    def solve(i, current_sum):
        if i == len(nums):
            return 1 if current_sum == target else 0

        # binary: assign + or assign -
        return solve(i + 1, current_sum + nums[i]) + \
               solve(i + 1, current_sum - nums[i])

    return solve(0, 0)
```

Every element is processed — there is no "start index" or "remaining elements to choose from." Forcing approach 2's for-loop here is awkward because you're not selecting a subset, you're assigning a state to all elements.

Other problems with the same binary-assignment structure:
- **Partition Equal Subset Sum** — each element goes to subset A or subset B
- **Letter Case Permutation** — each letter is uppercased or lowercased (digits are forced)
- **Generate all binary strings of length N** — each position is `0` or `1`

**Rule:** if every element must be assigned one of two states → approach 1. If you are choosing *which* elements to include → approach 2.
