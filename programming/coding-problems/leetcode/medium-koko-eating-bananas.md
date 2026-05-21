# Koko Eating Bananas (LC 875) — Medium

> Given piles of bananas and `h` hours, find the minimum eating speed `k` such that all piles can be finished in time.  
> At speed `k`: each pile takes `ceil(pile / k)` hours. Koko eats one pile at a time.

---

## Key Insight — Binary Search on the Answer

Same pattern as Aggressive Cows: binary search over the **answer** (speed `k`) rather than over arrangements.

For a given speed `k`, feasibility is checkable in O(N):

```
total_hours(k) = sum(ceil(pile / k) for pile in piles) <= h?
```

If feasible → try a smaller `k`. If not → need a larger `k`.

```
search space: [1 .............. max(piles)]
               ↑                     ↑
          slowest (1 banana/hr)   fastest (whole pile in 1 hr — never need faster)

[NOT | NOT | feasible | feasible | feasible | feasible]
              ↑
         want this boundary → smallest feasible k
```

---

## Trace for `piles=[3,6,7,11], h=8`

```
lo=1, hi=11

mid=6:  ceil(3/6)+ceil(6/6)+ceil(7/6)+ceil(11/6) = 1+1+2+2 = 6 ≤ 8  → feasible, result=6, hi=5
mid=3:  ceil(3/3)+ceil(6/3)+ceil(7/3)+ceil(11/3) = 1+2+3+4 = 10 > 8  → too slow, lo=4
mid=4:  ceil(3/4)+ceil(6/4)+ceil(7/4)+ceil(11/4) = 1+2+2+3 = 8 ≤ 8  → feasible, result=4, hi=3

lo=4 > hi=3 → done.  Answer: 4  ✓
```

---

## Implementation

```python
import math

def minEatingSpeed(piles: list[int], h: int) -> int:

    def can_finish(k: int) -> bool:
        # Check if speed k allows finishing all piles within h hours
        return sum(math.ceil(pile / k) for pile in piles) <= h

    lo, hi = 1, max(piles)   # never need k > max(piles): each pile ≤ 1 hour already
    result = hi

    while lo <= hi:
        mid = (lo + hi) // 2
        if can_finish(mid):
            result = mid     # feasible — record and try smaller
            hi = mid - 1
        else:
            lo = mid + 1     # too slow — need larger k

    return result
```

**Time** O(N log M) — log M binary search steps × O(N) feasibility check (M = max pile size)  
**Space** O(1)

### Integer ceiling without `math.ceil`

```python
math.ceil(pile / k)  ==  (pile + k - 1) // k
```

---

## Pattern — "Binary Search on the Answer"

Use when:
- Asked to **minimise the maximum** or **maximise the minimum**
- Direct search over all configurations is too slow
- Given a candidate answer, feasibility is checkable in O(N)

The boundary structure is always:

```
[infeasible ... infeasible | feasible ... feasible]   (minimise: find left boundary)
[feasible ... feasible | infeasible ... infeasible]   (maximise: find right boundary)
```

*See also: [../geeksforgeeks/medium-aggressive-cows.md](../geeksforgeeks/medium-aggressive-cows.md) — same pattern, maximise minimum distance*
