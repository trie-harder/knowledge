# Sorting Algorithms

Ordered from worst to best time complexity.

---

## Stability

A sort is **stable** if elements that compare as equal appear in the output in the same relative order they had in the input.

```python
data = [("Alice", 2), ("Bob", 1), ("Carol", 2)]

# Stable sort by score — Alice and Carol tied at 2; Alice stays before Carol
sorted(data, key=lambda x: x[1])
# → [("Bob", 1), ("Alice", 2), ("Carol", 2)]  ✓ original order preserved
```

This matters whenever you sort by one key and then by another (multi-key sort by chaining stable sorts), or when the original sequence carries meaning (timestamps, insertion order, rank).

**Unstable** sorts (Quicksort, Heapsort, Selection Sort) may reorder equal elements arbitrarily — fine for plain integers, but a bug waiting to happen with structured records.

Python's `list.sort()` / `sorted()` are always stable (Timsort).

---

## Bubble Sort — O(n²)

Repeatedly swaps adjacent elements that are out of order. Every pass bubbles the largest unsorted element to the end.

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

bubble_sort([5, 3, 8, 1, 2])  # [1, 2, 3, 5, 8]
```

| Best | Average | Worst | Space |
|------|---------|-------|-------|
| O(n) | O(n²)   | O(n²) | O(1)  |

Best case O(n) only if you add an early-exit flag when no swaps occur in a pass.  
**When to use:** Never in production. Useful for teaching.

---

## Selection Sort — O(n²)

Each pass finds the minimum of the unsorted portion and swaps it into position.

```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

selection_sort([5, 3, 8, 1, 2])  # [1, 2, 3, 5, 8]
```

| Best  | Average | Worst | Space |
|-------|---------|-------|-------|
| O(n²) | O(n²)   | O(n²) | O(1)  |

Unlike bubble sort, no best-case benefit — always does O(n²) comparisons.  
Makes at most O(n) swaps, which can be an advantage when writes are expensive.  
**When to use:** Rarely. Marginally better than bubble sort on swap-costly media.

---

## Insertion Sort — O(n²)

Builds a sorted subarray one element at a time. Each new element is shifted leftward into its correct position.

```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

insertion_sort([5, 3, 8, 1, 2])  # [1, 2, 3, 5, 8]
```

| Best | Average | Worst | Space |
|------|---------|-------|-------|
| O(n) | O(n²)   | O(n²) | O(1)  |

**When to use:** Small arrays (n < ~20) or nearly-sorted data. Used as the base case inside Timsort and Introsort for small subarrays — the constant factor is very low.

---

## Merge Sort — O(n log n)

Divide-and-conquer. Recursively splits the array in half, sorts each half, then merges the two sorted halves.

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

merge_sort([5, 3, 8, 1, 2])  # [1, 2, 3, 5, 8]
```

| Best      | Average   | Worst     | Space  |
|-----------|-----------|-----------|--------|
| O(n log n)| O(n log n)| O(n log n)| O(n)   |

**Stable** — equal elements preserve their original order.  
Guaranteed O(n log n) regardless of input, unlike quicksort.  
Downside: O(n) auxiliary space for the merge step.  
**When to use:** When stable sort is required, or when worst-case guarantees matter. Standard choice for sorting linked lists (no random access needed).

---

## Quicksort — O(n log n) average

Picks a pivot, partitions the array into elements less than and greater than the pivot, then recursively sorts each partition.

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]  # middle element as pivot
    left  = [x for x in arr if x < pivot]
    mid   = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + mid + quicksort(right)

quicksort([5, 3, 8, 1, 2])  # [1, 2, 3, 5, 8]
```

In-place partition (more typical in practice):

```python
def quicksort_inplace(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    if low < high:
        p = partition(arr, low, high)
        quicksort_inplace(arr, low, p - 1)
        quicksort_inplace(arr, p + 1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
```

| Best      | Average   | Worst | Space       |
|-----------|-----------|-------|-------------|
| O(n log n)| O(n log n)| O(n²) | O(log n)    |

Worst case O(n²) on already-sorted input with a naive pivot — avoided with randomised pivot or median-of-three selection.  
**Not stable** by default.  
In practice faster than merge sort due to cache locality and low constant factors.  
**When to use:** General-purpose default when stability isn't needed. Python's `sort()` / `sorted()` is Timsort, not quicksort — but CPython uses introsort internally in some C extension paths.

---

## Heapsort — O(n log n)

Builds a max-heap, then repeatedly extracts the maximum to produce a sorted array.

```python
import heapq

def heapsort(arr):
    # heapq is a min-heap; negate values to simulate max-heap
    heap = [-x for x in arr]
    heapq.heapify(heap)
    return [-heapq.heappop(heap) for _ in range(len(heap))]

heapsort([5, 3, 8, 1, 2])  # [1, 2, 3, 5, 8]
```

| Best      | Average   | Worst     | Space |
|-----------|-----------|-----------|-------|
| O(n log n)| O(n log n)| O(n log n)| O(1)  |

Worst-case O(n log n) like merge sort, but in-place like quicksort.  
**Not stable.** Poor cache performance compared to quicksort in practice.  
**When to use:** When you need guaranteed O(n log n) and O(1) space. Used as the fallback in Introsort (C++ `std::sort`).

---

## Timsort — O(n log n) / O(n) best case

Python's built-in sort. A hybrid of merge sort and insertion sort, designed for real-world data that often contains naturally ordered subsequences ("runs").

```python
# You're already using it:
arr = [5, 3, 8, 1, 2]
arr.sort()           # in-place, returns None
sorted(arr)          # returns new list
```

Algorithm sketch:
1. Scan for natural runs (already-ascending or descending sequences); minimum run length ~32–64 elements.
2. Short runs are extended to minrun length using insertion sort.
3. Runs are pushed onto a stack and merged using a merge sort strategy that maintains invariants to minimise total merge work.

| Best | Average   | Worst     | Space  |
|------|-----------|-----------|--------|
| O(n) | O(n log n)| O(n log n)| O(n)   |

**Stable.**  
O(n) on already-sorted or reverse-sorted input.  
Outperforms pure merge sort and quicksort on real-world data with partial ordering.  
**When to use:** Default choice in Python — just call `list.sort()` or `sorted()`.

---

## Counting Sort — O(n + k)

Not comparison-based. Counts occurrences of each value, then reconstructs the sorted array from the counts. Only works for integers (or values mappable to a bounded integer range).

```python
def counting_sort(arr):
    if not arr:
        return arr
    offset = min(arr)
    k = max(arr) - offset + 1
    counts = [0] * k
    for x in arr:
        counts[x - offset] += 1
    result = []
    for i, c in enumerate(counts):
        result.extend([i + offset] * c)
    return result

counting_sort([4, 2, 2, 8, 3, 3, 1])  # [1, 2, 2, 3, 3, 4, 8]
```

| Best     | Average  | Worst    | Space  |
|----------|----------|----------|--------|
| O(n + k) | O(n + k) | O(n + k) | O(k)   |

k = range of values. If k >> n, this degenerates to wasted space and time.  
**Stable.**  
**When to use:** Integers in a small, known range (e.g. sorting ages, scores 0–100).

---

## Radix Sort — O(nw)

Sorts integers digit by digit (or byte by byte), from least significant to most significant digit, using a stable sub-sort (usually counting sort) at each digit position.

```python
def radix_sort(arr):
    if not arr:
        return arr
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        arr = counting_sort_by_digit(arr, exp)
        exp *= 10
    return arr

def counting_sort_by_digit(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    for x in arr:
        count[(x // exp) % 10] += 1
    for i in range(1, 10):
        count[i] += count[i - 1]
    for x in reversed(arr):
        idx = (x // exp) % 10
        output[count[idx] - 1] = x
        count[idx] -= 1
    return output

radix_sort([170, 45, 75, 90, 802, 24, 2, 66])  # [2, 24, 45, 66, 75, 90, 170, 802]
```

| Best  | Average | Worst | Space  |
|-------|---------|-------|--------|
| O(nw) | O(nw)   | O(nw) | O(n+w) |

w = number of digits (word size). For 32-bit integers, w = 10 decimal digits or 4 bytes.  
**Stable.**  
Can outperform comparison sorts when n is large and w is small.  
**When to use:** Large datasets of fixed-width integers or fixed-length strings.

---

## Summary

| Algorithm      | Best       | Average    | Worst      | Space    | Stable |
|----------------|------------|------------|------------|----------|--------|
| Bubble Sort    | O(n)       | O(n²)      | O(n²)      | O(1)     | Yes    |
| Selection Sort | O(n²)      | O(n²)      | O(n²)      | O(1)     | No     |
| Insertion Sort | O(n)       | O(n²)      | O(n²)      | O(1)     | Yes    |
| Merge Sort     | O(n log n) | O(n log n) | O(n log n) | O(n)     | Yes    |
| Quicksort      | O(n log n) | O(n log n) | O(n²)      | O(log n) | No     |
| Heapsort       | O(n log n) | O(n log n) | O(n log n) | O(1)     | No     |
| Timsort        | O(n)       | O(n log n) | O(n log n) | O(n)     | Yes    |
| Counting Sort  | O(n + k)   | O(n + k)   | O(n + k)   | O(k)     | Yes    |
| Radix Sort     | O(nw)      | O(nw)      | O(nw)      | O(n+w)   | Yes    |

**Practical defaults:**
- General purpose → `list.sort()` (Timsort)
- Need guaranteed O(n log n) + O(1) space → Heapsort
- Integers in bounded range → Counting Sort or Radix Sort
- Small / nearly-sorted arrays → Insertion Sort

---

## Python `list.sort()` — Using `key`

`list.sort()` and `sorted()` accept a `key` callable. Python extracts the key from each element once, sorts by those keys, then returns the elements — never calling a comparator directly between two elements (unlike C++'s `std::sort` comparator).

```python
# Sort by a single field
words = ["banana", "fig", "apple", "date"]
words.sort(key=len)                      # ["fig", "fig", "date", "apple", "banana"]
words.sort(key=str.lower)                # case-insensitive alphabetical

# Sort objects by attribute
people = [("Alice", 30), ("Bob", 25), ("Carol", 30)]
people.sort(key=lambda p: p[1])          # by age ascending

# Multi-key: primary ascending age, secondary ascending name (alphabetical)
people.sort(key=lambda p: (p[1], p[0]))

# Reverse a single key without negating strings — wrap in a class
from functools import cmp_to_key

# Descending on one field, ascending on another (cleaner with negation for numbers)
people.sort(key=lambda p: (-p[1], p[0]))  # age desc, name asc
```

**`key` vs `cmp_to_key`:** Prefer `key` always — it's O(N) extractions then standard comparisons. `cmp_to_key` wraps an old-style two-argument comparator (like Python 2's `cmp`) into a key object; use it only when the comparison logic can't be expressed as a extracted value (e.g. custom locale sorting, version strings).

```python
from functools import cmp_to_key

def version_cmp(a, b):
    # compare "1.10.2" vs "1.9.0" numerically per segment
    for x, y in zip(map(int, a.split(".")), map(int, b.split("."))):
        if x != y:
            return x - y  # negative → a first, positive → b first
    return len(a) - len(b)

versions = ["1.10.2", "1.9.0", "2.0.0", "1.9.1"]
versions.sort(key=cmp_to_key(version_cmp))
# ["1.9.0", "1.9.1", "1.10.2", "2.0.0"]
```

Both `list.sort()` (in-place, returns `None`) and `sorted()` (returns new list) accept the same `key` and `reverse` arguments.
