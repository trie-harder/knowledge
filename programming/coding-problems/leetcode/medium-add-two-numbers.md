# LeetCode 2 — Add Two Numbers (Reverse Order)

**Problem:**
Add two numbers represented as linked lists, where each node contains a single digit and the digits are stored in reverse order (least significant digit first).

**Example:**
- Input: (2 → 4 → 3) + (5 → 6 → 4)
- Output: 7 → 0 → 8  (342 + 465 = 807)

---

## Solution (Python)

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def addTwoNumbers(l1, l2):
    # We use a dummy head to simplify edge cases (no need to special-case the first node)
    dummy = ListNode(0)
    curr = dummy
    carry = 0
    # Loop continues as long as there are nodes in either list or a carry to process
    while l1 or l2 or carry:
        # If a list is exhausted, treat its value as 0
        v1 = l1.val if l1 else 0
        v2 = l2.val if l2 else 0
        # Add the two digits and the carry from the previous step
        total = v1 + v2 + carry
        # Compute new carry (will be 1 if total >= 10, else 0)
        carry = total // 10
        # The digit to store in this node is total % 10
        curr.next = ListNode(total % 10)
        curr = curr.next
        # Advance input pointers if possible
        if l1: l1 = l1.next
        if l2: l2 = l2.next
    # Return the next node after dummy (the real head)
    return dummy.next
```

**How this solution was constructed:**

- The problem is essentially digit-wise addition, just like how you add numbers by hand from right to left, carrying over when the sum is 10 or more.
- Since the lists are in reverse order, we can process them from head to tail, adding corresponding digits and propagating the carry.
- We use a dummy head node to avoid special-casing the first digit (this is a common linked list trick).
- The loop continues as long as there are digits left in either list or a carry to process (e.g., 5 + 5 = 10 needs an extra node for the carry).
- At each step, we add the two digits (or 0 if a list is exhausted) and the carry, create a new node for the result, and move forward.
- The carry is always either 0 or 1 (since 9 + 9 + 1 = 19 is the max sum for a digit).
- The result is built as a new linked list, which is returned (excluding the dummy head).

**Key points:**
- Handles lists of different lengths and final carry.
- O(n) time, O(1) extra space (output list is required).
- Dummy head simplifies edge cases and pointer management.

---

## Edge Cases
- One or both lists are empty (treat as 0).
- Final carry creates a new node (e.g., 5+5=10).
- Lists of different lengths.
