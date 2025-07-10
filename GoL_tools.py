import random
import pickle
import os
import sys
import platform
import contextlib
from PIL import Image, ImageDraw
from screeninfo import get_monitors
from scipy.signal import convolve2d
import numpy as np

def get_screen_resolution():
    if platform.system() == 'Darwin':
        try:
            from AppKit import NSScreen
            return int(NSScreen.mainScreen().frame().size.width), int(NSScreen.mainScreen().frame().size.height)
        except ImportError:
            print("AppKit not available, falling back to default resolution")
            return 1920, 1080
    elif platform.system() == 'Windows':
        try:
            for monitor in get_monitors():
                if monitor.is_primary:
                    return monitor.width, monitor.height
            return 1920, 1080
        except Exception as e:
            print(f"Error getting screen resolution on Windows: {e}")
            return 1920, 1080
    else:
        return 1920, 1080  # Default fallback

def count_neighbors(grid):
    kernel = np.array([[1, 1, 1],
                        [1, 0, 1],
                        [1, 1, 1]])
    neighbor_counts = convolve2d(np.array(grid), kernel, mode='same', boundary='wrap')
    return np.array(neighbor_counts)

def create_image(rows, cols, grid, image_file, cell_size, gen):
    width = cols * cell_size
    height = rows * cell_size
    image = Image.new('RGB', (width, height), 'black')
    draw = ImageDraw.Draw(image)
    if platform.system() == 'Darwin':
        for i in range(rows):
            for j in range(cols):
                if grid[i][j] == 1:
                    draw.rectangle(
                        [j * cell_size, i * cell_size, (j + 1) * cell_size - 1, (i + 1) * cell_size - 1],
                        fill='white'
                    )
    elif platform.system() == 'Windows':
        for i in range(rows):
            for j in range(cols):
                x0, y0 = j * cell_size, i * cell_size
                x1, y1 = x0 + cell_size, y0 + cell_size
                color = (255, 255, 255) if grid[i][j] == 1 else (0, 0, 0)
                draw.rectangle([x0, y0, x1, y1], fill=color)
    image.save(image_file)

def initialize_grid(rows, cols, mode='random'):
    if platform.system() == 'Darwin':
        if mode == 'random':
            return [[random.choice([0, 1]) for _ in range(cols)] for _ in range(rows)]
        elif mode == 'glider':
            grid = [[0 for _ in range(cols)] for _ in range(rows)]
            if rows >= 3 and cols >= 3:
                grid[1][0] = 1
                grid[2][1] = 1
                grid[0][2] = 1
                grid[1][2] = 1
                grid[2][2] = 1
            return grid
        else:
            raise ValueError("Invalid mode: use 'random' or 'glider'")
    elif platform.system() == 'Windows':
        import numpy as np
        grid = np.array([[0 for _ in range(cols)] for _ in range(rows)])
        if mode == 'random':
            grid = np.array([[random.choice([0, 1]) for _ in range(cols)] for _ in range(rows)])
        elif mode == 'glider':
            pass  # Not implemented in Windows version
        return grid

def set_wallpaper(image_file):
    if platform.system() == 'Windows':
        import ctypes
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_file, 0)
    elif platform.system() == 'Darwin':
        from appscript import app, mactypes
        app('Finder').desktop_picture.set(mactypes.File(image_file))
    else:
        print("Unsupported platform for setting wallpaper")

def clear_directory(directory):
    if platform.system() == 'Windows':
        import shutil
        if os.path.exists(directory):
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"Error deleting {item_path}: {e}")
        else:
            print(f"Directory {directory} does not exist")
    elif platform.system() == 'Darwin':
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

@contextlib.contextmanager
def suppress_stderr():
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr