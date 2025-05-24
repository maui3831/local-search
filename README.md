# Local Search

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)

For Introduction to Artificial Intelligence
by AI Group 2

## 8 Tiles problem


### 1. Introduction
The 8 tiles problem is a classic sliding puzzle consisting of a 3x3 grid with 8 numbered tiles and one blank space. The objective is to move the tiles until they are ordered sequentially from 1 to 8, with the blank in the bottom-right corner. This project demonstrates solving the 8 tiles problem using the Simulated Annealing algorithm, a local search technique inspired by the annealing process in metallurgy.

### 2. How Code Works
- The puzzle is represented by the `EightTilesPuzzle` class in `tiles.py`.
- The main algorithm is Simulated Annealing, implemented in the `simulated_annealing` function.
- The code starts from an initial state and iteratively explores neighboring states by moving the blank tile.
- The Manhattan distance heuristic is used to evaluate how close a state is to the goal.
- The process is visualized in the terminal using the `rich` library for colored tables.

### 3. Requirements
- Python 3.8 or higher (recommended)
- Required packages:
  - `rich` (for terminal visualization)

Install dependencies with:
```zsh
pip install -r requirements.txt
```
Or, if using `pyproject.toml`:
```zsh
pip install .
```

### 4. How to Run
Run the solver from the terminal:
```zsh
python tiles.py
```

### 5. Features
- Solves the 8 tiles problem using Simulated Annealing
- Visualizes each state and the solution path in the terminal
- Adjustable parameters for temperature, cooling rate, and iterations
- Automatically retries with different parameters if no solution is found

### 6. Project Structure
```
local-search/
├── tiles.py            # 8 tiles problem solver (this project)
├── README.md           # Project documentation
├── pyproject.toml      # Project dependencies
├── ...                 # Other files (e.g., n-queens solvers)
```

### 7. Controls
- The puzzle is solved automatically; no user input is required during execution.
- You can modify the initial state or Simulated Annealing parameters in `tiles.py`.

### 8. Visualization Elements
- The puzzle state is displayed as a colored table in the terminal using `rich`.
- The blank tile is shown as a cyan `#`.
- Each move in the solution path is printed step by step.

### 9. Algorithm Information
- **Simulated Annealing** is a probabilistic technique for approximating the global optimum of a given function.
- The algorithm explores neighboring states and sometimes accepts worse states to escape local minima, with the probability of such moves decreasing as the temperature cools.
- The heuristic used is the sum of Manhattan distances of each tile from its goal position.

### 10. Implementation Details
- The main logic is in `tiles.py`:
  - `EightTilesPuzzle`: Handles state, moves, and heuristic calculation.
  - `simulated_annealing`: Runs the optimization loop.
  - `print_solution_path`: Visualizes the solution.
- The code is modular and can be extended for other local search algorithms.
- Visualization is handled via the `rich` library for better readability.


## N-Queens problem

### 1. Introduction
The N-Queens problem is a classic combinatorial puzzle where the goal is to place N queens on an N×N chessboard so that no two queens threaten each other. This project provides a visual and interactive solution using Simulated Annealing, allowing users to select board sizes and watch the algorithm in action.

### 2. How Code Works
- The main logic is in `queen_annealing.py`.
- The `NQueensGUI` class manages the GUI, board state, and Simulated Annealing process.
- The algorithm starts with a random arrangement of queens and iteratively explores neighboring states by moving queens.
- The number of attacking pairs (conflicts) is used as the energy (cost) function.
- The GUI visualizes each step, allowing users to step through the solution or watch it animate.

### 3. Requirements
- Python 3.8 or higher (recommended)
- Required packages:
  - `pygame` (for GUI and visualization)
- Asset files (sounds and images) in `assets/n_queens/` (fallbacks are used if missing)

Install dependencies with:
```zsh
uv add pygame
```
Or, if using `pyproject.toml`:
```zsh
pip install .
```

### 4. How to Run
Run the visualizer from the terminal:
```zsh
uv run queen_annealing.py
```

### 5. Features
- Visual, interactive N-Queens solver using Simulated Annealing
- Responsive GUI with board size selection (4x4 to 8x8)
- Step-by-step or animated solution process
- Sound effects and custom queen images (if assets are present)
- Adjustable parameters for temperature, cooling rate, and iterations

### 6. Project Structure
```
local-search/
├── queen_annealing.py   # N-Queens visual solver (this project)
├── assets/n_queens/     # Sounds and images for GUI
├── README.md            # Project documentation
├── pyproject.toml       # Project dependencies
├── ...                  # Other files (e.g., 8 tiles solver)
```

### 7. Controls
- Select board size using the size buttons at the top.
- Click on the board to place queens manually.
- Use the 'Solve' button to start Simulated Annealing.
- Use 'Prev' and 'Next' to step through the solution.
- Use 'Reset' to clear the board.
- Toggle fullscreen with the button or F11/F.

### 8. Visualization Elements
- The chessboard and queens are drawn using Pygame.
- The side panel displays algorithm parameters, current step, and status.
- Sound effects and custom images enhance the experience (if assets are available).

### 9. Algorithm Information
- **Simulated Annealing** is a probabilistic optimization technique that explores the solution space by sometimes accepting worse states to escape local minima, with this probability decreasing as the temperature cools.
- The energy function is the number of pairs of queens attacking each other.
- The algorithm iteratively moves queens to reduce conflicts, visualized in real time.

### 10. Implementation Details
- All logic is in `queen_annealing.py`:
  - `NQueensGUI`: Handles GUI, board state, and Simulated Annealing.
  - Asset loading, event handling, and visualization are modularized.
  - The code is designed for extensibility and responsive layout.
- Asset files are optional; the app will run with fallbacks if they are missing.