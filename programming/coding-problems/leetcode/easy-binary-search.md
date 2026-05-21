# Binary Search (LC 704) — Easy

> Given a sorted array `nums` and a `target`, return its index or `-1` if not found.

---

## Key Insight

At each step, compare the middle element to the target and eliminate half the search space. Requires a **sorted** array — each comparison gives a definitive "go left" or "go right".

```
nums = [-1, 0, 3, 5, 9, 12],  target = 9

lo=0, hi=5, mid=2: nums[2]=3 < 9  → lo=3
lo=3, hi=5, mid=4: nums[4]=9 == 9 → return 4  ✓
```

---

## Template — Exact Search

```python
def search(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1

    while lo <= hi:            # lo==hi is still a valid 1-element range to check
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1       # target is to the right
        else:
            hi = mid - 1       # target is to the left

    return -1                  # lo > hi: search space exhausted
```

**Time** O(log N)  **Space** O(1)

---

## Template — Lower Bound (leftmost valid position)

Find the smallest index where `nums[i] >= target` (or where target would be inserted).  
Used when there may be duplicates or you want the first occurrence.

```python
def lower_bound(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums)     # hi = len(nums): answer may be past the end

    while lo < hi:            # loop ends when lo == hi (single candidate)
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1      # mid is too small, exclude it
        else:
            hi = mid          # mid could be the answer, keep it

    return lo                 # lo == hi: the leftmost valid position
```

> `bisect.bisect_left(nums, target)` does this in Python's standard library.

---

## Template — Upper Bound (first element strictly greater)

Find the smallest index where `nums[i] > target`.

```python
def upper_bound(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums)

    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] <= target:
            lo = mid + 1
        else:
            hi = mid

    return lo
```

> `bisect.bisect_right(nums, target)` does this in Python's standard library.

---

## Choosing the right template

| Goal | Template | Loop condition | `hi` init |
|---|---|---|---|
| Exact match | `==` check | `lo <= hi` | `len-1` |
| First `>= target` | lower bound | `lo < hi` | `len` |
| First `> target` | upper bound | `lo < hi` | `len` |
| Binary search on answer | lower bound variant | `lo < hi` | answer range max |

---

## Common pitfalls

- **`mid = (lo + hi) // 2`** — safe in Python (arbitrary int), but use `lo + (hi - lo) // 2` in languages with overflow (C, Java)
- **Off-by-one on `hi`**: exact search uses `hi = len-1` (valid indices only); bound searches use `hi = len` (answer can be past the end)
- **Infinite loop**: in lower/upper bound, if you set `hi = mid` you need `lo < hi` (not `<=`) to avoid `mid == hi` never shrinking
