import time
import pickle
import os
from GoL_tools_mac import get_screen_resolution, count_neighbors, create_image, initialize_grid, set_wallpaper

# File to store grid state
GRID_FILE = 'C:/Users/stanley/Desktop/GOL/game_of_life_grid.pkl'
DEBUG = 0

if __name__ == "__main__":
    # Get screen resolution
    screen_width, screen_height = get_screen_resolution()
    
    # Set cell size (adjustable; smaller = denser grid, larger = bigger cells)
    cell_size = 20
    
    # Calculate grid size based on screen resolution
    rows = screen_height // cell_size
    cols = screen_width // cell_size
    if DEBUG:
        print(f"Screen resolution: {screen_width}x{screen_height}, grid size: {rows}x{cols}, cell size: {cell_size}")

    # Load grid from file or initialize it
    if os.path.exists(GRID_FILE):
        with open(GRID_FILE, 'rb') as f:
            grid = pickle.load(f)
            # Verify loaded grid matches current dimensions
            if len(grid) != rows or len(grid[0]) != cols:
                if DEBUG:
                    print("Grid dimensions mismatch; initializing new grid")
                grid = initialize_grid(rows, cols)
    else:
        grid = initialize_grid(rows, cols)

    try:
        gen = 0
        while True:
            gen += 1
            # Use unique filename for each generation
            image_file = f'C:/Users/stanley/Desktop/GOL/game_of_life_{gen}.png'
            
            # Create and save the image for the current grid
            create_image(rows, cols, grid, image_file, cell_size, gen)
            #time.sleep(0.5)  # Ensure file write completes
            set_wallpaper(image_file)
            
            # Clean up previous image to avoid clutter
            if gen > 1:
                prev_image = f'C:/Users/stanley/Desktop/GOL/game_of_life_{gen-1}.png'
                if os.path.exists(prev_image):
                    os.remove(prev_image)
            
            # Compute the next generation
            new_grid = [[0 for _ in range(cols)] for _ in range(rows)]
            for i in range(rows):
                for j in range(cols):
                    neighbors = count_neighbors(rows, cols, grid, i, j)
                    if grid[i][j] == 1:
                        if neighbors == 2 or neighbors == 3:
                            new_grid[i][j] = 1
                    else:
                        if neighbors == 3:
                            new_grid[i][j] = 1
            
            # Save the new grid state
            with open(GRID_FILE, 'wb') as f:
                pickle.dump(new_grid, f)
            
            grid = new_grid
            if DEBUG:
                print(f"Generation {gen}: {sum(sum(row) for row in grid)} live cells")
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nSimulation stopped.")
        # Clean up temporary files
        if os.path.exists(GRID_FILE):
            os.remove(GRID_FILE)
        # Remove all generated image files
        i = 1
        while True:
            img = f'C:/Users/stanley/Desktop/GOL/game_of_life_{i}.png'
            if os.path.exists(img):
                os.remove(img)
                i += 1
            else:
                break
