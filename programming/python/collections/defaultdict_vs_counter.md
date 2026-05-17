# `defaultdict` vs `Counter`

Both live in `collections`. Both are dict subclasses. The difference is purpose and what they give you for free.

---

## `defaultdict`

A dict that calls a factory function to supply a missing key's default value instead of raising `KeyError`.

```python
from collections import defaultdict

d = defaultdict(int)    # missing key → 0
d = defaultdict(list)   # missing key → []
d = defaultdict(set)    # missing key → set()
d = defaultdict(lambda: "N/A")  # missing key → "N/A"

d["x"] += 1   # no KeyError even though "x" didn't exist
```

The factory is any zero-argument callable. Accessing a missing key **creates the key** with the default value — a common footgun when you want read-only access.

```python
d = defaultdict(int)
if d["missing"]:   # this creates "missing": 0 in d !!
    ...
```

Use `.get()` or `key in d` to avoid this.

---

## `Counter`

A dict subclass specifically for counting hashable objects. Missing keys return `0` (read-only — does NOT create the key).

```python
from collections import Counter

c = Counter("abracadabra")
# Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})

c["z"]      # → 0, does NOT insert "z" into c
"z" in c    # → False
```

### Counter-specific features

```python
c = Counter("aab")
d = Counter("abb")

# Most common
c.most_common(2)    # [('a', 2), ('b', 1)]

# Arithmetic
c + d               # Counter({'b': 3, 'a': 3})  — add counts
c - d               # Counter({'a': 1})           — subtract, drop ≤ 0
c & d               # Counter({'a': 1, 'b': 1})  — min of each
c | d               # Counter({'b': 2, 'a': 2})  — max of each

# Equality — compares as dicts (exact key-value match)
Counter("ab") == Counter("ba")   # True — same freq map
```

---

## Key Difference: Missing Key Behaviour

| Behaviour | `defaultdict(int)` | `Counter` |
|---|---|---|
| `d["missing"]` | Returns `0` **and inserts key** | Returns `0`, does **not** insert |
| `"missing" in d` after access | `True` | `False` |
| Intended use | General auto-init dict | Frequency counting |

This matters for equality comparisons. If you use `defaultdict` for frequency maps and accidentally access a non-existent key, you'll have spurious zero-value entries that break `==` comparisons:

```python
a = defaultdict(int, {"a": 1})
b = defaultdict(int, {"a": 1})

_ = a["b"]   # creates "b": 0 in a

a == b       # False! {"a": 1, "b": 0} != {"a": 1}
```

`Counter` avoids this:
```python
a = Counter({"a": 1})
_ = a["b"]   # does NOT insert
a == Counter({"a": 1})  # True
```

---

## Sliding Window Frequency Map — Practical Example

LeetCode 567 (Permutation in String): check if any window of `s2` is an anagram of `s1`.

### With `Counter`

```python
s1Count = Counter(s1)
s2Count = Counter(s2[:len(s1)])

for i in range(len(s2) - len(s1) + 1):
    if s1Count == s2Count:
        return True
    # slide: remove left char
    s2Count[s2[i]] -= 1
    if s2Count[s2[i]] == 0:
        del s2Count[s2[i]]   # must clean up or equality breaks
    # slide: add right char
    if i + len(s1) < len(s2):
        s2Count[s2[i + len(s1)]] += 1
```

### With `defaultdict`

```python
s1Count = defaultdict(int)
s2Count = defaultdict(int)

for c in s1: s1Count[c] += 1
for c in s2[:len(s1)]: s2Count[c] += 1

for i in range(len(s2) - len(s1) + 1):
    if s1Count == s2Count:
        return True
    s2Count[s2[i]] -= 1
    if s2Count[s2[i]] == 0:
        del s2Count[s2[i]]   # same cleanup required — zero keys break ==
    if i + len(s1) < len(s2):
        s2Count[s2[i + len(s1)]] += 1
```

Both require explicit zero-key deletion before equality comparison. `Counter` is slightly more ergonomic here because it handles read-access without creating keys, but the core sliding window logic is identical.

---

## When to Use Which

| Use case | Prefer |
|---|---|
| Counting chars, words, elements | `Counter` |
| Frequency map equality comparisons | `Counter` (safer — no accidental key creation) |
| Grouping items by key (e.g. group anagrams) | `defaultdict(list)` |
| Graph adjacency lists | `defaultdict(list)` or `defaultdict(set)` |
| Memoisation / caches with non-zero defaults | `defaultdict(lambda: ...)` |
| Any counting + arithmetic (add/subtract counters) | `Counter` |
