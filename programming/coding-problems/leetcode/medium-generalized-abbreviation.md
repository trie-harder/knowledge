# LeetCode 320 — Generalized Abbreviation (i18n-style)

**Problem:**
Given a string, generate all possible generalized abbreviations by replacing any substring of consecutive characters with their count.

**Example:**
Input: "test"
Output: ['test', 'tes1', 'te1t', 'te2', 't1st', 't1s1', 't2t', 't3', '1est', '1es1', '1e1t', '1e2', '2st', '2s1', '3t', '4']

---

## Solution (Python, Backtracking)

```python
def generateAbbreviations(word):
    res = []
    def backtrack(pos, cur, count):
        if pos == len(word):
            # If count > 0, append it to the end
            if count > 0:
                cur += str(count)
            res.append(cur)
            return
        # Option 1: Abbreviate this character (increase count)
        backtrack(pos + 1, cur, count + 1)
        # Option 2: Keep this character
        new_cur = cur + (str(count) if count > 0 else '') + word[pos]
        backtrack(pos + 1, new_cur, 0)
    backtrack(0, '', 0)
    return res

# Example usage:
# print(generateAbbreviations('test'))
```

**How this solution was constructed:**
- Use backtracking to explore all choices at each character: abbreviate (increase count) or keep (append count if any, then the character).
- When the end is reached, append any pending count.
- This ensures consecutive abbreviations are combined (e.g., 't2t' not 't1t1').
- Time: O(2^n), Space: O(2^n * n) for n = len(word).

**Key points:**
- Backtracking is ideal for generating all combinations.
- Count is only appended when a character is kept, or at the end.
- Handles all edge cases (empty string, all abbreviations, no abbreviations).

---

# Why don't we use a for loop in the backtracking for this problem?
# In the subsets problem, a for loop is natural because at each step you can pick any of the remaining elements—
# the recursion is n-ary (many branches per node).
# For generalized abbreviation, at each character you have only two choices:
#   1. Abbreviate this character (increase the count, don't add the character to the result)
#   2. Keep this character (append the current count if any, then the character, and reset the count)
# This makes the recursion tree strictly binary at each position—so a for loop is not a natural fit.
# In summary: subsets = n-ary tree (for loop), generalized abbreviation = binary tree (no for loop).
