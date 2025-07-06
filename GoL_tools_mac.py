import subprocess
from PIL import Image, ImageDraw
from screeninfo import get_monitors
import random

DEBUG = 0

def get_screen_resolution():
    """Get the primary monitor's resolution."""
    try:
        for monitor in get_monitors():
            if monitor.is_primary:
                return monitor.width, monitor.height
        return 1920, 1080  # Fallback resolution
    except Exception as e:
        print(f"Error getting screen Dimensionality Reduction screen resolution: {e}")
        return 1920, 1080  # Fallback

def count_neighbors(rows, cols, grid, i, j):
    """Count live neighbors for a cell at (i, j)."""
    count = 0
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni, nj = i + di, j + dj
            if 0 <= ni < rows and 0 <= nj < cols:
                count += grid[ni][nj]
    return count

def create_image(rows, cols, grid, image_file, cell_size, gen):
    """Create a PNG image from the grid with black and white squares."""
    image = Image.new('RGB', (cols * cell_size, rows * cell_size), color='black')
    draw = ImageDraw.Draw(image)
    
    for i in range(rows):
        for j in range(cols):
            x0, y0 = j * cell_size, i * cell_size
            x1, y1 = x0 + cell_size, y0 + cell_size
            color = (255, 255, 255) if grid[i][j] == 1 else (0, 0, 0)
            draw.rectangle([x0, y0, x1, y1], fill=color)
    
    image.save(image_file)
    if DEBUG:
        print(f"Generated image for generation {gen}: {image_file}")

def initialize_grid(rows, cols, preset='random'):
    """Initialize a grid with a preset."""
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    if preset == 'random':
        grid = [[random.choice([0, 1]) for _ in range(cols)] for _ in range(rows)]
    elif preset == 'glider':
        pass
    else:
        pass
    return grid

def set_wallpaper(image_file):
    """Set the generated image as the desktop wallpaper using System Events."""
    script = f'''
    tell application "System Events"
        tell every desktop
            set picture to POSIX file "{image_file}"
            set picture rotation to 0
            set change interval to 0
        end tell
    end tell
    '''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if DEBUG:
        if result.returncode != 0:
            print(f"Error setting wallpaper: {result.stderr}")
        else:
            print(f"Set wallpaper to {image_file}")

def clear_directory(path):
    if os.path.exists(path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Error deleting {item_path}: {e}")
    else:
        print(f"Directory {path} does not exist")
