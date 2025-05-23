""" 
N-Queens GUI with Simulated Annealing and Size Selection - Improved Layout
"""

import pygame
import sys
import random
import math
import os

# For reproducibility
# random.seed(42)  

class NQueensGUI:
    def __init__(self):
        pygame.init()
        self.available_sizes = [4,5, 6,7, 8]
        self.n = 4  # Default size
        self.solution = []
        self.current_state = []
        self.mode = "annealing"
        self.steps = []
        self.current_step = 0
        self.is_solving = False
        self.annealing_generator = None
        self.is_fullscreen = False
        
        # Simulated Annealing parameters
        self.initial_temperature = 100.0
        self.cooling_rate = 0.95
        self.min_temperature = 0.1
        self.max_iterations = 200_000
        self.current_temperature = self.initial_temperature
        self.current_iteration = 0
        self.best_state = None
        self.best_energy = float('inf')
        
        # Dynamic sizing based on board size
        self.update_board_sizing()
        
        self.BG_COLOR = (245, 246, 250)
        self.BOARD_BG = (220, 220, 220)
        self.GREEN = (118, 150, 86)
        self.CREAM = (238, 238, 210)
        self.RED = (255, 0, 0, 100)
        self.BUTTON_COLOR = (52, 73, 94)
        self.BUTTON_HOVER = (41, 128, 185)
        self.BUTTON_DISABLED = (189, 195, 199)
        self.BUTTON_TEXT = (255, 255, 255)
        self.FONT_COLOR = (44, 62, 80)
        self.PANEL_BG = (230, 230, 230)
        self.SIZE_BUTTON_ACTIVE = (46, 204, 113)
        self.SIZE_BUTTON_INACTIVE = (149, 165, 166)
        
        self.WINDOW_WIDTH = 1600
        self.WINDOW_HEIGHT = 1000
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("N-Queens Simulated Annealing Visualizer")
        self.load_assets()
        self.init_ui_elements()

    def update_board_sizing(self):
        """Update board sizing based on current n value - now much larger"""
        # Make board much larger to utilize center-left space
        if self.n <= 4:
            self.CELL_SIZE = 140
        elif self.n <= 6:
            self.CELL_SIZE = 110
        else:
            self.CELL_SIZE = 80
        
        self.BOARD_SIZE = self.CELL_SIZE * self.n

    def load_assets(self):
        pygame.mixer.init()
        self.move_sound = pygame.mixer.Sound("./assets/n_queens/move.mp3")
        self.error_sound = pygame.mixer.Sound("./assets/n_queens/incorrect.mp3")
        self.win_sound = pygame.mixer.Sound("./assets/n_queens/finish.mp3")
        self.premove_sound = pygame.mixer.Sound("./assets/n_queens/premove.mp3")
        self.gameend_sound = pygame.mixer.Sound("./assets/n_queens/game-end.mp3")
        self.icon = pygame.image.load("./assets/n_queens/icon.png")
        pygame.display.set_icon(self.icon)

    def init_ui_elements(self):
        self.font = pygame.font.SysFont('Segoe UI', 36)
        self.small_font = pygame.font.SysFont('Segoe UI', 22)
        self.info_font = pygame.font.SysFont('Segoe UI', 18)
        self.size_font = pygame.font.SysFont('Segoe UI', 16)
        
        # Calculate safe margins based on screen size
        margin_left = 80
        margin_top = 120
        
        # Ensure board doesn't cover size buttons by adding extra top margin if needed
        min_board_y = margin_top + 40  # Space for size buttons + padding
        
        # Center-left board positioning with proper spacing
        self.board_x = margin_left
        self.board_y = max(min_board_y, (self.WINDOW_HEIGHT - self.BOARD_SIZE) // 2)
        
        # Ensure board doesn't go off screen
        if self.board_y + self.BOARD_SIZE > self.WINDOW_HEIGHT - 100:
            self.board_y = self.WINDOW_HEIGHT - self.BOARD_SIZE - 100
        
        # Right side panel - positioned relative to board
        self.panel_x = self.board_x + self.BOARD_SIZE + 80
        self.panel_y = self.board_y
        self.panel_width = min(280, self.WINDOW_WIDTH - self.panel_x - 40)  # Ensure panel fits
        self.panel_height = min(500, self.WINDOW_HEIGHT - self.panel_y - 200)  # Leave space for buttons
        
        # Size selection buttons (top of screen) - always at fixed position
        self.size_buttons = {}
        button_width = 70
        button_height = 35
        start_x = margin_left
        start_y = 60
        
        for i, size in enumerate(self.available_sizes):
            x = start_x + i * (button_width + 15)
            self.size_buttons[size] = pygame.Rect(x, start_y, button_width, button_height)
        
        # Control buttons - repositioned to right side in 2x2 grid
        button_width = 120
        button_height = 45
        buttons_start_x = self.panel_x + 20
        buttons_start_y = self.panel_y + self.panel_height + 30
        
        # Ensure buttons don't go off screen
        if buttons_start_y + button_height * 2 + 15 > self.WINDOW_HEIGHT - 50:
            buttons_start_y = self.WINDOW_HEIGHT - button_height * 2 - 65
        
        # Top row buttons
        self.solve_rect = pygame.Rect(buttons_start_x, buttons_start_y, button_width, button_height)
        self.reset_rect = pygame.Rect(buttons_start_x + button_width + 15, buttons_start_y, button_width, button_height)
        
        # Bottom row buttons
        self.prev_step_rect = pygame.Rect(buttons_start_x, buttons_start_y + button_height + 15, button_width, button_height)
        self.next_step_rect = pygame.Rect(buttons_start_x + button_width + 15, buttons_start_y + button_height + 15, button_width, button_height)
        
        # Fullscreen button (top right)
        self.fullscreen_rect = pygame.Rect(self.WINDOW_WIDTH - 120, 20, 100, 35)

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Get actual fullscreen dimensions
            info = pygame.display.Info()
            self.WINDOW_WIDTH = info.current_w
            self.WINDOW_HEIGHT = info.current_h
        else:
            self.WINDOW_WIDTH = 1600
            self.WINDOW_HEIGHT = 1000
            self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        
        # Reinitialize UI elements with new dimensions
        self.init_ui_elements()

    def count_attacks(self, state):
        """Count the number of pairs of queens that are attacking each other"""
        attacks = 0
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                # Check same row
                if state[i][0] == state[j][0]:
                    attacks += 1
                # Check diagonal
                if abs(state[i][0] - state[j][0]) == abs(state[i][1] - state[j][1]):
                    attacks += 1
        return attacks

    def get_random_neighbor(self, state):
        """Generate a random neighboring state by moving one queen"""
        new_state = state.copy()
        # Randomly select a queen to move
        queen_idx = random.randint(0, self.n-1)
        # Randomly select a new row for the queen
        new_row = random.randint(0, self.n-1)
        new_state[queen_idx] = (new_row, queen_idx)
        return new_state

    def record_step(self, state, energy, description=""):
        """Record a step in the solution process"""
        self.steps.append({
            'state': state.copy(),
            'energy': energy,
            'description': description
        })
        self.current_step = len(self.steps) - 1

    def simulated_annealing(self):
        """Solve N-Queens using simulated annealing"""
        self.is_solving = True
        self.steps = []
        self.current_temperature = self.initial_temperature
        self.current_iteration = 0
        self.best_state = self.current_state.copy()
        self.best_energy = self.count_attacks(self.best_state)
        
        # Record initial state
        self.record_step(self.best_state, self.best_energy, "Initial State")
        yield
        
        while (self.current_temperature > self.min_temperature and 
               self.current_iteration < self.max_iterations and 
               self.best_energy > 0):
            
            # Play premove sound during solving process (every 5th iteration to avoid spam)
            if self.current_iteration % 5 == 0:
                self.premove_sound.play()
            
            # Record temperature and iteration info
            self.record_step(self.current_state, self.best_energy,
                           f"Temperature: {self.current_temperature:.2f}, Iteration: {self.current_iteration}")
            yield
            
            # Generate neighbor
            neighbor = self.get_random_neighbor(self.current_state)
            neighbor_energy = self.count_attacks(neighbor)
            
            # Calculate energy difference
            energy_diff = neighbor_energy - self.best_energy
            
            # Accept if better or with probability based on temperature
            if energy_diff < 0 or random.random() < math.exp(-energy_diff / self.current_temperature):
                self.current_state = neighbor
                if neighbor_energy < self.best_energy:
                    self.best_state = neighbor.copy()
                    self.best_energy = neighbor_energy
                    # Play premove sound when finding better state
                    self.premove_sound.play()
                    self.record_step(self.best_state, self.best_energy,
                                   f"New Best State Found! Energy: {self.best_energy}")
                    yield
            
            # Cool down
            self.current_temperature *= self.cooling_rate
            self.current_iteration += 1
            
            # Record every 10th iteration
            if self.current_iteration % 10 == 0:
                self.record_step(self.current_state, self.best_energy,
                               f"Cooling Down - Temperature: {self.current_temperature:.2f}")
                yield
        
        # Record final state
        if self.best_energy == 0:
            self.record_step(self.best_state, self.best_energy, "Solution Found!")
            self.win_sound.play()
        else:
            self.record_step(self.best_state, self.best_energy, 
                           f"Best State Found (Energy: {self.best_energy})")
        
        # Always play game-end sound when solving process completes
        self.gameend_sound.play()
        self.is_solving = False
        yield

    def change_board_size(self, new_size):
        """Change the board size and reset the game"""
        if new_size == self.n or self.is_solving:
            return
        
        self.n = new_size
        self.update_board_sizing()
        self.init_ui_elements()  # Reinitialize UI elements with new sizing
        self.current_state = []
        self.steps = []
        self.current_step = 0
        self.move_sound.play()

    def draw_board(self):
        pygame.draw.rect(self.screen, self.BOARD_BG, 
                        (self.board_x-8, self.board_y-8, self.BOARD_SIZE+16, self.BOARD_SIZE+16), 
                        border_radius=16)
        for row in range(self.n):
            for col in range(self.n):
                color = self.CREAM if (row + col) % 2 == 0 else self.GREEN
                rect = pygame.Rect(
                    self.board_x + col * self.CELL_SIZE,
                    self.board_y + row * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )
                pygame.draw.rect(self.screen, color, rect, border_radius=8)

    def draw_queen(self, row, col):
        img = pygame.image.load("./assets/n_queens/queen.png")
        # Scale queen image based on cell size
        queen_size = max(30, self.CELL_SIZE - 20)
        img = pygame.transform.smoothscale(img, (queen_size, queen_size))
        x = self.board_x + col * self.CELL_SIZE + (self.CELL_SIZE - queen_size) // 2
        y = self.board_y + row * self.CELL_SIZE + (self.CELL_SIZE - queen_size) // 2
        self.screen.blit(img, (x, y))

    def draw_button(self, text, rect, enabled=True):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos)
        color = self.BUTTON_COLOR if enabled else self.BUTTON_DISABLED
        if enabled and is_hover:
            color = self.BUTTON_HOVER
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        text_surf = self.small_font.render(text, True, self.BUTTON_TEXT if enabled else (200, 200, 200))
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_size_buttons(self):
        """Draw the size selection buttons"""
        # Title for size selection
        size_title = self.info_font.render("Board Size:", True, self.FONT_COLOR)
        self.screen.blit(size_title, (80, 35))
        
        mouse_pos = pygame.mouse.get_pos()
        
        for size, rect in self.size_buttons.items():
            # Determine button color
            is_active = (size == self.n)
            is_hover = rect.collidepoint(mouse_pos) and not self.is_solving
            
            if is_active:
                color = self.SIZE_BUTTON_ACTIVE
            elif is_hover:
                color = self.BUTTON_HOVER
            else:
                color = self.SIZE_BUTTON_INACTIVE
            
            # Draw button
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            
            # Draw text
            text = f"{size}x{size}"
            text_color = self.BUTTON_TEXT if (is_active or is_hover) else self.FONT_COLOR
            text_surf = self.size_font.render(text, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)

    def draw_side_panel(self):
        # Draw panel background
        pygame.draw.rect(self.screen, self.PANEL_BG, 
                        (self.panel_x, self.panel_y, self.panel_width, self.panel_height),
                        border_radius=10)
        
        y = self.panel_y + 15
        # Title
        title = self.info_font.render("Simulated Annealing", True, self.FONT_COLOR)
        self.screen.blit(title, (self.panel_x + 15, y))
        y += 35

        # Current board info
        board_info = self.info_font.render(f"Board: {self.n}x{self.n}", True, self.FONT_COLOR)
        self.screen.blit(board_info, (self.panel_x + 15, y))
        y += 25

        # Parameters
        params = [
            f"Initial Temp: {self.initial_temperature}",
            f"Cooling Rate: {self.cooling_rate}",
            f"Min Temp: {self.min_temperature}",
            f"Max Iterations: {self.max_iterations}"
        ]
        
        for param in params:
            text = self.size_font.render(param, True, self.FONT_COLOR)
            self.screen.blit(text, (self.panel_x + 15, y))
            y += 20

        y += 15
        # Current state info
        if self.steps:
            step = self.steps[self.current_step]
            info = [
                f"Step: {self.current_step + 1}/{len(self.steps)}",
                f"Status: {step['description'][:25]}{'...' if len(step['description']) > 25 else ''}",
                f"Attacks: {step['energy']}"
            ]
            for text in info:
                text_surf = self.size_font.render(text, True, self.FONT_COLOR)
                self.screen.blit(text_surf, (self.panel_x + 15, y))
                y += 20

        # Current temperature and iteration
        if self.is_solving:
            y += 15
            current_info = [
                f"Current Temp: {self.current_temperature:.2f}",
                f"Iteration: {self.current_iteration}"
            ]
            for text in current_info:
                text_surf = self.size_font.render(text, True, self.FONT_COLOR)
                self.screen.blit(text_surf, (self.panel_x + 15, y))
                y += 20

        # Instructions
        y += 25
        instructions = [
            "Instructions:",
            "1. Select board size above",
            "2. Click squares to place queens",
            f"3. Place all {self.n} queens (one per column)",
            "4. Click 'Solve' to start annealing",
            "5. Use step buttons to review"
        ]
        
        for i, instruction in enumerate(instructions):
            font = self.size_font
            color = self.FONT_COLOR if i == 0 else (100, 100, 100)
            text_surf = font.render(instruction, True, color)
            if i == 0:
                y += 5
            self.screen.blit(text_surf, (self.panel_x + 15, y))
            y += 18

    def draw_ui(self):
        self.screen.fill(self.BG_COLOR)
        
        # Title
        title = self.font.render("N-Queens Simulated Annealing", True, self.FONT_COLOR)
        title_x = (self.WINDOW_WIDTH - title.get_width()) // 2
        self.screen.blit(title, (title_x, 20))
        
        # Fullscreen button
        self.draw_button("Fullscreen" if not self.is_fullscreen else "Windowed", self.fullscreen_rect, True)
        
        # Draw size selection buttons
        self.draw_size_buttons()
        
        # Draw board
        self.draw_board()
        for row, col in self.current_state:
            self.draw_queen(row, col)
            
        # Draw side panel
        self.draw_side_panel()
        
        # Draw control buttons in 2x2 grid on right side
        self.draw_button("Solve", self.solve_rect, len(self.current_state) == self.n and not self.is_solving)
        self.draw_button("Reset", self.reset_rect, not self.is_solving)
        self.draw_button("Prev Step", self.prev_step_rect, self.current_step > 0 and not self.is_solving)
        self.draw_button("Next Step", self.next_step_rect, self.current_step < len(self.steps) - 1 and not self.is_solving)

    def handle_click(self, pos):
        if self.is_solving:
            return
            
        # Check fullscreen button
        if self.fullscreen_rect.collidepoint(pos):
            self.toggle_fullscreen()
            return
            
        # Check size button clicks
        for size, rect in self.size_buttons.items():
            if rect.collidepoint(pos):
                self.change_board_size(size)
                return
        
        # Check control button clicks
        if self.solve_rect.collidepoint(pos) and len(self.current_state) == self.n:
            self.annealing_generator = self.simulated_annealing()
            self.is_solving = True
            self.premove_sound.play()
        elif self.reset_rect.collidepoint(pos):
            self.current_state = []
            self.steps = []
            self.current_step = 0
        elif self.prev_step_rect.collidepoint(pos) and self.current_step > 0:
            self.current_step -= 1
            self.current_state = self.steps[self.current_step]['state'].copy()
            self.premove_sound.play()
        elif self.next_step_rect.collidepoint(pos) and self.current_step < len(self.steps) - 1:
            # Check if this is the last step before incrementing
            if self.current_step == len(self.steps) - 2:  # Moving to the last step
                self.gameend_sound.play()
            else:
                self.premove_sound.play()
            self.current_step += 1
            self.current_state = self.steps[self.current_step]['state'].copy()
        elif (self.board_x <= pos[0] < self.board_x + self.BOARD_SIZE and
              self.board_y <= pos[1] < self.board_y + self.BOARD_SIZE):
            # Handle board clicks
            col = (pos[0] - self.board_x) // self.CELL_SIZE
            row = (pos[1] - self.board_y) // self.CELL_SIZE
            
            # Ensure click is within board bounds
            if 0 <= row < self.n and 0 <= col < self.n:
                if not any(q[1] == col for q in self.current_state) and len(self.current_state) < self.n:
                    self.current_state.append((row, col))
                    self.move_sound.play()

    def handle_keypress(self, key):
        """Handle keyboard shortcuts"""
        if key == pygame.K_F11 or key == pygame.K_F:
            self.toggle_fullscreen()
        elif key == pygame.K_ESCAPE and self.is_fullscreen:
            self.toggle_fullscreen()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.is_fullscreen:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            # Process annealing steps
            if self.is_solving and self.annealing_generator:
                try:
                    next(self.annealing_generator)
                except StopIteration:
                    self.is_solving = False
                    self.annealing_generator = None

            self.draw_ui()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

def main():
    required_files = [
        "./assets/n_queens/move.mp3",
        "./assets/n_queens/incorrect.mp3",
        "./assets/n_queens/finish.mp3",
        "./assets/n_queens/queen.png",
        "./assets/n_queens/premove.mp3",
        "./assets/n_queens/game-end.mp3"
    ]
    
    for f in required_files:
        if not os.path.exists(f):
            print(f"Missing required file: {f}")
            return

    gui = NQueensGUI()
    gui.run()

if __name__ == "__main__":
    main()