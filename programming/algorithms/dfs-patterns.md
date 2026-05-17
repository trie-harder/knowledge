# DFS Patterns

## State Management: `nonlocal` vs. Threading Return Values

When a DFS helper needs to maintain state across recursive calls, there are two approaches.

### Threading (functional style)

Pass state in as a parameter; return the updated state alongside the result.

```python
def isValidBST(root):
    def dfs(node, prev):
        if node is None:
            return True, prev
        leftValid, prev = dfs(node.left, prev)   # prev updated by left subtree
        if not leftValid:
            return False, prev
        if node.val <= prev:
            return False, prev
        prev = node.val
        return dfs(node.right, prev)             # updated prev passed to right

    valid, _ = dfs(root, float('-inf'))
    return valid
```

**When to use:**
- The state *shapes* the recursion — it changes meaningfully at each call and the callee needs it to determine what to do
- Examples: `depth` in level-order (each level is one deeper), `min_val`/`max_val` bounds in BST validation by range
- You want a pure function (no side effects, easier to test)

---

### `nonlocal` (imperative style)

Mutate a variable in the enclosing scope. This is a side effect — the variable acts as a shared cursor or accumulator updated as the traversal progresses.

```python
def isValidBST(root):
    prev = float('-inf')

    def dfs(node):
        nonlocal prev
        if node is None:
            return True
        if not dfs(node.left):      # validates left subtree, advances prev
            return False
        if node.val <= prev:
            return False
        prev = node.val             # advance cursor to current node
        return dfs(node.right)      # tail call on right subtree

    return dfs(root)
```

**When to use:**
- State flows *linearly* across the traversal, cutting across the tree structure rather than following it
- Examples: `prev` in inorder BST validation (flows left → root → right sequentially), a running count or result list that all branches contribute to
- Threading would require returning multiple values awkwardly just to pass a cursor around

---

### Decision rule

> **Thread it** if the value shapes the recursion (the recursive call's behaviour depends on it).
> **Use `nonlocal`** if you're maintaining a cursor or accumulator that flows across the whole traversal.

| Pattern | State type | Style |
|---|---|---|
| `depth` in level-order | Shapes recursion — each call is one deeper | Thread |
| `prev` in inorder validation | Sequential cursor across all nodes | `nonlocal` |
| Result list accumulation | Shared collector for all branches | `nonlocal` |
| Min/max bounds in BST validation | Shapes recursion — different bounds per branch | Thread |

---

## Traversal Orders

| Order | When work happens | Code shape |
|---|---|---|
| Pre-order | Before recursive calls | `process(node)` → `dfs(left)` → `dfs(right)` |
| In-order | Between recursive calls | `dfs(left)` → `process(node)` → `dfs(right)` |
| Post-order | After recursive calls return | `dfs(left)` → `dfs(right)` → `process(node)` |

Pre-order and in-order with two recursive calls are **not** tail recursive — deferred work always exists. See `tail-call-optimization.md`.

---

## Iterative DFS with an Explicit Stack

The call stack in recursive DFS is implicit. Iterative DFS makes it explicit — each stack entry replaces a call frame. Anything passed as arguments in the recursive version becomes part of the tuple pushed onto the stack.

### Preorder (root → left → right)

Process node immediately on pop. Push right before left so left is popped first (LIFO).

```python
def preorder(root):
    if not root:
        return
    stack = [root]
    while stack:
        node = stack.pop()
        print(node.val)           # process immediately
        if node.right:
            stack.append(node.right)   # push right first
        if node.left:
            stack.append(node.left)    # left popped first
```

### Inorder (left → root → right)

Can't process on first visit — must go all the way left first, then backtrack. Use a `curr` pointer to chase left edges; the stack holds the "return address" for backtracking.

```python
def inorder(root):
    stack = []
    curr = root
    while curr or stack:
        while curr:               # chase left as far as possible
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()        # backtrack
        print(curr.val)           # process here — between left and right
        curr = curr.right         # then go right
```

### Postorder (left → right → root)

Process node after both subtrees. The trick: collect in *reverse postorder* (root → right → left) then reverse the result. This is preorder with left/right push order swapped.

```python
def postorder(root):
    if not root:
        return []
    stack = [root]
    result = []
    while stack:
        node = stack.pop()
        result.append(node.val)   # collect reversed
        if node.left:
            stack.append(node.left)    # push left first
        if node.right:
            stack.append(node.right)   # right popped first
    return result[::-1]           # reverse → left → right → root
```

### With parameters (constraint propagation)

Pass node state as tuples — equivalent to recursive parameters:

```python
def isValidBST(root):
    stack = [(root, float('-inf'), float('inf'))]
    while stack:
        node, low, high = stack.pop()
        if node is None:
            continue
        if not (low < node.val < high):
            return False
        stack.append((node.left,  low,       node.val))
        stack.append((node.right, node.val,  high))
    return True
```

### Summary

| Order | Core idea | Difficulty |
|---|---|---|
| Preorder | Pop and process immediately; push right then left | Easy |
| Inorder | Chase left to bottom; pop and process; go right | Medium |
| Postorder | Preorder with left/right swapped, then reverse | Medium |
