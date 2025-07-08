import sys
import os
import time
import pickle
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QSpinBox, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal
from GoL_tools import get_screen_resolution, count_neighbors, create_image, initialize_grid, set_wallpaper, clear_directory, suppress_stderr

class SimulationThread(QThread):
    status_update = pyqtSignal(str)

    def __init__(self, directory, cell_size, mode, initial_grid=None):
        super().__init__()
        self.directory = directory
        self.cell_size = cell_size
        self.mode = mode
        self.initial_grid = initial_grid
        self.stop_flag = False

    def run(self):
        try:
            screen_width, screen_height = get_screen_resolution()
            rows = screen_height // self.cell_size
            cols = screen_width // self.cell_size
            grid_file = os.path.join(self.directory, 'game_of_life_grid.pkl')

            if self.initial_grid is not None:
                grid = self.initial_grid
                if len(grid) != rows or len(grid[0]) != cols:
                    self.status_update.emit("Initial grid dimensions do not match. Initializing with mode.")
                    grid = initialize_grid(rows, cols, self.mode)
            elif os.path.exists(grid_file):
                with open(grid_file, 'rb') as f:
                    grid = pickle.load(f)
                if len(grid) != rows or len(grid[0]) != cols:
                    grid = initialize_grid(rows, cols, self.mode)
            else:
                grid = initialize_grid(rows, cols, self.mode)

            gen = 0
            while not self.stop_flag:
                gen += 1
                image_file = os.path.join(self.directory, f'game_of_life_{gen}.png')
                create_image(rows, cols, grid, image_file, self.cell_size, gen)
                time.sleep(1)
                set_wallpaper(image_file)
                if gen > 1:
                    prev_image = os.path.join(self.directory, f'game_of_life_{gen-1}.png')
                    if os.path.exists(prev_image):
                        os.remove(prev_image)
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
                with open(grid_file, 'wb') as f:
                    pickle.dump(new_grid, f)
                grid = new_grid
                live_cells = sum(sum(row) for row in grid)
                self.status_update.emit(f"Generation {gen}: {live_cells} live cells")
        except Exception as e:
            self.status_update.emit(f"Error: {e}")
        finally:
            clear_directory(self.directory)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game of Life")
        self.setGeometry(100, 100, 400, 300)

        # Cell size input
        self.cell_size_label = QLabel("Cell Size:", self)
        self.cell_size_spin = QSpinBox(self)
        self.cell_size_spin.setMinimum(1)
        self.cell_size_spin.setValue(5)

        # Mode selection
        self.mode_label = QLabel("Initialization Mode:", self)
        self.mode_combo = QComboBox(self)
        self.mode_combo.addItems(['random', 'glider', 'import'])

        # Buttons
        self.select_dir_button = QPushButton("Select Directory", self)
        self.select_dir_button.clicked.connect(self.select_directory)

        self.upload_file_button = QPushButton("Upload Grid File", self)
        self.upload_file_button.clicked.connect(self.upload_file)
        self.upload_file_button.setEnabled(False)  # Disabled until 'import' mode

        self.start_button = QPushButton("Start Simulation", self)
        self.start_button.clicked.connect(self.start_simulation)

        self.stop_button = QPushButton("Stop Simulation", self)
        self.stop_button.clicked.connect(self.stop_simulation)

        self.status_label = QLabel("Status: Idle", self)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.cell_size_label)
        layout.addWidget(self.cell_size_spin)
        layout.addWidget(self.mode_label)
        layout.addWidget(self.mode_combo)
        layout.addWidget(self.select_dir_button)
        layout.addWidget(self.upload_file_button)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initial state
        self.gol_directory = None
        self.grid = None
        self.simulation_thread = None

        # Connect mode change to update upload button
        self.mode_combo.currentIndexChanged.connect(self.update_upload_button)

    def update_upload_button(self):
        mode = self.mode_combo.currentText()
        self.upload_file_button.setEnabled(mode == 'import')

    def select_directory(self):
        with suppress_stderr():
            self.gol_directory = QFileDialog.getExistingDirectory(self, "Select directory for Game of Life files")
        if not self.gol_directory:
            self.status_label.setText("No directory selected.")
        else:
            self.status_label.setText(f"Directory selected: {self.gol_directory}")
            self.set_blank_wallpaper()

    def upload_file(self):
        with suppress_stderr():
            pkl_file, _ = QFileDialog.getOpenFileName(self, "Select PKL file", "", "Pickle files (*.pkl)")
        if pkl_file:
            with open(pkl_file, 'rb') as f:
                grid = pickle.load(f)
            cell_size = self.cell_size_spin.value()
            screen_width, screen_height = get_screen_resolution()
            expected_rows = screen_height // cell_size
            expected_cols = screen_width // cell_size
            if len(grid) == expected_rows and len(grid[0]) == expected_cols:
                self.grid = grid
                self.status_label.setText(f"Grid loaded from {pkl_file}")
            else:
                self.status_label.setText("Loaded grid dimensions do not match.")
        else:
            self.status_label.setText("No file selected.")

    def start_simulation(self):
        if not self.gol_directory:
            self.status_label.setText("Please select a directory first.")
            return
        if self.simulation_thread and self.simulation_thread.isRunning():
            self.status_label.setText("Simulation already running.")
            return
        mode = self.mode_combo.currentText()
        cell_size = self.cell_size_spin.value()
        if mode == 'import':
            if self.grid is None:
                self.status_label.setText("Please upload a grid file for import mode.")
                return
            initial_grid = self.grid
        else:
            initial_grid = None
        self.simulation_thread = SimulationThread(self.gol_directory, cell_size, mode, initial_grid)
        self.simulation_thread.status_update.connect(self.update_status)
        self.simulation_thread.start()
        self.status_label.setText("Simulation started.")

    def stop_simulation(self):
        if self.simulation_thread and self.simulation_thread.isRunning():
            self.simulation_thread.stop_flag = True
            self.simulation_thread.wait()
            self.set_blank_wallpaper()
            self.status_label.setText("Simulation stopped.")
        else:
            self.status_label.setText("No simulation running.")

    def set_blank_wallpaper(self):
        if not self.gol_directory:
            return
        cell_size = self.cell_size_spin.value()
        screen_width, screen_height = get_screen_resolution()
        rows = screen_height // cell_size
        cols = screen_width // cell_size
        blank_grid = [[0 for _ in range(cols)] for _ in range(rows)]
        image_file = os.path.join(self.gol_directory, 'blank_grid.png')
        create_image(rows, cols, blank_grid, image_file, cell_size, gen=0)
        set_wallpaper(image_file)

    def update_status(self, message):
        self.status_label.setText(message)

    def closeEvent(self, event):
        if self.simulation_thread and self.simulation_thread.isRunning():
            self.stop_simulation()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
