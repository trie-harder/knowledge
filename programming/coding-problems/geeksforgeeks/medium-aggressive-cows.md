# Aggressive Cows (GFG) — Medium

> Given stall positions and `k` cows, place the cows such that the **minimum distance between any two cows is maximized**.

---

## Key Insight — Binary Search on the Answer

Instead of searching over placements, binary search over the **answer itself** (the minimum distance `d`).

For a fixed `d`, the feasibility question becomes simple:
> "Can we place k cows such that every consecutive pair is at least `d` apart?"

This is greedily checkable — place the first cow at `stalls[0]`, then always place the next cow at the earliest stall that is `>= d` away from the last placed cow.

If feasible for `d`, try larger. If not, try smaller.

```
search space: [1 ............ stalls[-1] - stalls[0]]
               ↑                                    ↑
             min possible                       max possible
             (adjacent stalls)               (only 2 cows, ends)

[feasible | feasible | feasible | NOT | NOT | NOT]
                              ↑
                         want this boundary → largest feasible d
```

---

## Algorithm

1. Sort stalls
2. Binary search on `d` in `[1, stalls[-1] - stalls[0]]`
3. For each candidate `d`, greedily check if k cows can be placed

### Feasibility check (greedy)

```
Place cow at stalls[0]. For each subsequent stall, place a cow there
if it is >= d away from the last placed cow. Count total cows placed.
```

Greedy works because placing a cow as early as possible never hurts — it leaves the most room for future cows.

---

## Trace for `stalls=[1,2,4,8,9], k=3`

```
sorted: [1, 2, 4, 8, 9],  lo=1, hi=8

mid=4:  place at 1, next >= 5 → 8, next >= 12 → none.  count=2 < 3 → False  hi=3
mid=2:  place at 1, next >= 3 → 4, next >= 6 → 8.      count=3 >= 3 → True  result=2, lo=3
mid=3:  place at 1, next >= 4 → 4, next >= 7 → 8.      count=3 >= 3 → True  result=3, lo=4

lo=4 > hi=3 → done.  Answer: 3  ✓
```

---

## Implementation

```python
def aggressiveCows(stalls: list[int], k: int) -> int:
    stalls.sort()
    n = len(stalls)

    def can_place(min_dist: int) -> bool:
        # Greedily place cows: always use the earliest valid stall
        count, last = 1, stalls[0]
        for i in range(1, n):
            if stalls[i] - last >= min_dist:
                count += 1
                last = stalls[i]
                if count == k:
                    return True
        return count >= k

    lo, hi = 1, stalls[-1] - stalls[0]
    result = 1

    while lo <= hi:
        mid = (lo + hi) // 2
        if can_place(mid):
            result = mid    # mid is feasible — record it and try larger
            lo = mid + 1
        else:
            hi = mid - 1   # mid too large — try smaller

    return result
```

**Time** O(N log N) — sort + O(log(max_dist)) × O(N) feasibility checks  
**Space** O(1)

---

## Pattern — "Binary Search on the Answer"

Use this pattern when:
- You're asked to **maximise the minimum** or **minimise the maximum** of something
- Direct search over arrangements is too slow
- But given a candidate answer, you can **check feasibility in O(N)**

The search space is the range of possible answer values (not indices). The feasibility check is usually greedy.

Other problems with this pattern: Koko Eating Bananas, Split Array Largest Sum, Minimum Days to Make Bouquets.
