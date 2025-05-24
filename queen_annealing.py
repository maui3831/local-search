""" 
N-Queens GUI with Simulated Annealing and Size Selection - Responsive Layout
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
        
        # Get system screen info for responsive design
        info = pygame.display.Info()
        self.system_width = info.current_w
        self.system_height = info.current_h
        
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
        
        # Set initial window size based on system resolution
        self.setup_window_size()
        
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
        
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("N-Queens Simulated Annealing Visualizer")
        
        # Dynamic sizing based on board size and screen
        self.update_board_sizing()
        self.load_assets()
        self.init_ui_elements()

    def setup_window_size(self):
        """Setup window size based on system resolution"""
        # Calculate optimal window size (80% of screen with reasonable limits)
        optimal_width = min(1600, int(self.system_width * 0.8))
        optimal_height = min(1000, int(self.system_height * 0.8))
        
        # Ensure minimum usable size
        self.WINDOW_WIDTH = max(1000, optimal_width)
        self.WINDOW_HEIGHT = max(700, optimal_height)
        
        # For very small screens, use most of the available space
        if self.system_width < 1200 or self.system_height < 800:
            self.WINDOW_WIDTH = min(self.system_width - 100, 1200)
            self.WINDOW_HEIGHT = min(self.system_height - 100, 900)

    def update_board_sizing(self):
        """Update board sizing based on current n value and available space"""
        # Calculate available space for board (considering UI elements)
        available_width = self.WINDOW_WIDTH - 400  # Reserve space for panel and margins
        available_height = self.WINDOW_HEIGHT - 200  # Reserve space for title and buttons
        
        # Calculate max cell size based on available space
        max_cell_size_by_width = available_width // self.n
        max_cell_size_by_height = available_height // self.n
        max_cell_size = min(max_cell_size_by_width, max_cell_size_by_height)
        
        # Set reasonable bounds for cell size
        if self.n <= 4:
            preferred_size = min(120, max_cell_size)
        elif self.n <= 6:
            preferred_size = min(90, max_cell_size)
        else:
            preferred_size = min(70, max_cell_size)
        
        # Ensure minimum playable size
        self.CELL_SIZE = max(40, preferred_size)
        self.BOARD_SIZE = self.CELL_SIZE * self.n

    def load_assets(self):
        pygame.mixer.init()
        try:
            self.move_sound = pygame.mixer.Sound("./assets/n_queens/move.mp3")
            self.error_sound = pygame.mixer.Sound("./assets/n_queens/incorrect.mp3")
            self.win_sound = pygame.mixer.Sound("./assets/n_queens/finish.mp3")
            self.premove_sound = pygame.mixer.Sound("./assets/n_queens/premove.mp3")
            self.gameend_sound = pygame.mixer.Sound("./assets/n_queens/game-end.mp3")
            self.icon = pygame.image.load("./assets/n_queens/icon.png")
            pygame.display.set_icon(self.icon)
        except:
            # Create dummy sounds if assets not found
            self.move_sound = None
            self.error_sound = None
            self.win_sound = None
            self.premove_sound = None
            self.gameend_sound = None

    def init_ui_elements(self):
        """Initialize UI elements with responsive positioning"""
        # Scale fonts based on window size
        base_scale = min(self.WINDOW_WIDTH / 1600, self.WINDOW_HEIGHT / 1000)
        
        self.font = pygame.font.SysFont('Segoe UI', max(24, int(36 * base_scale)))
        self.small_font = pygame.font.SysFont('Segoe UI', max(16, int(22 * base_scale)))
        self.info_font = pygame.font.SysFont('Segoe UI', max(14, int(18 * base_scale)))
        self.size_font = pygame.font.SysFont('Segoe UI', max(12, int(16 * base_scale)))
        
        # Calculate responsive margins
        margin_left = max(20, int(self.WINDOW_WIDTH * 0.05))
        margin_top = max(80, int(self.WINDOW_HEIGHT * 0.08))
        
        # Board positioning - center-left with proper spacing
        board_area_width = self.WINDOW_WIDTH * 0.6  # 60% of width for board area
        self.board_x = margin_left
        self.board_y = margin_top + 60  # Space for size buttons
        
        # Ensure board fits in allocated space
        if self.board_x + self.BOARD_SIZE > board_area_width:
            self.board_x = max(margin_left, int(board_area_width - self.BOARD_SIZE) // 2)
        
        # Vertically center the board in available space
        available_board_height = self.WINDOW_HEIGHT - self.board_y - 100
        if available_board_height > self.BOARD_SIZE:
            self.board_y += (available_board_height - self.BOARD_SIZE) // 2
        
        # Right side panel - responsive positioning
        panel_margin = max(20, int(self.WINDOW_WIDTH * 0.02))
        self.panel_x = max(self.board_x + self.BOARD_SIZE + panel_margin, 
                          int(self.WINDOW_WIDTH * 0.62))
        self.panel_y = self.board_y
        self.panel_width = min(300, self.WINDOW_WIDTH - self.panel_x - panel_margin)
        self.panel_height = min(self.BOARD_SIZE, 
                               self.WINDOW_HEIGHT - self.panel_y - 150)  # Leave space for buttons
        
        # Size selection buttons - responsive layout
        self.size_buttons = {}
        button_width = max(50, int(self.WINDOW_WIDTH * 0.04))
        button_height = max(30, int(self.WINDOW_HEIGHT * 0.035))
        buttons_per_row = min(len(self.available_sizes), 
                             int((board_area_width - margin_left) // (button_width + 15)))
        
        start_x = margin_left
        start_y = margin_top
        
        for i, size in enumerate(self.available_sizes):
            row = i // buttons_per_row
            col = i % buttons_per_row
            x = start_x + col * (button_width + 15)
            y = start_y + row * (button_height + 10)
            self.size_buttons[size] = pygame.Rect(x, y, button_width, button_height)
        
        # Control buttons - responsive 2x2 grid
        button_width = max(80, min(120, int(self.panel_width * 0.4)))
        button_height = max(35, int(self.WINDOW_HEIGHT * 0.04))
        button_spacing = max(10, int(self.panel_width * 0.05))
        
        buttons_start_x = self.panel_x + (self.panel_width - button_width * 2 - button_spacing) // 2
        buttons_start_y = self.panel_y + self.panel_height + 20
        
        # Ensure buttons don't go off screen
        if buttons_start_y + button_height * 2 + button_spacing > self.WINDOW_HEIGHT - 20:
            buttons_start_y = self.WINDOW_HEIGHT - button_height * 2 - button_spacing - 20
        
        # Top row buttons
        self.solve_rect = pygame.Rect(buttons_start_x, buttons_start_y, 
                                     button_width, button_height)
        self.reset_rect = pygame.Rect(buttons_start_x + button_width + button_spacing, 
                                     buttons_start_y, button_width, button_height)
        
        # Bottom row buttons
        self.prev_step_rect = pygame.Rect(buttons_start_x, 
                                         buttons_start_y + button_height + button_spacing, 
                                         button_width, button_height)
        self.next_step_rect = pygame.Rect(buttons_start_x + button_width + button_spacing, 
                                         buttons_start_y + button_height + button_spacing, 
                                         button_width, button_height)
        
        # Fullscreen button (top right) - responsive
        fs_width = max(80, int(self.WINDOW_WIDTH * 0.08))
        fs_height = max(30, int(self.WINDOW_HEIGHT * 0.035))
        self.fullscreen_rect = pygame.Rect(self.WINDOW_WIDTH - fs_width - 20, 20, 
                                          fs_width, fs_height)

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
            self.setup_window_size()
            self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        
        # Reinitialize UI elements with new dimensions
        self.update_board_sizing()
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

    def play_sound(self, sound):
        """Safely play sound if available"""
        if sound:
            try:
                sound.play()
            except:
                pass

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
                self.play_sound(self.premove_sound)
            
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
                    self.play_sound(self.premove_sound)
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
            self.play_sound(self.win_sound)
        else:
            self.record_step(self.best_state, self.best_energy, 
                           f"Best State Found (Energy: {self.best_energy})")
        
        # Always play game-end sound when solving process completes
        self.play_sound(self.gameend_sound)
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
        self.play_sound(self.move_sound)

    def draw_board(self):
        # Draw board background with responsive border
        border_size = max(4, int(self.CELL_SIZE * 0.1))
        pygame.draw.rect(self.screen, self.BOARD_BG, 
                        (self.board_x - border_size, self.board_y - border_size, 
                         self.BOARD_SIZE + border_size * 2, self.BOARD_SIZE + border_size * 2), 
                        border_radius=max(8, border_size * 2))
        
        for row in range(self.n):
            for col in range(self.n):
                color = self.CREAM if (row + col) % 2 == 0 else self.GREEN
                rect = pygame.Rect(
                    self.board_x + col * self.CELL_SIZE,
                    self.board_y + row * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )
                pygame.draw.rect(self.screen, color, rect, 
                               border_radius=max(4, int(self.CELL_SIZE * 0.1)))

    def draw_queen(self, row, col):
        # Draw queen using image for better appearance
        img = pygame.image.load("./assets/n_queens/queen.png")
        img = pygame.transform.scale(img, (self.CELL_SIZE-10, self.CELL_SIZE-10))
        x = self.board_x + col * self.CELL_SIZE + 5
        y = self.board_y + row * self.CELL_SIZE + 5
        self.screen.blit(img, (x, y))

    def draw_button(self, text, rect, enabled=True):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos)
        color = self.BUTTON_COLOR if enabled else self.BUTTON_DISABLED
        if enabled and is_hover:
            color = self.BUTTON_HOVER
        
        border_radius = max(6, int(min(rect.width, rect.height) * 0.15))
        pygame.draw.rect(self.screen, color, rect, border_radius=border_radius)
        
        # Scale text to fit button
        font_size = max(12, min(rect.height // 2, rect.width // len(text) * 2))
        temp_font = pygame.font.SysFont('Segoe UI', font_size)
        text_surf = temp_font.render(text, True, self.BUTTON_TEXT if enabled else (200, 200, 200))
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_size_buttons(self):
        """Draw the size selection buttons"""
        # Title for size selection
        size_title = self.info_font.render("Board Size:", True, self.FONT_COLOR)
        self.screen.blit(size_title, (self.size_buttons[self.available_sizes[0]].x, 
                                     self.size_buttons[self.available_sizes[0]].y - 25))
        
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
            border_radius = max(4, int(min(rect.width, rect.height) * 0.2))
            pygame.draw.rect(self.screen, color, rect, border_radius=border_radius)
            
            # Draw text
            text = f"{size}x{size}"
            text_color = self.BUTTON_TEXT if (is_active or is_hover) else self.FONT_COLOR
            font_size = max(10, min(rect.height // 2, rect.width // 4))
            temp_font = pygame.font.SysFont('Segoe UI', font_size)
            text_surf = temp_font.render(text, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)

    def draw_side_panel(self):
        # Draw panel background
        border_radius = max(8, int(min(self.panel_width, self.panel_height) * 0.02))
        pygame.draw.rect(self.screen, self.PANEL_BG, 
                        (self.panel_x, self.panel_y, self.panel_width, self.panel_height),
                        border_radius=border_radius)
        
        y = self.panel_y + 15
        line_height = max(18, int(self.panel_height * 0.04))
        
        # Title
        title = self.info_font.render("Simulated Annealing", True, self.FONT_COLOR)
        self.screen.blit(title, (self.panel_x + 15, y))
        y += line_height + 10

        # Current board info
        board_info = self.info_font.render(f"Board: {self.n}x{self.n}", True, self.FONT_COLOR)
        self.screen.blit(board_info, (self.panel_x + 15, y))
        y += line_height + 5

        # Parameters (abbreviated for smaller screens)
        params = [
            f"Initial Temp: {self.initial_temperature}",
            f"Cooling: {self.cooling_rate}",
            f"Min Temp: {self.min_temperature}",
            f"Max Iter: {self.max_iterations}"
        ]
        
        for param in params:
            text = self.size_font.render(param, True, self.FONT_COLOR)
            self.screen.blit(text, (self.panel_x + 15, y))
            y += line_height - 2

        y += 10
        # Current state info
        if self.steps:
            step = self.steps[self.current_step]
            max_desc_length = max(20, self.panel_width // 8)  # Adaptive description length
            desc = step['description'][:max_desc_length]
            if len(step['description']) > max_desc_length:
                desc += '...'
                
            info = [
                f"Step: {self.current_step + 1}/{len(self.steps)}",
                f"Status: {desc}",
                f"Attacks: {step['energy']}"
            ]
            for text in info:
                text_surf = self.size_font.render(text, True, self.FONT_COLOR)
                self.screen.blit(text_surf, (self.panel_x + 15, y))
                y += line_height - 2

        # Current temperature and iteration
        if self.is_solving:
            y += 10
            current_info = [
                f"Temp: {self.current_temperature:.2f}",
                f"Iter: {self.current_iteration}"
            ]
            for text in current_info:
                text_surf = self.size_font.render(text, True, self.FONT_COLOR)
                self.screen.blit(text_surf, (self.panel_x + 15, y))
                y += line_height - 2

        # Instructions (compact for smaller screens)
        if y < self.panel_y + self.panel_height - 100:  # Only show if space available
            y += 15
            instructions = [
                "Instructions:",
                "1. Select board size",
                "2. Click to place queens",
                f"3. Place all {self.n} queens",
                "4. Click 'Solve'",
                "5. Use step buttons"
            ]
            
            for i, instruction in enumerate(instructions):
                color = self.FONT_COLOR if i == 0 else (100, 100, 100)
                text_surf = self.size_font.render(instruction, True, color)
                if y + line_height > self.panel_y + self.panel_height - 20:
                    break  # Stop if running out of space
                self.screen.blit(text_surf, (self.panel_x + 15, y))
                y += line_height - 3

    def draw_ui(self):
        self.screen.fill(self.BG_COLOR)
        
        # Title - responsive positioning
        title = self.font.render("N-Queens Simulated Annealing", True, self.FONT_COLOR)
        title_x = (self.WINDOW_WIDTH - title.get_width()) // 2
        self.screen.blit(title, (title_x, 20))
        
        # Fullscreen button
        fs_text = "Full" if not self.is_fullscreen else "Win"
        self.draw_button(fs_text, self.fullscreen_rect, True)
        
        # Draw size selection buttons
        self.draw_size_buttons()
        
        # Draw board
        self.draw_board()
        for row, col in self.current_state:
            self.draw_queen(row, col)
            
        # Draw side panel
        self.draw_side_panel()
        
        # Draw control buttons
        self.draw_button("Solve", self.solve_rect, len(self.current_state) == self.n and not self.is_solving)
        self.draw_button("Reset", self.reset_rect, not self.is_solving)
        self.draw_button("Prev", self.prev_step_rect, self.current_step > 0 and not self.is_solving)
        self.draw_button("Next", self.next_step_rect, self.current_step < len(self.steps) - 1 and not self.is_solving)

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
            self.play_sound(self.premove_sound)
        elif self.reset_rect.collidepoint(pos):
            self.current_state = []
            self.steps = []
            self.current_step = 0
        elif self.prev_step_rect.collidepoint(pos) and self.current_step > 0:
            self.current_step -= 1
            self.current_state = self.steps[self.current_step]['state'].copy()
            self.play_sound(self.premove_sound)
        elif self.next_step_rect.collidepoint(pos) and self.current_step < len(self.steps) - 1:
            # Check if this is the last step before incrementing
            if self.current_step == len(self.steps) - 2:  # Moving to the last step
                self.play_sound(self.gameend_sound)
            else:
                self.play_sound(self.premove_sound)
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
                    self.play_sound(self.move_sound)

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
    
    missing_files = []
    for f in required_files:
        if not os.path.exists(f):
            missing_files.append(f)
    
    if missing_files:
        print("Warning: Missing asset files (will use fallbacks):")
        for f in missing_files:
            print(f"  - {f}")
        print("The application will still work but without sounds/custom queen image.")

    gui = NQueensGUI()
    gui.run()

if __name__ == "__main__":
    main()