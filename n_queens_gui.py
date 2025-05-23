"""
Data Structures and Algorithms - Programming Task 2 - N-Queens Problem - GUI Version

BS Computer Science 2-4 | Group 1

    Bognot, Kristina Cassandra D.
    Frilles, Roljohn C.
    Llesis, Earl Gem
    Mancilla, Nathalia Angela S.
    Montemayor, Keith Reijay M.
    Palpal-latoc, Alfred Joshua I.
    Reyes, Rainier Joshua D.
    Torres, Nigel Frederick J.
"""

import pygame
import sys
import time

class NQueensGUI:
    def __init__(self, n):
        pygame.init()
        self.n = n
        self.solution = []
        self.top_row = 0
        
        # Window setup
        self.WINDOW_SIZE = 800
        self.CELL_SIZE = self.WINDOW_SIZE // self.n
        self.WINDOW_SIZE = self.CELL_SIZE * self.n  # Adjust window size to fit board perfectly
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.GRAY = (128, 128, 128)
        
        # Initialize display
        self.screen = pygame.display.set_mode((self.WINDOW_SIZE, self.WINDOW_SIZE))
        pygame.display.set_caption(f"N-Queens Problem (N={n})")
        
        # Font setup
        self.font = pygame.font.Font(None, 36)
        
        # Animation speed (in seconds)
        self.animation_speed = 0.5

    def draw_board(self):
        """Draw the chessboard"""
        self.screen.fill(self.WHITE)
        
        # Draw the board
        for row in range(self.n):
            for col in range(self.n):
                x = col * self.CELL_SIZE
                y = row * self.CELL_SIZE
                
                # Alternate colors for chessboard pattern
                color = self.WHITE if (row + col) % 2 == 0 else self.GRAY
                pygame.draw.rect(self.screen, color, (x, y, self.CELL_SIZE, self.CELL_SIZE))
                
                # Draw grid lines
                pygame.draw.rect(self.screen, self.BLACK, (x, y, self.CELL_SIZE, self.CELL_SIZE), 1)

    def draw_queens(self):
        """Draw the queens on the board"""
        for row, col in self.solution:
            x = col * self.CELL_SIZE + self.CELL_SIZE // 2
            y = row * self.CELL_SIZE + self.CELL_SIZE // 2
            
            # Draw queen (as a circle with a crown)
            pygame.draw.circle(self.screen, self.RED, (x, y), self.CELL_SIZE // 3)
            # Draw crown
            crown_points = [
                (x - self.CELL_SIZE//4, y),
                (x - self.CELL_SIZE//6, y - self.CELL_SIZE//4),
                (x, y - self.CELL_SIZE//3),
                (x + self.CELL_SIZE//6, y - self.CELL_SIZE//4),
                (x + self.CELL_SIZE//4, y)
            ]
            pygame.draw.lines(self.screen, self.RED, False, crown_points, 2)

    def is_safe(self, row, col):
        """Check if placing a queen at (row, col) is safe"""
        for i in range(self.top_row):
            if self.solution[i][1] == col or abs(self.solution[i][0] - row) == abs(self.solution[i][1] - col):
                return False
        return True

    def solve(self, curr_row=0):
        """Solve the N-Queens problem using backtracking with visualization"""
        if curr_row == self.n:
            return True

        for col in range(self.n):
            if self.is_safe(curr_row, col):
                # Place queen
                self.solution.append((curr_row, col))
                self.top_row += 1
                
                # Update display
                self.draw_board()
                self.draw_queens()
                pygame.display.flip()
                time.sleep(self.animation_speed)

                # Recursively solve for next row
                if self.solve(curr_row + 1):
                    return True

                # If placing queen doesn't lead to a solution, backtrack
                self.solution.pop()
                self.top_row -= 1
                
                # Update display
                self.draw_board()
                self.draw_queens()
                pygame.display.flip()
                time.sleep(self.animation_speed)

        return False

    def run(self):
        """Run the GUI and solve the N-Queens problem"""
        running = True
        solved = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not solved:
                        solved = self.solve()
                        if solved:
                            print("Solution found!")
                        else:
                            print("No solution exists!")
                    elif event.key == pygame.K_r:  # Reset
                        self.solution = []
                        self.top_row = 0
                        solved = False
                        self.draw_board()
                        pygame.display.flip()

            # Draw the current state
            self.draw_board()
            self.draw_queens()
            
            # Draw instructions
            if not solved:
                text = self.font.render("Press SPACE to solve", True, self.BLACK)
            else:
                text = self.font.render("Press R to reset", True, self.BLACK)
            self.screen.blit(text, (10, 10))
            
            pygame.display.flip()

        pygame.quit()
        sys.exit()

def main():
    # Get input from user
    n = int(input("Enter N size (recommended 4-8): "))
    
    # Create and run GUI
    gui = NQueensGUI(n)
    gui.run()

if __name__ == "__main__":
    main() 