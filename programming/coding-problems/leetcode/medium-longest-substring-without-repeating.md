# Longest Substring Without Repeating Characters (LC 3) — Medium

> Given a string `s`, find the length of the longest substring without duplicate characters.

---

## Key Insight

Sliding window `[l, r]` where all characters within are unique.

- Grow `r` to the right one step at a time
- When `s[r]` is already in the window → shrink from `l` until the duplicate is removed
- Track the max window size seen

---

## Approach 1 — Set + Two Pointers

Use a set to track characters currently in the window. When a duplicate is found, pop from the left one character at a time.

```python
def lengthOfLongestSubstring(s: str) -> int:
    seen = set()
    l = 0
    best = 0

    for r in range(len(s)):
        # Shrink from left until s[r] is no longer in the window
        while s[r] in seen:
            seen.remove(s[l])
            l += 1
        seen.add(s[r])
        best = max(best, r - l + 1)

    return best
```

**Time** O(N) — each character is added and removed at most once  
**Space** O(min(N, A)) — set size bounded by alphabet size A

---

## Approach 2 — Dict (direct jump, preferred)

Instead of evicting one character at a time, store the last seen index of each character and jump `l` directly past the duplicate.

```python
def lengthOfLongestSubstring(s: str) -> int:
    last_seen = {}   # char → index of its last occurrence
    l = 0
    best = 0

    for r, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= l:
            # Duplicate is inside the current window — jump l past it
            # last_seen[ch] + 1: skip over the previous occurrence of ch
            l = last_seen[ch] + 1
        last_seen[ch] = r
        best = max(best, r - l + 1)

    return best
```

**Time** O(N) — single pass  
**Space** O(min(N, A))

### Why the `>= l` guard?

`last_seen[ch]` might point to an occurrence **before** the current window (we never clean up the dict). Without the guard, we'd incorrectly shrink `l` backward.

```
s = "abba"
       ↑ r=3, ch='a', last_seen['a']=0, but l=2 already
       last_seen['a']=0 < l=2  → 'a' is outside the window, no conflict → skip jump
```

---

## Comparison

| | Set + Two Pointers | Dict (direct jump) |
|---|---|---|
| Time | O(N) | O(N) |
| Space | O(A) | O(A) |
| Left pointer movement | one step at a time | jumps directly |
| Clarity | easier to trace | requires the `>= l` guard |
