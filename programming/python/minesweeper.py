'''

Basically Minesweeper

Part 1. take a grid and reveal all cells, cells have count of adjacent mines

Part 2. Impl click - reveal single cell on the new game for grid, reveal adj cells, lose if hit mine

'''



from collections import deque


grid = [[0,-1,0],
        [0,0,0],
        [-1,0,0]]

class MineSweeper:
    def __init__(self, grid):
        self.m = len(grid)
        self.n = len(grid[0])
        self.grid = grid

        self.mine = -1

        # WRONG this will create a reference to the same row across all rows
        # self.hidden = [['X'] * self.n]  * self.m
        #
        # Always use a list comprehension for 2D grids in Python to avoid shared references between rows.
        self.hidden = [['X' for _ in range(self.n)] for _ in range(self.m)]


    
    def revealGrid(self):
        for i in range(self.m):
            for j in range(self.n):
                if self.grid[i][j] == self.mine:
                    # add 1 to all adj neighbors
                    for r,c in [(1,0),(-1,0),(0,1),(0,-1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                        nr, nc = i+r, j+c
                        if 0 <= nr < self.m and 0 <= nc < self.n and self.grid[nr][nc] != self.mine:
                            self.grid[nr][nc] += 1
        
        return self.grid


    def click(self, i, j):
        if self.grid[i][j] == self.mine:
            self.hidden[i][j] = 'M'
            return self.hidden
        
        queue = deque([(i, j)])
        visited = set([(i, j)])

        while queue:
            i, j = queue.pop()

            # check adj mine count for i,j cell
            adj_mines = self.grid[i][j]

            self.hidden[i][j] = adj_mines
            
            if adj_mines == 0:
                for r,c in [(1,0),(-1,0),(0,1),(0,-1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                    nr, nc = i+r, j+c
                    if 0 <= nr < self.m and 0 <= nc < self.n and self.grid[nr][nc] != self.mine:
                        if (nr,nc) not in visited:
                            visited.add((nr, nc))
                            queue.appendleft((nr, nc))
        
        return self.hidden




if __name__ == "__main__":
    ms = MineSweeper(grid)
    print(ms.revealGrid())

    state = ms.click(0,0)
    print(state)
    state = ms.click(2,2)
    print(state)
    state = ms.click(0,2)
    print(state)
    state = ms.click(1,0)
    print(state)
                        

'''
[[1, -1, 1], 
 [2, 2, 1], 
 [-1, 1, 0]]

[[1, 'X', 'X'],
 ['X', 'X', 'X'],
 ['X', 'X', 'X']]

[[1, 'X', 'X'], 
 ['X', 2, 1], 
 ['X', 1, 0]]

[[1, 'X', 1], 
 [2, 2, 1], 
['X', 1, 0]]


Follow-ups:
  Game over flag for clicks - when click mine, game is over
  Handle retry game for new grid?

Summary on Game Board:
 - You can return the full board, a mask, a list of revealed cells, a mapping, or an event log.
 - The best choice depends on your UI, performance needs, and how you want to communicate state changes to the user or frontend.

 
*** The best choice depends on how you want to communicate state changes to the user or frontend

 
'''
    