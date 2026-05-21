# Maximum Alternating Subsequence Sum (LC 1911) — Medium

> Return the maximum alternating sum of any subsequence of `nums`.  
> Alternating sum = `a[0] - a[1] + a[2] - a[3] + ...` (subsequence indexed from 0).

---

## Key Insight

At any point during the scan, you're in one of two states:

- **even state**: you've selected an even number of elements so far → next pick gets a `+` sign
- **odd state**: you've selected an odd number of elements so far → next pick gets a `-` sign

For each element you make one of two choices: **skip** (stay in same state) or **pick** (transition to the other state).

---

## Subproblem

```
dp_even(i) = max alternating sum considering nums[0..i], having selected an even count of elements
dp_odd(i)  = max alternating sum considering nums[0..i], having selected an odd count of elements
```

### Recurrence

```
dp_even(i) = max(dp_even(i-1),  dp_odd(i-1)  - nums[i])   # skip  OR  pick at odd pos (- sign)
dp_odd(i)  = max(dp_odd(i-1),   dp_even(i-1) + nums[i])   # skip  OR  pick at even pos (+ sign)
```

**Why the transitions cross (odd→even subtracts, even→odd adds):**

The sign of `nums[i]` is set by its **position in the subsequence**, not by whether the total count ends up even or odd:

```
Came from dp_even(i-1) → even elements before → nums[i] is at an even position → + sign → goes into dp_odd
Came from dp_odd(i-1)  → odd elements before  → nums[i] is at an odd position  → - sign → goes into dp_even
```

So picking always transitions between states, and the state you're *leaving* determines the sign of the element you just picked.

### Base cases

```
dp_even(-1) = 0      # empty subsequence — 0 elements selected, 0 is even
dp_odd(-1)  = -inf   # impossible to have selected an odd count before any element
```

### Answer

`dp_odd(n-1)` — both states only depend on index `i-1`, so this collapses to two rolling variables.

---

## Trace for `[4, 2, 5, 3]`

```
start:  even=0,  odd=-inf

num=4:  new_even = max(0,  -inf-4) = 0    new_odd = max(-inf, 0+4) = 4
        even=0,  odd=4       → picked 4 as first element: [4]

num=2:  new_even = max(0,  4-2)   = 2     new_odd = max(4,    0+2) = 4
        even=2,  odd=4       → even: extended [4] with -2 → [4,2]; odd: still just [4]

num=5:  new_even = max(2,  4-5)   = 2     new_odd = max(4,    2+5) = 7
        even=2,  odd=7       → odd: extended [4,2] with +5 → [4,2,5] = 4-2+5 = 7 ✓

num=3:  new_even = max(2,  7-3)   = 4     new_odd = max(7,    2+3) = 7
        even=4,  odd=7       → odd unchanged: [4,2,5] still best

Answer: odd = 7
```

---

## Implementation

### Uncollapsed — full arrays

```python
def maxAlternatingSum(nums: list[int]) -> int:
    n = len(nums)
    # dp_even[i] = best sum considering nums[0..i] with even count selected
    # dp_odd[i]  = best sum considering nums[0..i] with odd count selected
    dp_even = [0] * n
    dp_odd  = [0] * n

    # Base: before i=0 → even=0, odd=-inf
    # i=0: either skip (even stays 0) or pick at even pos (odd = nums[0])
    dp_even[0] = 0
    dp_odd[0]  = nums[0]

    for i in range(1, n):
        # odd→even: came from odd count → nums[i] at odd position → - sign
        dp_even[i] = max(dp_even[i-1], dp_odd[i-1] - nums[i])
        # even→odd: came from even count → nums[i] at even position → + sign
        dp_odd[i]  = max(dp_odd[i-1],  dp_even[i-1] + nums[i])

    # dp_odd ends with a + element (odd count → last pick at even pos → + sign)
    # dp_even ends with a - element (or 0 elements) — always ≤ dp_odd for positive nums
    # so dp_odd[n-1] is always the global maximum
    return dp_odd[n - 1]
```

**Time** O(N) — single pass  
**Space** O(N) — two arrays

### Collapsed — rolling variables

```python
def maxAlternatingSum(nums: list[int]) -> int:
    # even = best sum having selected an even count of elements (next pick = + sign)
    # odd  = best sum having selected an odd count of elements  (next pick = - sign)
    even, odd = 0, 0
    # Note: odd starts at 0 (not -inf) because Python's max handles it naturally —
    # we never subtract from -inf, and the first num will always prefer even+num over odd.
    # In practice, initialising both to 0 is safe: odd can only grow via even+num.

    for num in nums:
        # odd→even: odd elements before → num at odd position → - sign
        # even→odd: even elements before → num at even position → + sign
        # Tuple assignment computes both from the old values before either is overwritten
        even, odd = max(even, odd - num), max(odd, even + num)

    return odd
```

**Time** O(N) — single pass  
**Space** O(1) — two rolling variables

---

## Why this collapses to rolling variables

`even` and `odd` each depend only on the **previous** `even` and `odd` — a fixed 2-state window. Both are updated simultaneously from the prior values (note the tuple assignment), so no temporary variable is needed.

---

## Connection to other problems

This is a **state machine DP** — the same pattern as:
- **Best Time to Buy and Sell Stock** (holding / not-holding states)
- **House Robber** (robbed / not-robbed states)

The state encodes "where you are" in the alternating pattern; the transition encodes "skip or pick".
