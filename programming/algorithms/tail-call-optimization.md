# Tail Call Optimization (TCO)

## What is a Tail Call?

A **tail call** is a recursive call that is the **last action** in a function — the return value of the recursive call is returned directly, with no work done after it returns.

A language runtime that supports **TCO** can reuse the current stack frame instead of pushing a new one, making tail recursion equivalent to iteration in memory usage.

**Python does not implement TCO.** Recursive calls always consume a stack frame. Understanding the concept still matters for:
- Recognising when a loop is the correct implementation
- Understanding why some recursions are $O(h)$ space and others aren't
- Interview discussions about recursion classification

---

## Tail Recursive — True Examples

### LCA on a BST (LC 235)

```python
def lowestCommonAncestor(self, root, p, q):
    if p.val > root.val and q.val > root.val:
        return self.lowestCommonAncestor(root.right, p, q)  # last action
    elif p.val < root.val and q.val < root.val:
        return self.lowestCommonAncestor(root.left, p, q)   # last action
    else:
        return root
```

Why: each branch makes **one** recursive call and returns its result directly. No work after the call.

Equivalent iterative form (what TCO would produce):

```python
def lowestCommonAncestor(self, root, p, q):
    while True:
        if p.val > root.val and q.val > root.val:
            root = root.right
        elif p.val < root.val and q.val < root.val:
            root = root.left
        else:
            return root
```

### Linked List Traversal

```python
def find(node, target):
    if node is None:
        return None
    if node.val == target:
        return node
    return find(node.next, target)  # last action, single call
```

---

## NOT Tail Recursive — Common Examples

### Max Depth of Binary Tree (LC 104)

```python
def maxDepth(self, root):
    if root is None:
        return 0
    leftDepth = self.maxDepth(root.left)
    rightDepth = self.maxDepth(root.right)
    return 1 + max(leftDepth, rightDepth)  # work done AFTER calls return
```

Why not: `1 + max(...)` executes after both recursive calls complete. Work is deferred — this is **post-order head recursion**.

### Invert Binary Tree (LC 226)

```python
def invertTree(self, root):
    if root is None:
        return None
    left = self.invertTree(root.left)
    right = self.invertTree(root.right)
    root.left, root.right = right, left  # work done AFTER calls return
    return root
```

### Reverse Linked List (recursive)

```python
def reverseList(self, head):
    if not head or not head.next:
        return head
    new_head = self.reverseList(head.next)  # recurse first
    head.next.next = head                   # work done on the way back up
    head.next = None
    return new_head
```

---

## Why Binary Trees Can Never Be Truly Tail Recursive

A tail call requires: "go do this one thing; you don't need to come back to me."

Binary trees have **two children**. Even if the second call could be a tail call, the first call still has the entire right subtree waiting. There is always deferred work — the stack frame must be preserved.

This is why iterative BFS/DFS with an explicit stack is the standard way to handle deep trees.

---

## The Identifying Test

Ask: **is there any computation left to do after the recursive call returns?**

| Pattern | Tail recursive? |
|---|---|
| `return recurse(...)` | Yes — result passed straight back |
| `return 1 + recurse(...)` | No — addition happens after return |
| `x = recurse(...); return x + 1` | No — addition happens after return |
| Two recursive calls | Never — at least one has deferred work |
| `recurse(left); recurse(right)` | No — second call is pending while first runs |

---

## Space Complexity Implications

| Recursion type | Stack frames held simultaneously | Space |
|---|---|---|
| True tail recursion | 1 (reused, with TCO) | $O(1)$ — but Python doesn't do this |
| Single-path head recursion | $h$ (depth of recursion) | $O(h)$ |
| Binary tree DFS | $h$ (one path root→leaf) | $O(h)$ = $O(\log n)$ balanced, $O(n)$ skewed |

For DFS on an arbitrary tree: $O(h)$, which is $O(n)$ worst case (skewed tree) and $O(\log n)$ best case (balanced tree).
