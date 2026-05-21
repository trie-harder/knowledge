# Longest Palindromic Substring (LC 5)

> Given string `s`, return the longest substring that is a palindrome.

---

## Key Insight

A substring `s[i..j]` is a palindrome if:
1. The outer characters match: `s[i] == s[j]`
2. The inner substring is also a palindrome: `s[i+1..j-1]` is a palindrome

This gives a clean recursive structure — check outward characters, delegate inward.

---

## Approach 1 — 2D DP

### Define the subproblem

`dp[i][j]` = True if `s[i..j]` is a palindrome

### Recurrence

```
dp[i][j] = s[i] == s[j]  and  dp[i+1][j-1]     (length >= 3)
```

### Base cases

```
dp[i][i]   = True              single char — always a palindrome
dp[i][i+1] = s[i] == s[i+1]   two chars — palindrome iff they match
```

### Fill order

`dp[i][j]` depends on `dp[i+1][j-1]` — a **shorter** substring (shrinks from both ends).  
Neither left-to-right nor right-to-left applies here. Fill by **increasing length**:

```
length 1 → length 2 → length 3 → ... → length N
```

This ensures `dp[i+1][j-1]` (length L-2) is always computed before `dp[i][j]` (length L).

### Table layout (s = "babad", n=5)

```
      j=0  j=1  j=2  j=3  j=4
i=0  [L1] [L2] [L3] [L4] [L5]
i=1       [L1] [L2] [L3] [L4]
i=2            [L1] [L2] [L3]
i=3                 [L1] [L2]
i=4                      [L1]
```

Each diagonal = one length. `dp[i][j]` always reads from one step **down-left** (`dp[i+1][j-1]`):

```
      j=0  j=1  j=2  j=3  j=4
i=0   ...   ...  [?]              ← dp[0][2]: "bab"?
i=1        [ ✓ ]                    ↙ checks dp[1][1]=T, s[0]=='b'==s[2] ✓ → T
```

### Full trace for "babad"

```
L1 (single chars — all True):
  dp[0][0]=T  dp[1][1]=T  dp[2][2]=T  dp[3][3]=T  dp[4][4]=T

L2 (pairs):
  dp[0][1]: 'b'=='a'? F
  dp[1][2]: 'a'=='b'? F
  dp[2][3]: 'b'=='a'? F
  dp[3][4]: 'a'=='d'? F

L3 (triples):
  dp[0][2]: s[0]='b', s[2]='b' ✓, dp[1][1]=T → T   "bab" ← longest so far
  dp[1][3]: s[1]='a', s[3]='a' ✓, dp[2][2]=T → T   "aba" ← tied
  dp[2][4]: s[2]='b', s[4]='d' ✗              → F

L4:
  dp[0][3]: s[0]='b', s[3]='a' ✗  → F
  dp[1][4]: s[1]='a', s[4]='d' ✗  → F

L5:
  dp[0][4]: s[0]='b', s[4]='d' ✗  → F

Answer: "bab" (length 3)
```

### Implementation

```python
def longestPalindrome(s: str) -> str:
    n = len(s)
    dp = [[False] * n for _ in range(n)]
    start, best = 0, 1

    # Base case L1: every single char is a palindrome by definition
    for i in range(n):
        dp[i][i] = True

    # Base case L2: two chars — palindrome iff they match.
    # Can't use the general recurrence here because dp[i+1][j-1] = dp[i+1][i]
    # has i+1 > i, meaning an empty/invalid range — handle separately.
    for i in range(n - 1):
        if s[i] == s[i + 1]:
            dp[i][i+1] = True
            start, best = i, 2

    # General recurrence (length >= 3):
    #   dp[i][j] = s[i]==s[j] and dp[i+1][j-1]
    #
    # Derived from the key insight:
    #   s[i..j] is a palindrome iff
    #     (1) outer chars match:       s[i] == s[j]
    #     (2) inner substring is too:  s[i+1..j-1] is a palindrome
    #
    # So dp[i][j] depends on dp[i+1][j-1] — a strictly shorter substring.
    # Fill by increasing length so dp[i+1][j-1] is always ready.
    #
    # diff = j - i = index gap = length - 1
    #   diff=2 → length 3 (first batch needing the recurrence)
    #   diff=n-1 → length n (full string)
    # range(n - diff): keeps j = i + diff in bounds (j <= n-1 means i <= n-1-diff)
    for diff in range(2, n):          # diff = j - i; same as length in range(3, n+1)
        for i in range(n - diff):     # i + diff <= n-1, so j stays in bounds
            j = i + diff
            if s[i] == s[j] and dp[i+1][j-1]:
                dp[i][j] = True
                start, best = i, diff + 1   # diff + 1 = length

    return s[start:start + best]
```

**Time** O(N²) — N² cells, O(1) per cell  
**Space** O(N²) — the DP table

---

## Approach 2 — Expand Around Center (preferred)

Every palindrome has a center — either a single character (odd length) or two equal characters (even length). Expand outward from each possible center while characters match.

```
"b a b a d"
     ↑       ← center at index 2, expand: s[1]==s[3]? 'a'=='a' ✓ → "bab"
                                  expand: s[0]==s[4]? 'b'=='d' ✗ → stop
```

```python
def longestPalindrome(s: str) -> str:
    start, best = 0, 1

    def expand(l, r):
        nonlocal start, best
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if r - l + 1 > best:
                start, best = l, r - l + 1
            l -= 1
            r += 1

    for i in range(len(s)):
        expand(i, i)       # odd-length center ("aba" → center = i)
        expand(i, i + 1)   # even-length center ("abba" → center = i, i+1)

    return s[start:start + best]
```

**Time** O(N²) — N centers × O(N) expansion each  
**Space** O(1) — no table needed

---

## Comparison

| | 2D DP | Expand Around Center |
|---|---|---|
| Time | O(N²) | O(N²) |
| Space | O(N²) | O(1) |
| Fill order insight | by length (diagonal) | implicit in expansion |
| Reusable subresults | yes — `dp[i][j]` for any range | no |
| Preferred when | need to query many substrings | just find the longest |

**Prefer expand-around-center** for this problem — same time, much less space.  
**Prefer DP** if you need to answer multiple "is s[i..j] a palindrome?" queries (precompute once, look up in O(1)).

---

## Why filling left-to-right within rows would break DP

When filling row `i=0` left to right: computing `dp[0][4]` needs `dp[1][3]`, which is in row 1 — not yet filled. The down-left dependency crosses rows, so row-major order doesn't work. Length-diagonal order is the only fill order that respects all dependencies.

---

*See also: [dynamic-programming.md](dynamic-programming.md) — 2D DP patterns and fill order concepts*
