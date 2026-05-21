# Longest Palindromic Subsequence (LC 516) — Medium

> Given string `s`, return the length of the longest palindromic subsequence.  
> A subsequence is characters in order but **not necessarily contiguous** (unlike a substring).

---

## Connection to Longest Palindromic Substring

Both problems use the same 2D subproblem shape `dp[i][j]` over `s[i..j]`, fill by the same diagonal order, and share the same outer-chars-match structure. The difference is what happens when chars **don't** match:

| | Palindromic Substring | Palindromic Subsequence |
|---|---|---|
| `dp[i][j]` | `bool` — is `s[i..j]` a palindrome? | `int` — length of longest pal. subseq. in `s[i..j]` |
| `s[i] == s[j]` | `dp[i+1][j-1]` must also be True | `dp[i+1][j-1] + 2` |
| `s[i] != s[j]` | `False` — stop, inner structure irrelevant | `max(dp[i+1][j], dp[i][j-1])` — skip one end, take the best |
| Base case | `dp[i][i] = True` | `dp[i][i] = 1` |
| Fill order | by length (diagonal) | by length (diagonal) |
| Answer | track the best `True` cell | `dp[0][n-1]` |

The key new idea: when outer chars don't match, substring DP gives up immediately. Subsequence DP can still salvage — try dropping `s[i]` (look at `s[i+1..j]`) or dropping `s[j]` (look at `s[i..j-1]`), and take whichever is longer.

---

## Subproblem

```
dp[i][j] = length of the longest palindromic subsequence in s[i..j]
```

### Recurrence

```
s[i] == s[j]:   dp[i][j] = dp[i+1][j-1] + 2     include both outer chars
s[i] != s[j]:   dp[i][j] = max(dp[i+1][j], dp[i][j-1])   skip one end
```

### Base cases

```
dp[i][i] = 1        single char — palindrome of length 1
dp[i][j] = 0        for i > j  (empty range — arises when length=2 and s[i]==s[j])
```

The length=2 case is handled automatically by the recurrence:
- `s[i]==s[i+1]`: `dp[i+1][i] = 0` (empty) → `dp[i][i+1] = 0 + 2 = 2` ✓
- `s[i]!=s[i+1]`: `max(dp[i+1][i+1], dp[i][i]) = max(1, 1) = 1` ✓

No separate L2 pass needed — unlike the substring problem.

### Fill order

Same as substring: `dp[i][j]` depends on `dp[i+1][j-1]`, `dp[i+1][j]`, and `dp[i][j-1]` — all strictly shorter substrings. Fill by **increasing length**.

---

## Trace for `s = "bbbab"`

```
L1 (base):  dp[0][0]=1  dp[1][1]=1  dp[2][2]=1  dp[3][3]=1  dp[4][4]=1

L2:
  dp[0][1]: 'b'=='b' ✓  dp[1][0]+2 = 0+2 = 2
  dp[1][2]: 'b'=='b' ✓  dp[2][1]+2 = 0+2 = 2
  dp[2][3]: 'b'!='a'    max(dp[3][3], dp[2][2]) = max(1,1) = 1
  dp[3][4]: 'a'!='b'    max(dp[4][4], dp[3][3]) = max(1,1) = 1

L3:
  dp[0][2]: 'b'=='b' ✓  dp[1][1]+2 = 1+2 = 3
  dp[1][3]: 'b'!='a'    max(dp[2][3], dp[1][2]) = max(1,2) = 2
  dp[2][4]: 'b'=='b' ✓  dp[3][3]+2 = 1+2 = 3

L4:
  dp[0][3]: 'b'!='a'    max(dp[1][3], dp[0][2]) = max(2,3) = 3
  dp[1][4]: 'b'=='b' ✓  dp[2][3]+2 = 1+2 = 3

L5:
  dp[0][4]: 'b'=='b' ✓  dp[1][3]+2 = 2+2 = 4

Answer: dp[0][4] = 4   ("bbbb")
```

---

## Implementation

```python
def longestPalindromeSubseq(s: str) -> int:
    n = len(s)
    # dp[i][j] = length of longest palindromic subsequence in s[i..j]
    # i > j: empty range → 0 (Python initialises to 0, so this is free)
    dp = [[0] * n for _ in range(n)]

    for i in range(n):
        dp[i][i] = 1   # base case: single char

    # Fill by increasing length — ensures dp[i+1][j-1], dp[i+1][j], dp[i][j-1] are ready
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                # Outer chars match — include both, recurse inward
                # when length=2: dp[i+1][j-1] = dp[i+1][i] = 0 (i+1>i) → gives 2 ✓
                dp[i][j] = dp[i+1][j-1] + 2
            else:
                # Chars don't match — can't use both ends
                # Try dropping s[i] or dropping s[j], take the better option
                dp[i][j] = max(dp[i+1][j], dp[i][j-1])

    return dp[0][n - 1]
```

**Time** O(N²) — N² cells, O(1) per cell  
**Space** O(N²) — the DP table

---

*See also: [longest-palindromic-substring.md](../algorithms/longest-palindromic-substring.md) — same 2D DP shape, fill order, and outer-match structure*
