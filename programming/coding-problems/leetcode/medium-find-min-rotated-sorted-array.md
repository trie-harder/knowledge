# Find Minimum in Rotated Sorted Array (LC 153) — Medium

> A sorted array was rotated at some pivot. Find the minimum element. All values are unique.

---

## Key Insight

Rotation splits the array into two sorted segments. The minimum is the **inflection point** — the one element where the sorted order resets.

```
[3, 4, 5, 1, 2]
           ↑ minimum: where the right segment begins
```

Use binary search: compare `nums[mid]` to `nums[hi]` to determine which segment `mid` falls in:

- `nums[mid] > nums[hi]` → `mid` is in the **left (higher) segment**, minimum is to the right: `lo = mid + 1`
- `nums[mid] < nums[hi]` → `mid` is in the **right (lower) segment**, minimum is at `mid` or left: `hi = mid`

When `lo == hi`, both pointers have converged on the minimum.

---

## Why compare to `nums[hi]` not `nums[lo]`?

Think of the rotated array as a hill that got cut and rearranged:

```
Original: 1  2  3  4  5
Rotated:  3  4  5  1  2
         big big big small small
```

`nums[hi]` is always one of the **small** numbers on the right side. So:

- `nums[mid] > nums[hi]` → mid is on the **big side** — the minimum is further right → `lo = mid + 1`
- `nums[mid] < nums[hi]` → mid is already on the **small side** — the minimum is here or further left → `hi = mid`

Using `nums[lo]` doesn't work because `lo` starts on the big side too. If both `lo` and `mid` are in the big segment, `nums[mid] > nums[lo]` tells you nothing — you can't distinguish "mid is right of lo in the big segment" from "mid crossed the inflection". `nums[hi]` is a reliable anchor because it only ever moves left via `hi = mid`, always staying in the small segment.

---

## Trace

```
[3, 4, 5, 1, 2]   lo=0, hi=4

mid=2: nums[2]=5 > nums[4]=2  → in left segment, min is right  → lo=3
mid=3: nums[3]=1 < nums[4]=2  → in right segment, min is here or left → hi=3
lo=3 == hi=3 → return nums[3]=1  ✓

[4, 5, 6, 7, 0, 1, 2]   lo=0, hi=6

mid=3: nums[3]=7 > nums[6]=2  → lo=4
mid=5: nums[5]=1 < nums[6]=2  → hi=5
mid=4: nums[4]=0 < nums[5]=1  → hi=4
lo=4 == hi=4 → return nums[4]=0  ✓

[1, 2, 3] (no rotation)  lo=0, hi=2

mid=1: nums[1]=2 < nums[2]=3  → hi=1
mid=0: nums[0]=1 < nums[1]=2  → hi=0
lo=0 == hi=0 → return nums[0]=1  ✓
```

---

## Implementation

```python
def findMin(nums: list[int]) -> int:
    lo, hi = 0, len(nums) - 1

    while lo < hi:             # lo == hi: single candidate, done
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            # mid is in the higher left segment — minimum is strictly to the right
            # exclude mid itself: it's larger than nums[hi] so can't be the minimum
            lo = mid + 1
        else:
            # nums[mid] <= nums[hi]: mid is in the lower right segment
            # minimum is at mid or to its left — keep mid as a candidate
            # don't do hi = mid - 1: mid itself could be the minimum
            hi = mid

    # lo == hi: converged on the single minimum element
    return nums[lo]
```

**Time** O(log N)  **Space** O(1)

---

## Connection to binary search templates

This uses the **lower bound** loop structure (`lo < hi`, `hi = mid`) rather than the exact-search structure (`lo <= hi`, `hi = mid - 1`) — because we're converging on a boundary, not matching a value.

*See also: [easy-binary-search.md](easy-binary-search.md) — lower bound template*
