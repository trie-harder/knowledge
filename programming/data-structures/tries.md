# Tries

A **trie** (prefix tree) is a tree where each node represents a single character, and paths from root to marked nodes spell out words.

```
insert("cat", "car", "card", "care", "bat")

        root
       /    \
      c      b
      |      |
      a      a
     / \     |
    t*  r    t*
        |
        d*  e*
```

`*` = end-of-word marker

## Why a Trie Over a Hash Set / BST?

| Operation        | Hash Set      | BST            | Trie           |
|------------------|---------------|----------------|----------------|
| Exact lookup     | O(L) avg      | O(L·log N)     | O(L)           |
| Prefix search    | O(N·L)        | O(N·L)         | **O(P)**       |
| Wildcard search  | O(N·L)        | O(N·L)         | O(N·L) worst; prunes early in practice |
| Autocomplete     | O(N·L)        | O(N·L)         | **O(P + K)**   |
| Sorted iteration | O(N log N)    | O(N)           | O(N)           |

`L` = word length, `N` = number of words, `P` = prefix length, `K` = number of matches.

The key advantage: **shared prefixes** are stored once, so a query for prefix `"car"` immediately prunes the entire `b…` subtree.

## Complexity

| Operation      | Time     | Space   | Notes                                      |
|----------------|----------|---------|--------------------------------------------|
| **Build**      | O(N·L)   | O(N·L)  | Each character is one node; worst case no sharing |
| **Insert**     | O(L)     | O(L)    | At most L new nodes per word               |
| **Exact lookup** | O(L)   | O(1)    | Walk L edges, check end-of-word flag       |
| **Prefix search** | O(P)  | O(1)    | Walk P edges; existence check only         |
| **Autocomplete** | O(P+K) | O(K)   | Walk to prefix node, then DFS/BFS subtree  |
| **Delete**     | O(L)     | O(1)    | Unmark end-of-word; prune if no children   |

Space in practice is **much better than O(N·L)** when words share prefixes (e.g. a dictionary of English words shares enormous common prefixes).

## Where Tries Are Used Effectively

- **Autocomplete / typeahead** — search engines, IDEs, mobile keyboards
- **Spell checkers** — fast prefix walk + end-of-word check
- **IP routing (radix trie)** — longest-prefix match on binary address bits
- **DNS resolvers** — hierarchical label matching
- **Word games** — Boggle, Scrabble valid-word checks over a board
- **Genome sequence search** — shared k-mer prefix compression
- **`grep`-style matching** — aho-corasick automaton is a trie + failure links

## Minimal Python Snippet

```python
class TrieNode:
    __slots__ = ("children", "is_end")
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def _walk(self, s: str) -> TrieNode | None:
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node
```

## Wildcard Search Analysis (LC 211)

When search supports `.` as a wildcard (matches any single character), a DFS is needed that fans out to all children at each `.` node.

| Approach | `addWord` | `searchWord` (no wildcard) | `searchWord` (wildcard `.`) |
|----------|-----------|---------------------------|-----------------------------|
| Hash map | O(M) amortized | O(M) avg | O(N·M) — must scan all keys |
| BST      | O(M·log N) | O(M·log N) | O(N·M) — binary ordering breaks down |
| Trie     | O(M) | **O(M)** | O(N·M) worst case |

`M` = word/pattern length, `N` = number of stored words.

**Why trie wildcard is O(N·M) and not O(26^M):**
The trie contains at most N·M nodes total, so a DFS visits at most N·M nodes regardless of branching factor. O(26^M) would only apply to a completely full trie storing all 26^M possible words — never realistic.

**Why trie still wins in practice:**
All three approaches share the same O(N·M) worst case for wildcards, but the trie can prune entire subtrees for non-wildcard characters. A pattern like `"c.t"` only explores the `c` subtree; hash map and BST always scan all N words.

**Recursive stack space:** O(M) — stack depth equals pattern length, each frame is O(1). Only O(M²) if each frame copies the remaining string (e.g. Python string slicing) instead of passing an index.

## Trade-offs

- **Memory overhead**: each node holds a dict (or fixed 26-char array); for sparse alphabets a `dict` child map is more space-efficient; for dense alphabets a fixed array gives O(1) child access.
- **Cache locality**: pointer-chasing per character is slower in practice than a single hash lookup for exact-match-only workloads.
- **Best fit**: workloads that mix exact lookup *and* prefix queries, or need sorted/autocomplete iteration.
