# LeetCode 911 — Online Election

**Problem:**
You are given two integer arrays persons and times. At time times[i], the person persons[i] received a vote. Implement the class TopVotedCandidate:
- `TopVotedCandidate(persons, times)`: Initializes the object with the voting data.
- `q(t)`: Returns the person who was leading the election at time t. If there is a tie, the most recent vote wins.

---

## Step-by-step Intuition

1. **Preprocessing:**
   - As you process the votes, keep track of the current leader at each time.
   - For each vote, update the vote count for the person and update the leader if necessary.
   - Store the leader at each time in a list.

2. **Query:**
   - For a query at time t, use binary search to find the largest time ≤ t.
   - Return the leader at that time.

---

## Solution (Python)

```python
import bisect
from collections import defaultdict

class TopVotedCandidate:
    def __init__(self, persons, times):
        self.times = times
        self.leaders = []
        count = defaultdict(int)
        leader = -1
        for p in persons:
            count[p] += 1
            if leader == -1 or count[p] >= count[leader]:
                leader = p
            self.leaders.append(leader)

    def q(self, t):
        # Find the rightmost time <= t
        i = bisect.bisect_right(self.times, t) - 1
        return self.leaders[i]
```

---

## Complexity Analysis
- **Time Complexity:**
  - Constructor: $O(N)$, where $N$ is the number of votes.
  - Query: $O(\log N)$ per query (binary search).
- **Space Complexity:** $O(N)$ for storing leaders and times.

---

## Key Points
- Precompute the leader at each vote time for fast queries.
- Use binary search to efficiently answer queries for any time t.
- In case of a tie, the most recent vote wins (handled by updating leader on >=).

---

## Related Problems
- LeetCode 981: Time-Based Key-Value Store
- LeetCode 362: Design Hit Counter
- LeetCode 911: Online Election (this problem)
