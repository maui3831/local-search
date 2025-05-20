import random
import math
import copy
import time


class EightTilesPuzzle:
    def __init__(self, initial_state=None):
        self.state = (
            initial_state if initial_state else [[5, 1, 3], [4, 2, 8], [6, 7, "#"]]
        )
        self.goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, "#"]]
        self.blank_pos = self._find_blank()

    def _find_blank(self):
        """Find the position of the blank tile."""
        for i in range(3):
            for j in range(3):
                if self.state[i][j] == "#":
                    return (i, j)
        return None

    def _get_possible_moves(self):
        """Get all possible moves from the current state."""
        i, j = self.blank_pos
        moves = []

        # Check up
        if i > 0:
            moves.append((-1, 0))
        # Check down
        if i < 2:
            moves.append((1, 0))
        # Check left
        if j > 0:
            moves.append((0, -1))
        # Check right
        if j < 2:
            moves.append((0, 1))

        return moves

    def _apply_move(self, move):
        """Apply a move to the current state."""
        di, dj = move
        i, j = self.blank_pos

        # Create a new state
        new_state = copy.deepcopy(self.state)

        # Swap the blank with the tile in the move direction
        new_state[i][j], new_state[i + di][j + dj] = (
            new_state[i + di][j + dj],
            new_state[i][j],
        )

        # Update the blank position
        new_blank_pos = (i + di, j + dj)

        return new_state, new_blank_pos

    def get_random_neighbor(self):
        """Generate a random neighboring state."""
        # Get all possible moves
        moves = self._get_possible_moves()

        # Select a random move
        move = random.choice(moves)

        # Apply the move
        new_state, new_blank_pos = self._apply_move(move)

        # Create a new puzzle with the new state
        neighbor = copy.deepcopy(self)
        neighbor.state = new_state
        neighbor.blank_pos = new_blank_pos

        return neighbor

    def calculate_heuristic(self):
        """Calculate the Manhattan distance heuristic."""
        distance = 0

        for i in range(3):
            for j in range(3):
                value = self.state[i][j]

                # Skip the blank tile
                if value == "#":
                    continue

                # Find the position of the value in the goal state
                for gi in range(3):
                    for gj in range(3):
                        if self.goal_state[gi][gj] == value:
                            # Calculate Manhattan distance
                            distance += abs(i - gi) + abs(j - gj)
                            break

        return distance

    def is_goal(self):
        """Check if the current state is the goal state."""
        return self.state == self.goal_state

    def print_state(self):
        """Print the current state of the puzzle."""
        for row in self.state:
            print(row)
        print()


def simulated_annealing(
    puzzle,
    initial_temperature=1.0,
    cooling_rate=0.995,
    min_temperature=0.01,
    max_iterations=10000,
):
    """Solve the 8 tiles puzzle using simulated annealing."""
    # Initialize variables
    current_puzzle = copy.deepcopy(puzzle)
    best_puzzle = copy.deepcopy(current_puzzle)
    current_energy = current_puzzle.calculate_heuristic()
    best_energy = current_energy
    temperature = initial_temperature
    iteration = 0

    # For tracking solution path
    moves_history = []
    moves_history.append(copy.deepcopy(current_puzzle.state))

    while (
        temperature > min_temperature
        and iteration < max_iterations
        and not current_puzzle.is_goal()
    ):
        # Generate a random neighbor
        neighbor_puzzle = current_puzzle.get_random_neighbor()
        neighbor_energy = neighbor_puzzle.calculate_heuristic()

        # Calculate the energy (cost) difference
        energy_diff = neighbor_energy - current_energy

        # Accept the neighbor if it's better or with a certain probability
        if energy_diff < 0 or random.random() < math.exp(-energy_diff / temperature):
            current_puzzle = neighbor_puzzle
            current_energy = neighbor_energy
            moves_history.append(copy.deepcopy(current_puzzle.state))

            # Update the best solution if necessary
            if current_energy < best_energy:
                best_puzzle = copy.deepcopy(current_puzzle)
                best_energy = current_energy

        # Cool down the temperature
        temperature *= cooling_rate
        iteration += 1

    return best_puzzle, best_energy, iteration, moves_history


def print_solution_path(moves_history):
    """Print the solution path."""
    print(f"Solution found in {len(moves_history) - 1} moves:")
    for i, state in enumerate(moves_history):
        print(f"Move {i}:")
        for row in state:
            print(row)
        print()


def main():
    # Initial state
    initial_state = [[5, 1, 3], [4, 2, 8], [6, 7, "#"]]

    # Create the puzzle
    puzzle = EightTilesPuzzle(initial_state)

    print("Initial state:")
    puzzle.print_state()

    print("Goal state:")
    for row in puzzle.goal_state:
        print(row)
    print()

    print("Solving with simulated annealing...")
    start_time = time.time()

    # Parameters for simulated annealing
    initial_temperature = 1.0
    cooling_rate = 0.995
    min_temperature = 0.01
    max_iterations = 50000

    # Run simulated annealing
    best_puzzle, best_energy, iterations, moves_history = simulated_annealing(
        puzzle,
        initial_temperature=initial_temperature,
        cooling_rate=cooling_rate,
        min_temperature=min_temperature,
        max_iterations=max_iterations,
    )

    end_time = time.time()

    if best_puzzle.is_goal():
        print(
            f"Solution found in {iterations} iterations and {end_time - start_time:.2f} seconds!"
        )
        print(f"Final heuristic value: {best_energy}")
        print_solution_path(moves_history)
    else:
        print(f"No solution found after {iterations} iterations.")
        print(f"Best heuristic value achieved: {best_energy}")
        print("Best state found:")
        best_puzzle.print_state()

    # Try again with different parameters if no solution was found
    if not best_puzzle.is_goal():
        print("\nTrying again with different parameters...")

        # Different parameters for better exploration
        initial_temperature = 5.0  # Higher initial temperature
        cooling_rate = 0.999  # Slower cooling rate
        max_iterations = 100000  # More iterations

        start_time = time.time()
        best_puzzle, best_energy, iterations, moves_history = simulated_annealing(
            puzzle,
            initial_temperature=initial_temperature,
            cooling_rate=cooling_rate,
            min_temperature=min_temperature,
            max_iterations=max_iterations,
        )
        end_time = time.time()

        if best_puzzle.is_goal():
            print(
                f"Solution found in {iterations} iterations and {end_time - start_time:.2f} seconds!"
            )
            print(f"Final heuristic value: {best_energy}")
            print_solution_path(moves_history)
        else:
            print(f"Still no solution found after {iterations} iterations.")
            print(f"Best heuristic value achieved: {best_energy}")
            print("Best state found:")
            best_puzzle.print_state()


if __name__ == "__main__":
    main()
