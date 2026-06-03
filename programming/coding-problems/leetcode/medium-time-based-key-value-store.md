# LeetCode 981 — Time-Based Key-Value Store

**Problem:**
Design a time-based key-value data structure that can store multiple values for the same key at different timestamps and retrieve the value for a key at a given timestamp.

- Implement two methods:
  - `set(key, value, timestamp)`: Stores the key and value, along with the given timestamp.
  - `get(key, timestamp)`: Returns the value such that set was called previously with `set(key, value, ts)` and `ts <= timestamp`. If there are multiple such values, return the one with the largest `ts`. If there are none, return an empty string.

---

## Step-by-step Intuition

1. **Data Structure:**
   - Use a dictionary to map each key to a list of (timestamp, value) pairs.
   - Store the list sorted by timestamp (append in order, since timestamps are strictly increasing).

2. **Setting a Value:**
   - For `set(key, value, timestamp)`, append (timestamp, value) to the list for that key.

3. **Getting a Value:**
   - For `get(key, timestamp)`, perform binary search on the list of (timestamp, value) pairs for the key to find the largest timestamp less than or equal to the given timestamp.
   - Return the corresponding value, or "" if not found.

---

## Solution (Python)

```python
from collections import defaultdict
import bisect

class TimeMap:
    def __init__(self):
        self.store = defaultdict(list)  # key -> list of (timestamp, value)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        arr = self.store[key]
        # Binary search for rightmost timestamp <= given timestamp
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
  - `set`: $O(1)$ (append to list)
  - `get`: $O(\log N)$ (binary search, where $N$ is the number of timestamps for the key)
- **Space Complexity:** $O(K + N)$, where $K$ is the number of unique keys and $N$ is the total number of set operations.

---

## Key Points
- Use a dictionary of lists to store (timestamp, value) pairs for each key.
- Use binary search to efficiently find the correct value for a given timestamp.
- Timestamps are strictly increasing for each key, so appending keeps the list sorted.

---

## Related Problems
- LeetCode 362: Design Hit Counter
- LeetCode 981: Time-Based Key-Value Store (this problem)
- LeetCode 432: All O(1) Data Structure
