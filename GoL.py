import time

# Grid size
rows = 10
cols = 10

# Initialize grid with a glider pattern
grid = [[0 for _ in range(cols)] for _ in range(rows)]
grid[0][1] = 1
grid[1][2] = 1
grid[2][0] = 1
grid[2][1] = 1
grid[2][2] = 1

def print_grid(grid):
    for row in grid:
        print(' '.join(['*' if cell else '.' for cell in row]))

def count_neighbors(grid, i, j):
    count = 0
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni, nj = i + di, j + dj
            # Only count neighbors within the grid
            if 0 <= ni < rows and 0 <= nj < cols:
                count += grid[ni][nj]
    return count

try:
    gen = 0
    while True:
        print(f"Generation {gen}")
        print_grid(grid)
        new_grid = [[0 for _ in range(cols)] for _ in range(rows)]
        for i in range(rows):
            for j in range(cols):
                neighbors = count_neighbors(grid, i, j)
                if grid[i][j] == 1:
                    if neighbors == 2 or neighbors == 3:
                        new_grid[i][j] = 1
                else:
                    if neighbors == 3:
                        new_grid[i][j] = 1
        grid = new_grid
        gen += 1
        print()  # Add a blank line between generations
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nSimulation stopped.")
