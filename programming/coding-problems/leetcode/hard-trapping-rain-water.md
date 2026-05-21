# Trapping Rain Water (LC 42) — Hard

> Given `n` non-negative integers representing an elevation map, compute how much water it can trap after raining.

---

## Key Insight

The water above bar `i` is capped by the **shorter of the two surrounding walls**:

```
water[i] = max(0, min(left_max[i], right_max[i]) - height[i])
```

Water rises to the level of the shorter wall. If the bar itself is taller than that level, it holds nothing.

```
height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]

              █
      █   ██ █ █
  █  ████████████
  0  1  0  2  1  0  1  3  2  1  2  1

  at i=5: left_max=2, right_max=3 → min=2 → water = 2 - 0 = 2
  at i=2: left_max=1, right_max=3 → min=1 → water = 1 - 0 = 1
```

Total trapped = 6.

---

## Approach 1 — Precompute Left/Right Max Arrays

Build `left_max[i]` and `right_max[i]` explicitly, then sum up.

```python
def trap(height: list[int]) -> int:
    n = len(height)
    left_max  = [0] * n    # left_max[i]  = max height in height[0..i]
    right_max = [0] * n    # right_max[i] = max height in height[i..n-1]

    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i-1], height[i])

    right_max[-1] = height[-1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i+1], height[i])

    water = 0
    for i in range(n):
        water += max(0, min(left_max[i], right_max[i]) - height[i])
    return water
```

**Time** O(N) — three linear passes  
**Space** O(N) — two extra arrays

---

## Approach 2 — Two Pointers (preferred)

Avoid the extra arrays. Use `l` and `r` pointers moving inward, tracking `left_max` and `right_max` on the fly.

**Why it works:**

If `left_max <= right_max`, the water at `l` is definitely bounded by `left_max` — we already know the right side is at least as tall, so it won't be the limiting wall. We can safely compute water at `l` without knowing the exact right boundary. Same logic applies to `r` when `right_max < left_max`.

```
[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
 l                                  r

left_max=0, right_max=1 → left side is limiting → process l
left_max=1, right_max=1 → process l (tie goes to left)
...
```

```python
def trap(height: list[int]) -> int:
    l, r = 0, len(height) - 1
    left_max = right_max = 0
    water = 0

    while l <= r:
        if left_max <= right_max:
            # Left side is the limiting wall — safe to compute water at l
            # (right side is >= left_max, so it won't be the bottleneck)
            left_max = max(left_max, height[l])
            water += left_max - height[l]   # always >= 0 since left_max >= height[l]
            l += 1
        else:
            # Right side is the limiting wall — safe to compute water at r
            right_max = max(right_max, height[r])
            water += right_max - height[r]
            r -= 1

    return water
```

**Time** O(N) — single pass  
**Space** O(1)

---

## Why `left_max - height[l]` is never negative

We update `left_max = max(left_max, height[l])` **before** subtracting. So `left_max >= height[l]` always holds — no need for `max(0, ...)`.

---

## Comparison

| | Precompute Arrays | Two Pointers |
|---|---|---|
| Time | O(N) | O(N) |
| Space | O(N) | O(1) |
| Clarity | explicit, easy to trace | requires understanding the invariant |
| Preferred | learning / debugging | interviews / production |
