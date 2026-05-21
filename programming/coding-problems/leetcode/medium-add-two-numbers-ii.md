# LeetCode 445 — Add Two Numbers II (Forward Order)

**Problem:**
Add two numbers represented as linked lists, where each node contains a single digit and the digits are stored in forward order (most significant digit first). You may not modify the input lists (no reversal allowed).

**Example:**
- Input: (7 → 2 → 4 → 3) + (5 → 6 → 4)
- Output: 7 → 8 → 0 → 7  (7243 + 564 = 7807)

---

## Solution (Python)

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def addTwoNumbers(l1, l2):
    # Since the digits are in forward order, we can't process from least to most significant directly.
    # We use stacks to reverse the order, so we can add from the least significant digit (the end of the list).
    stack1, stack2 = [], []
    while l1:
        stack1.append(l1.val)
        l1 = l1.next
    while l2:
        stack2.append(l2.val)
        l2 = l2.next
    carry = 0
    head = None
    # Now pop from stacks to add digits from least significant to most significant
    while stack1 or stack2 or carry:
        v1 = stack1.pop() if stack1 else 0
        v2 = stack2.pop() if stack2 else 0
        total = v1 + v2 + carry
        carry = total // 10
        # Insert new node at the front (since we're building the result in forward order)
        node = ListNode(total % 10)
        node.next = head
        head = node
    return head
```


**How this solution was constructed:**

- The main challenge is that the digits are in forward order, so we can't add from the head (most significant digit) without knowing the length of each list or reversing them (which is not allowed by the problem statement).
- By pushing all digits onto stacks, we can pop them off in reverse order, allowing us to add from least significant to most significant digit, just like the classic addition algorithm.
- We keep a carry and build the result list by prepending nodes (so the most significant digit ends up at the head).
- The loop continues as long as there are digits or a carry to process.
- This approach uses O(n) extra space for the stacks, but is clean and avoids modifying the input lists.

**Key points:**
- Uses stacks to process digits from least to most significant.
- No input list reversal; O(n) time, O(n) space for stacks.
- Handles different lengths and final carry.

---

## Edge Cases
- One or both lists are empty (treat as 0).
- Final carry creates a new node.
- Lists of different lengths.

---

## Alternative Solution: Recursion (No Stacks, No Padding)

```python
# This approach uses recursion to process the lists from the most significant digit (head) to the least.
# It does NOT pad the lists; instead, it handles unequal lengths in the call stack by treating missing nodes as 0.
# Time: O(n), Space: O(n) (call stack and output list)

def addTwoNumbersRecursive(l1, l2):
    # Helper function returns (node, carry)
    def add_helper(n1, n2):
        if not n1 and not n2:
            return (None, 0)
        # Recurse to the next node, using None if a list is shorter
        next_node, carry = add_helper(n1.next if n1 else None, n2.next if n2 else None)
        v1 = n1.val if n1 else 0
        v2 = n2.val if n2 else 0
        total = v1 + v2 + carry
        node = ListNode(total % 10)
        node.next = next_node
        return (node, total // 10)

    head, carry = add_helper(l1, l2)
    # If there's a carry left, add a new node at the front
    if carry:
        head = ListNode(carry, head)
    return head
```

**How this solution was constructed:**
- Recursion allows us to process the most significant digit last (post-order), so we can add from the least significant digit up as the call stack unwinds.
- Instead of padding, we treat missing nodes as 0 at each recursive call, so the code is simpler and doesn't require extra setup.
- The helper returns both the new node and the carry, which is propagated up the call stack.
- If there's a leftover carry after the topmost call, we add a new node at the front.
- This approach is clean, does not require reversing, explicit stacks, or padding, but uses O(n) space for the recursion stack.

**Key points:**
- Recursion processes digits in the correct order for forward lists.
- Handles lists of different lengths by treating missing nodes as 0.
- O(n) time, O(n) space (call stack).
- Handles all edge cases, including final carry.
- Padding aligns the lists for digit-wise addition.
- O(n) time, O(n) space (call stack).
- Handles all edge cases, including final carry.
# Why do we pad the shorter list?
# Padding ensures that our recursive calls always align the correct digits for addition.
# Without padding, the recursion would add the most significant digit of the longer list to zero,
# rather than to the corresponding digit of the shorter list, producing incorrect results.
# Why must we pad the shorter list?
# In recursive addition, each call should add corresponding digits (same place value) from both lists.
# If the lists are unequal in length and we don't pad, the recursion will add the most significant digit of the longer list to zero,
# not to the correct digit of the shorter list. This misaligns the addition and produces incorrect results.
# Padding ensures that every recursive call adds the correct pair of digits, preserving place value alignment.
