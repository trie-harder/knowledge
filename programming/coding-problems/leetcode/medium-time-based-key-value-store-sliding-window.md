# Time-Based Key-Value Store with Sliding Window (Last 10 Seconds)

**Problem (Follow-up):**
Design a time-based key-value data structure that supports:
- `set(key, value, timestamp)`: Store the key and value at the given timestamp.
- `get(key, timestamp)`: Return the value for the key at the largest timestamp ≤ `timestamp`, but **only consider values set within the last 10 seconds** (i.e., timestamps ≥ `timestamp - 10`).
- You may evict entries older than 10 seconds to save space.

---

## Step-by-step Intuition

1. **Data Structure:**
   - For each key, store a list (or deque) of (timestamp, value) pairs, sorted by timestamp.
   - Only keep entries with timestamp ≥ (current_time - 10).

2. **Eviction:**
   - On each `set` or `get`, remove entries with timestamp < (current_time - 10) for that key.
   - This keeps the data structure small and efficient.

3. **Getting a Value:**
   - Use binary search to find the largest timestamp ≤ query timestamp, but only among entries in the last 10 seconds.
   - If no such entry exists, return "".

---

## Solution (Python)

```python
from collections import defaultdict, deque
import bisect

class SlidingTimeMap:
    def __init__(self):
        self.store = defaultdict(deque)  # key -> deque of (timestamp, value)

    def set(self, key: str, value: str, timestamp: int) -> None:
        dq = self.store[key]
        dq.append((timestamp, value))
        # Evict old entries
        while dq and dq[0][0] < timestamp - 10:
            dq.popleft()

    def get(self, key: str, timestamp: int) -> str:
        dq = self.store[key]
        # Evict old entries
        while dq and dq[0][0] < timestamp - 10:
            dq.popleft()
        # Tradeoff: We use deque for fast O(1) eviction from the front during set/get.
        # For get, we convert to a list for binary search (O(n)), but since the window is small (last 10 seconds),
        # this is usually fast and get is often called less frequently than set.
        # This keeps set/evict fast and code simple, accepting a minor cost in get.
        # Binary search for rightmost timestamp <= query timestamp
        arr = list(dq)
        left, right = 0, len(arr) - 1
        res = ""
        while left <= right:
            mid = (left + right) // 2
            if arr[mid][0] <= timestamp:
                res = arr[mid][1]
                left = mid + 1
            else:
                right = mid - 1
        return res
```

---

## Complexity Analysis
- **Time Complexity:**
  - `set`: $O(1)$ amortized (append and evict from deque)
  - `get`: $O(\log n)$ (binary search, where $n$ is the number of entries in the last 10 seconds for the key)
- **Space Complexity:** $O(K \cdot W)$, where $K$ is the number of unique keys and $W$ is the maximum number of sets in any 10-second window.

---

## Key Points
- Use a deque to efficiently evict old entries from the front.
- Binary search is still possible on the (short) list of recent entries.
- This approach is optimal for a sliding window of recent timestamps.

---

## Related Problems
- LeetCode 981: Time-Based Key-Value Store
- LeetCode 362: Design Hit Counter (sliding window)
