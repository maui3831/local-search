""" 
Enhanced N-Queens GUI with Chess.com-style interface and additional features
"""

import pygame
import sys
import time
import thorpy
import os
import threading

class NQueensGUI:
    def __init__(self, n):
        pygame.init()
        self.n = n
        self.solution = []
        self.steps = []
        self.current_step = 0
        self.mode = "auto"
        self.history = []
        self.conflicts = []
        
        # Window setup
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 800
        self.CELL_SIZE = 800 // n
        self.BOARD_SIZE = self.CELL_SIZE * n
        
        # Colors
        self.GREEN = (118, 150, 86)
        self.CREAM = (238, 238, 210)
        self.RED = (255, 0, 0, 100)
        self.BUTTON_COLOR = (74, 74, 74)
        
        # Initialize display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption(f"N-Queens Problem (N={n})")
        
        # Load assets
        self.load_assets()
        self.init_ui_elements()
        self.animation_speed = 0.5

    def load_assets(self):
        pygame.mixer.init()
        self.move_sound = pygame.mixer.Sound("./assets/n_queens/move.mp3")
        self.error_sound = pygame.mixer.Sound("./assets/n_queens/incorrect.mp3")
        self.win_sound = pygame.mixer.Sound("./assets/n_queens/finish.mp3")
        self.icon = pygame.image.load("./assets/n_queens/icon.png")
        pygame.display.set_icon(self.icon)

    def init_ui_elements(self):
        self.font = pygame.font.Font(None, 24)
        self.history_font = pygame.font.Font(None, 20)
        self.mode_auto_rect = pygame.Rect(820, 20, 100, 30)
        self.mode_manual_rect = pygame.Rect(820, 60, 100, 30)
        self.prev_rect = pygame.Rect(820, 100, 80, 30)
        self.next_rect = pygame.Rect(820, 140, 80, 30)
        self.highlight_surface = pygame.Surface((self.CELL_SIZE, self.CELL_SIZE), pygame.SRCALPHA)
        self.solve_rect = pygame.Rect(820, 180, 80, 30)

    def set_mode(self, mode):
        """Handle mode selection"""
        self.mode = mode
        self.mode_auto.set_value(mode == "auto")
        self.mode_manual.set_value(mode == "manual")
        self.reset_board()

    def mode_clicked(self, event):
        """Handle mode selection"""
        self.mode = event.el.get_value()
        self.reset_board()

    def draw_board(self):
        """Draw chess.com-style board with highlights"""
        self.screen.fill(self.CREAM, (0, 0, self.BOARD_SIZE, self.BOARD_SIZE))
        
        for row in range(self.n):
            for col in range(self.n):
                # Draw base board
                color = self.CREAM if (row + col) % 2 == 0 else self.GREEN
                rect = pygame.Rect(
                    col * self.CELL_SIZE,
                    row * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)
                
                # Draw highlights
                if (row, col) in self.conflicts:
                    self.highlight_surface.fill(self.RED)
                    self.screen.blit(self.highlight_surface, rect.topleft)
                    
    def draw_button(self, text, rect, enabled=True):
        """Draw a button with proper enabled/disabled states"""
        button_color = self.BUTTON_COLOR if enabled else (150, 150, 150)  # Grey when disabled
        text_color = (255, 255, 255) if enabled else (200, 200, 200)      # White text when enabled
        
        pygame.draw.rect(self.screen, button_color, rect)
        text_surf = self.font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_ui(self):
        """Draw all UI elements with proper solve button state"""
        # Determine solve button state
        solve_enabled = (
            (self.mode == "auto") or 
            (self.mode == "manual" and len(self.solution) == self.n)
        )
        
        # Draw buttons
        self.draw_button("Auto", self.mode_auto_rect, self.mode == "auto")
        self.draw_button("Manual", self.mode_manual_rect, self.mode == "manual")
        self.draw_button("Previous", self.prev_rect)
        self.draw_button("Next", self.next_rect)
        self.draw_button("Solve", self.solve_rect, solve_enabled)
        
        # History panel
        self.draw_history()

   

    def draw_history(self):
        """Draw move history panel"""
        y = 180
        for entry in self.history[-10:]:  # Show last 10 entries
            text_surf = self.history_font.render(entry, True, (0, 0, 0))
            self.screen.blit(text_surf, (820, y))
            y += 20

    def draw_queen(self, row, col):
        """Draw queen using image"""
        img = pygame.image.load("./assets/n_queens/queen.png")
        img = pygame.transform.scale(img, (self.CELL_SIZE-10, self.CELL_SIZE-10))
        x = col * self.CELL_SIZE + 5
        y = row * self.CELL_SIZE + 5
        self.screen.blit(img, (x, y))

    def handle_click(self, pos):
        """Handle clicks with proper solve button validation"""
        if self.mode_auto_rect.collidepoint(pos):
            self.mode = "auto"
            self.reset_board()
        elif self.mode_manual_rect.collidepoint(pos):
            self.mode = "manual"
            self.reset_board()
        elif self.prev_rect.collidepoint(pos):
            self.prev_step()
        elif self.next_rect.collidepoint(pos):
            self.next_step()
        elif self.solve_rect.collidepoint(pos):
            # Check if solve button is enabled
            solve_enabled = (
                (self.mode == "auto") or 
                (self.mode == "manual" and len(self.solution)) == self.n
            )
            if solve_enabled:
                self.solve()
        elif pos[0] < self.BOARD_SIZE and self.mode == "manual":
            self.handle_manual_placement(pos)

    def handle_manual_placement(self, pos):
        col = pos[0] // self.CELL_SIZE
        row = pos[1] // self.CELL_SIZE
        if self.is_safe(row, col):
            self.solution.append((row, col))
            self.record_step("Place", (row, col))
            self.move_sound.play()
        else:
            self.error_sound.play()
            self.flash_highlight(row, col)

    def solve(self):
        """Handle solving based on current mode"""
        if self.mode == "auto":
            # Start automatic solver
            self.reset_board()
            self.solving = True
            self.solve_thread = threading.Thread(target=self.backtrack_wrapper)
            self.solve_thread.start()
        else:
            # Validate manual solution
            if len(self.solution) == self.n:
                self.win_sound.play()
                self.flash_victory()
            else:
                self.error_sound.play()

    def flash_victory(self):
        """Visual feedback for correct solution"""
        for _ in range(3):
            self.screen.fill(self.GREEN, (0, 0, self.BOARD_SIZE, self.BOARD_SIZE))
            pygame.display.flip()
            time.sleep(0.2)
            self.draw_board()
            pygame.display.flip()
            time.sleep(0.2)

    def backtrack_wrapper(self):
        """Wrapper for backtracking to handle threading"""
        self.steps = []
        self.current_step = 0
        if self.backtrack(0):
            self.win_sound.play()
        self.solving = False

    def backtrack(self, row):
        if row == self.n:
            return True
            
        for col in range(self.n):
            if self.is_safe(row, col):
                self.solution.append((row, col))
                self.record_step("Place", (row, col))
                self.move_sound.play()
                
                # Update display without blocking
                pygame.event.post(pygame.event.Event(pygame.USEREVENT))
                time.sleep(self.animation_speed)
                
                if self.backtrack(row + 1):
                    return True
                
                self.solution.pop()
                self.record_step("Remove", (row, col))
                self.error_sound.play()
                
                # Update display without blocking
                pygame.event.post(pygame.event.Event(pygame.USEREVENT))
                time.sleep(self.animation_speed)
        
        return False

    def record_step(self, action, pos):
        """Record each step for history"""
        self.steps.append((action, pos, list(self.solution)))
        self.current_step = len(self.steps) - 1
        self.update_history()

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.solution = self.steps[self.current_step][2].copy()
            self.update_history()
            self.move_sound.play()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.solution = self.steps[self.current_step][2].copy()
            self.update_history()
            self.error_sound.play()

    def update_history(self):
        self.history = []
        for i, step in enumerate(self.steps):
            entry = f"Step {i+1}: {step[0]} {step[1]}"
            if i == self.current_step:
                entry = "▶ " + entry
            self.history.append(entry)

    def reset_board(self):
        """Reset the board to initial state"""
        self.solution = []
        self.steps = []
        self.current_step = 0
        self.draw_board()

    def run(self):
        """Main game loop with proper event handling"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.USEREVENT:  # Custom update event
                    pass  # Forces display update

            # Draw all elements
            self.draw_board()
            for row, col in self.solution:
                self.draw_queen(row, col)
            self.draw_ui()
            
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()


    def is_safe(self, row, col):
        """Check if placing a queen at (row, col) is safe (unchanged)"""
        for i in range(len(self.solution)):
            q_row, q_col = self.solution[i]
            if q_col == col or abs(q_row - row) == abs(q_col - col):
                return False
        return True

    def flash_highlight(self, row, col):
        """Non-blocking highlight animation"""
        start_time = time.time()
        while time.time() - start_time < 0.3:
            rect = pygame.Rect(col*self.CELL_SIZE, row*self.CELL_SIZE, 
                             self.CELL_SIZE, self.CELL_SIZE)
            self.screen.fill((255, 0, 0, 100), rect)
            pygame.display.update(rect)
            pygame.time.delay(50)

def main():
    n = int(input("Enter N size (4-8): "))
    if n < 4 or n > 8:
        print("Please enter a value between 4 and 8")
        return
    
    required_files = [
        "./assets/n_queens/move.mp3",
        "./assets/n_queens/incorrect.mp3",
        "./assets/n_queens/finish.mp3",
        "./assets/n_queens/queen.png"
    ]
    
    for f in required_files:
        if not os.path.exists(f):
            print(f"Missing required file: {f}")
            return

    gui = NQueensGUI(n)
    gui.run()

if __name__ == "__main__":
    main()