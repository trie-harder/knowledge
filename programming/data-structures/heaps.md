# Heaps

A **heap** is a complete binary tree stored as an array, satisfying the **heap property**:
- **Min-heap**: every parent ≤ its children → root is always the minimum.
- **Max-heap**: every parent ≥ its children → root is always the maximum.

```
Min-heap example:

         1          index: [1, 3, 2, 7, 5, 8, 4]
        / \
       3   2         parent(i) = (i-1)//2
      / \ / \        left(i)   = 2i+1
     7  5 8  4       right(i)  = 2i+2
```

No sorting between siblings — only the parent/child relationship is enforced. This is what makes heaps faster than a sorted array for priority-queue operations.

## Shape Guarantee

A heap is always a **complete binary tree** — every level fully filled except possibly the last, which fills left to right. This shape is not something `heapify` produces; it is a structural precondition encoded by the array itself. The index formulas (`left = 2i+1`, `right = 2i+2`) only make sense for a complete tree, so any array of length N implicitly represents one.

The heap property (parent ≤ children) is what `heapify` establishes. The shape is already fixed before any comparisons happen.

This guarantees height = ⌊log₂ N⌋ with no worst-case skew — unlike a BST where inserting sorted input gives O(N) height.

## Etymology

The name comes from an informal meaning of *heap* — a pile of things where you can always quickly grab the "best" one off the top, without caring about the internal order of the rest. It was coined by J.W.J. Williams in his 1964 paper introducing heapsort.

## Complexity

| Operation         | Time          | Space  | Notes                                         |
|-------------------|---------------|--------|-----------------------------------------------|
| **Build** (heapify) | **O(N)**    | O(1)   | Linear — sift-down from N/2 to 0; tighter than O(N log N) |
| **Push**          | O(log N)      | O(1)   | Append then sift-up                           |
| **Pop** (min/max) | O(log N)      | O(1)   | Swap root with last, shrink, sift-down        |
| **Peek** (min/max)| **O(1)**      | O(1)   | Root is always at index 0                     |
| **Delete arbitrary** | O(log N)  | O(1)   | Replace with last element, sift up or down    |
| **Merge two heaps** | O(N)        | O(N)   | Concat arrays then heapify (naïve)            |

Space for the heap itself is O(N).

## Why O(N) build, not O(N log N)?

The naive assumption: N nodes × O(log N) per sift-down = O(N log N). But most nodes are near the **bottom** of the tree and have very little work to do.

In a heap of N nodes, the number of nodes at each height h is at most ⌈N / 2^(h+1)⌉:

| Height | # nodes  | Sift-down cost | Work          |
|--------|----------|----------------|---------------|
| 0 (leaves) | ~N/2 | 0           | 0             |
| 1      | ~N/4     | 1              | N/4           |
| 2      | ~N/8     | 2              | N/4           |
| ...    | ...      | ...            | ...           |
| log N  | 1 (root) | log N          | log N         |

**Deriving the total from the table:**

Each row contributes `(nodes at height h) × (cost per node)`. Nodes at height h ≈ N / 2^(h+1), and sift-down cost is h:

$$\text{Total work} = \sum_{h=0}^{\lfloor \log N \rfloor} \frac{N}{2^{h+1}} \cdot h = \frac{N}{2} \sum_{h=0}^{\lfloor \log N \rfloor} \frac{h}{2^h}$$

Bounding by the infinite series (which only adds positive terms):

$$\leq \frac{N}{2} \sum_{h=0}^{\infty} \frac{h}{2^h}$$

That infinite sum evaluates to 2. To see why, start from the geometric series and differentiate:

$$\sum_{h=0}^{\infty} x^h = \frac{1}{1-x} \quad \xrightarrow{\text{d/dx, then} \times x} \quad \sum_{h=0}^{\infty} h \cdot x^h = \frac{x}{(1-x)^2}$$

Substitute $x = \tfrac{1}{2}$:

$$\sum_{h=0}^{\infty} \frac{h}{2^h} = \frac{\tfrac{1}{2}}{(\tfrac{1}{2})^2} = \frac{\tfrac{1}{2}}{\tfrac{1}{4}} = 2$$

So total work ≤ (N/2) × 2 = **N = O(N)**.

Contrast with N calls to `heappush` (sift-**up**): each element is appended to the bottom and may travel all the way to the root. The i-th insertion costs O(log i), so the total is:

$$\sum_{i=1}^{N} \log i = \log(N!) \approx N \log N$$

Concretely, the last N/2 insertions each go into a heap already of height O(log N) — half the elements pay the full price.

The key insight: **sift-down (heapify)** does cheap work on the numerous bottom nodes (leaves cost 0, near-leaves cost 1, …); **N × heappush** pays O(log N) for each of the last N/2 insertions because the heap is already tall by then.

### Implementation

```python
def heapify(arr: list) -> None:
    """Build a min-heap in-place in O(N)."""
    n = len(arr)
    # Start from the last non-leaf and sift-down each node
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(arr, i, n)

def _sift_down(arr: list, i: int, n: int) -> None:
    smallest = i
    left, right = 2 * i + 1, 2 * i + 2
    if left < n and arr[left] < arr[smallest]:
        smallest = left
    if right < n and arr[right] < arr[smallest]:
        smallest = right
    if smallest != i:
        arr[i], arr[smallest] = arr[smallest], arr[i]
        _sift_down(arr, smallest, n)

arr = [5, 3, 8, 1, 2]
heapify(arr)
print(arr)  # [1, 2, 8, 3, 5]  — valid min-heap
```

Leaves (indices `n//2` to `n-1`) are skipped entirely — they trivially satisfy the heap property. The loop starts at the last internal node `n//2 - 1` and works toward the root, so by the time a node is sifted down, both its subtrees are already valid heaps.

## Common Uses

- **Priority queues** — task schedulers, Dijkstra's, Prim's, A\*
- **K smallest / K largest** — maintain a size-K heap over a stream
- **Median of a data stream** — two heaps: max-heap for lower half, min-heap for upper half
- **Merge K sorted lists** — push (value, list_index) tuples into a min-heap
- **Top-K frequent elements** — count with a hash map, heap on counts

## Python: `heapq`

Python only provides a **min-heap**. For a max-heap, negate values.

```python
import heapq

nums = [5, 1, 8, 3]
heapq.heapify(nums)          # O(N) in-place — now [1, 3, 8, 5]

heapq.heappush(nums, 2)      # O(log N)
smallest = heapq.heappop(nums)  # O(log N) → 1

# Peek without popping
smallest = nums[0]           # O(1)

# Max-heap: negate values
max_heap = [-x for x in [5, 1, 8, 3]]
heapq.heapify(max_heap)
largest = -heapq.heappop(max_heap)  # → 8

# K largest elements — O(N log K)
k_largest = heapq.nlargest(3, [5, 1, 8, 3, 9])  # [9, 8, 5]

# K smallest — O(N log K)
k_smallest = heapq.nsmallest(3, [5, 1, 8, 3, 9])  # [1, 3, 5]
```

### `nlargest` / `nsmallest` — complexity and mutation

Both functions accept any iterable and return a **new list**. The original is never modified; elements in the result are the same objects (shallow), not copies.

| | `nlargest(k, it)` | `nsmallest(k, it)` |
|---|---|---|
| Internal structure | min-heap of size K | max-heap of size K (negated) |
| Time | O(N log K) | O(N log K) |
| Space | O(K) | O(K) |

CPython fallback: if `K >= N/2`, both functions switch to `sorted(...)[::±1][:K]` — O(N log N) time, O(N) space. For typical use where K << N you get the O(N log K) path.

```python
points = [[1,3], [-2,2], [5,8]]
result = heapq.nsmallest(2, points, key=lambda p: p[0]**2 + p[1]**2)
# result → [[-2, 2], [1, 3]]   (new list)
# points → [[1,3], [-2,2], [5,8]]  (unchanged)
# result[0] is points[1]  → True  (same object, not a copy)
```

## Pattern: K Smallest in a Stream

Keep a **max-heap of size K** — if the new element is smaller than the root, replace it.

```python
import heapq

def k_smallest(stream, k: int) -> list[int]:
    max_heap = []
    for val in stream:
        heapq.heappush(max_heap, -val)
        if len(max_heap) > k:
            heapq.heappop(max_heap)
    return sorted(-x for x in max_heap)
```

## Pattern: Median of a Data Stream

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lo = []   # max-heap (lower half), values negated
        self.hi = []   # min-heap (upper half)

    def add(self, num: int) -> None:
        heapq.heappush(self.lo, -num)
        # Balance: ensure lo_max <= hi_min
        heapq.heappush(self.hi, -heapq.heappop(self.lo))
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def median(self) -> float:
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2
```

## Pattern: Merge K Sorted Lists

```python
import heapq

def merge_k_sorted(lists: list[list[int]]) -> list[int]:
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))  # (value, list_idx, elem_idx)

    result = []
    while heap:
        val, i, j = heapq.heappop(heap)
        result.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return result
```

Time: O(N log K) where N = total elements, K = number of lists.

## Trade-offs

- **Fast peek/pop of extremum** but no O(1) arbitrary access or search.
- **Not stable** — equal-priority elements have no guaranteed order; add a tie-breaking counter if insertion order matters.
- **Cache-friendly** — array representation gives better locality than a pointer-based tree.
- **Prefer `heapq.nlargest`/`nsmallest` over sorting** when K << N; they run in O(N log K) vs O(N log N).
