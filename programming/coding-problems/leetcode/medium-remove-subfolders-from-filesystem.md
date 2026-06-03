# LeetCode 1233 — Remove Sub-Folders from the Filesystem

**Problem:**
Given a list of folder paths, remove all sub-folders. A folder is a sub-folder if it is contained within another folder (i.e., its path starts with another folder’s path followed by a '/'). Return the list of folders after removing all sub-folders, in any order.

---

## Step-by-step Intuition

1. **Sort the Folders:**
   - Sort the folder paths lexicographically. This ensures that parent folders come before their sub-folders.

2. **Iterate and Filter:**
   - Iterate through the sorted list, and for each folder, check if it is a sub-folder of the last folder added to the result.
   - If not, add it to the result.
   - If it is a sub-folder (i.e., starts with the last result folder + '/'), skip it.

---

## Solution (Python)

```python
def removeSubfolders(folder):
    folder.sort()
    res = []
    for f in folder:
        if not res or not f.startswith(res[-1] + '/'):
            res.append(f)
    return res
```

---

## Complexity Analysis
- **Time Complexity:** $O(n \log n \cdot L)$, where $n$ is the number of folders and $L$ is the average length of a folder path (for sorting and prefix checking).
- **Space Complexity:** $O(n \cdot L)$ for storing the result.

---

## Key Points
- Sorting ensures parent folders are checked before sub-folders.
- Use string prefix checking to efficiently filter sub-folders.
- Only folders that are not sub-folders of the previous result are kept.

---

## Related Problems
- LeetCode 616: Add Bold Tag in String
- LeetCode 648: Replace Words
- LeetCode 1233: Remove Sub-Folders from the Filesystem (this problem)
