# Greedy Algorithms

## What is a Greedy Algorithm?

A greedy algorithm makes the **locally best choice at each step** without looking back or reconsidering past decisions.

At every step you ask: *"what's the best option available right now?"* and take it — no simulation of future consequences, no backtracking.

The opposite approach is dynamic programming or brute-force, which considers all possible sequences of choices and picks the globally best one.

---

## When Greedy Works

Greedy is correct when two conditions hold:

**1. Greedy choice property**
The locally optimal choice is always part of some globally optimal solution. Making the greedy choice never rules out achieving the best overall answer.

**2. Optimal substructure**
The problem can be broken into subproblems, and the optimal solution to the whole is composed of optimal solutions to the subproblems.

If either condition fails, greedy will produce a wrong answer.

---

## Proving Greedy Correctness

There are two standard arguments:

### Exchange Argument (most common)
> *If I swap the greedy choice for any alternative, I do no better — and possibly worse.*

You assume some optimal solution exists that makes a different choice at some step, then show you can "exchange" that choice for the greedy one without decreasing the total value. Since swapping never hurts, the greedy solution must also be optimal.

### Greedy Stays Ahead
> *At every step, the greedy solution is at least as good as any other solution so far.*

You prove by induction that after each step, greedy has accumulated at least as much value as any competing strategy. When you reach the end, greedy is still ahead — so it must be optimal.

---

## When Greedy Fails

Greedy fails when a locally good choice **closes off** a better global path.

**Example — Coin change with `[1, 3, 4]`, target = 6:**

```
Greedy: take 4 (largest ≤ 6), then two 1s → 3 coins
Optimal: two 3s                            → 2 coins
```

The greedy choice of `4` felt best locally but blocked the better solution. This is why coin change (with arbitrary denominations) requires DP, not greedy.

**The key question when evaluating greedy:** does making the locally best choice now *prevent* a better outcome later? If yes, greedy is wrong.

---

## Classic Examples

### Best Time to Buy and Sell Stock II
*Capture every upward price movement.*

```python
def max_profit(prices):
    profit = 0
    for i in range(1, len(prices)):
        profit += max(0, prices[i] - prices[i - 1])
    return profit
```

**Why greedy works:** Any multi-day profit decomposes into consecutive daily steps with the same total:

```
buy day 1, sell day 4:  prices[4] - prices[1]
  == (prices[2]-prices[1]) + (prices[3]-prices[2]) + (prices[4]-prices[3])
```

So capturing every positive daily step is equivalent to every possible buy/sell combination — but negative steps can be skipped for free (sell before a drop, rebuy after). Choices are **independent**: taking a gain today never prevents a gain tomorrow.

---

### Activity Selection / Interval Scheduling
*Schedule the maximum number of non-overlapping intervals.*

```python
def max_activities(intervals):
    intervals.sort(key=lambda x: x[1])  # sort by end time
    count, last_end = 0, float('-inf')
    for start, end in intervals:
        if start >= last_end:
            count += 1
            last_end = end
    return count
```

**Why greedy works:** Always picking the interval that ends earliest leaves the maximum remaining time for future intervals. Exchange argument: any solution that picks a later-ending interval can swap it for the earlier-ending one without losing any subsequent selections.

---

### Fractional Knapsack
*Maximise value in a knapsack — items can be split.*

```python
def fractional_knapsack(capacity, items):
    # items = [(weight, value), ...]
    items.sort(key=lambda x: x[1] / x[0], reverse=True)  # sort by value/weight
    total = 0.0
    for weight, value in items:
        if capacity <= 0:
            break
        take = min(weight, capacity)
        total += take * (value / weight)
        capacity -= take
    return total
```

**Why greedy works:** Taking the highest value-per-unit-weight first is always optimal when items are divisible. The exchange argument: swapping any portion of a lower-density item for a higher-density item never decreases total value.

**Note:** The 0/1 Knapsack (no splitting) breaks greedy — requires DP.

---

### Huffman Encoding
*Build an optimal prefix-free binary encoding.*

Always merge the two lowest-frequency nodes first. The resulting tree minimises the total encoded bit length.

**Why greedy works:** Lower-frequency characters end up deeper in the tree (longer codes), higher-frequency characters end up shallower. This is provably optimal via exchange argument — swapping any two nodes of different depths and frequencies to follow this rule never increases total cost.

---

## Summary

| Problem | Greedy Strategy | Works? |
|---|---|---|
| Stock trading (unlimited trades) | Capture every positive daily diff | Yes |
| Interval scheduling | Pick earliest end time | Yes |
| Fractional knapsack | Highest value/weight ratio first | Yes |
| Huffman encoding | Merge two lowest-frequency nodes | Yes |
| Coin change (arbitrary denominations) | Pick largest coin ≤ remaining | No — use DP |
| 0/1 Knapsack | Highest value/weight first | No — use DP |
| Shortest path (negative edges) | Dijkstra (greedy) | No — use Bellman-Ford |

**Rule of thumb:** if choices are independent (one choice doesn't block or affect the value of another), greedy is likely correct. If choices interact — one decision changes what future decisions are worth — reach for DP.
