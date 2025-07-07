import random
import pickle
import os
import sys
import contextlib
import platform
from PIL import Image, ImageDraw

def get_screen_resolution():
    if platform.system() == 'Windows':
        from win32api import GetSystemMetrics
        return GetSystemMetrics(0), GetSystemMetrics(1)
    elif platform.system() == 'Darwin':
        from AppKit import NSScreen
        return int(NSScreen.mainScreen().frame().size.width), int(NSScreen.mainScreen().frame().size.height)
    else:
        return 1920, 1080  # Default resolution

def count_neighbors(rows, cols, grid, i, j):
    total = 0
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            r = (i + di) % rows
            c = (j + dj) % cols
            total += grid[r][c]
    return total

def create_image(rows, cols, grid, file_name, cell_size, gen):
    width = cols * cell_size
    height = rows * cell_size
    image = Image.new('RGB', (width, height), 'black')
    draw = ImageDraw.Draw(image)
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 1:
                draw.rectangle(
                    [j * cell_size, i * cell_size, (j + 1) * cell_size - 1, (i + 1) * cell_size - 1],
                    fill='white'
                )
    image.save(file_name)

def initialize_grid(rows, cols, mode='random'):
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

def set_wallpaper(file_path):
    if platform.system() == 'Windows':
        import ctypes
        ctypes.windll.user32.SystemParametersInfoW(20, 0, file_path, 0)
    elif platform.system() == 'Darwin':
        from appscript import app, mactypes
        app('Finder').desktop_picture.set(mactypes.File(file_path))
    else:
        os.system(f"gsettings set org.gnome.desktop.background picture-uri 'file://{file_path}'")

def clear_directory(directory):
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
