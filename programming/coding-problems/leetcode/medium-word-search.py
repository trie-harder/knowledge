
"""
LeetCode 79. Word Search
https://leetcode.com/problems/word-search/

Given an m x n grid of characters board and a string word, return true if word exists in the grid.
The word can be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once.

---
Approach & Complexity:
- This solution uses **DFS (Depth-First Search)** with backtracking.
- For each cell, we start a DFS if the first character matches, recursively searching adjacent cells for the next character.
- We mark cells as visited by temporarily changing their value, then restore it (backtracking).
- **Why DFS?**
    - DFS is natural for path-finding where you must follow a sequence and can only use each cell once per path.
    - BFS is less suitable here because you need to track the path and visited state for each partial word, which is more complex and less efficient for this problem.
- **Time Complexity:** O(m * n * 3^L), where m,n = board size, L = word length.
    - For each cell, we may explore up to 3 directions (not 4, since we can't go back to the previous cell).
- **Space Complexity:** O(L) for the recursion stack (L = word length).
---
"""

def exist(board, word):
    if not board or not board[0]:
        return False
    m, n = len(board), len(board[0])
    word_len = len(word)

    def dfs(i, j, k):
        if k == word_len:
            return True
        if i < 0 or i >= m or j < 0 or j >= n or board[i][j] != word[k]:
            return False
        tmp = board[i][j]
        board[i][j] = '#'  # mark as visited
        found = (
            dfs(i+1, j, k+1) or
            dfs(i-1, j, k+1) or
            dfs(i, j+1, k+1) or
            dfs(i, j-1, k+1)
        )
        board[i][j] = tmp  # unmark
        return found

    for i in range(m):
        for j in range(n):
            if dfs(i, j, 0):
                return True
    return False

# Example usage and test
if __name__ == "__main__":
    board = [
        ['A','B','C','E'],
        ['S','F','C','S'],
        ['A','D','E','E']
    ]
    print(exist(board, "ABCCED"))  # True
    print(exist(board, "SEE"))     # True
    print(exist(board, "ABCB"))    # False
