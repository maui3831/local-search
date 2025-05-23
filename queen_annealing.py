""" 
N-Queens GUI with Simulated Annealing
"""

import pygame
import sys
import random
import math
import os

class NQueensGUI:
    def __init__(self):
        pygame.init()
        self.n = 4  # Fixed to 4x4
        self.solution = []
        self.current_state = []
        self.mode = "annealing"
        self.steps = []
        self.current_step = 0
        self.is_solving = False
        self.annealing_generator = None
        
        # Simulated Annealing parameters
        self.initial_temperature = 100.0
        self.cooling_rate = 0.95
        self.min_temperature = 0.1
        self.max_iterations = 1000
        self.current_temperature = self.initial_temperature
        self.current_iteration = 0
        self.best_state = None
        self.best_energy = float('inf')
        
        self.CELL_SIZE = 120
        self.BOARD_SIZE = self.CELL_SIZE * self.n
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
        self.WINDOW_WIDTH = 1200
        self.WINDOW_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("4-Queens Simulated Annealing Visualizer")
        self.load_assets()
        self.init_ui_elements()

    def load_assets(self):
        pygame.mixer.init()
        self.move_sound = pygame.mixer.Sound("./assets/n_queens/move.mp3")
        self.error_sound = pygame.mixer.Sound("./assets/n_queens/incorrect.mp3")
        self.win_sound = pygame.mixer.Sound("./assets/n_queens/finish.mp3")
        self.icon = pygame.image.load("./assets/n_queens/icon.png")
        pygame.display.set_icon(self.icon)

    def init_ui_elements(self):
        self.font = pygame.font.SysFont('Segoe UI', 36)
        self.small_font = pygame.font.SysFont('Segoe UI', 24)
        self.info_font = pygame.font.SysFont('Segoe UI', 20)
        # Center board
        self.board_x = 100
        self.board_y = 100
        # Side panel
        self.panel_x = self.board_x + self.BOARD_SIZE + 50
        self.panel_y = self.board_y
        self.panel_width = 300
        self.panel_height = self.BOARD_SIZE
        # Buttons
        self.annealing_rect = pygame.Rect(100, 700, 220, 54)
        self.solve_rect = pygame.Rect(350, 700, 180, 54)
        self.reset_rect = pygame.Rect(550, 700, 180, 54)
        self.prev_step_rect = pygame.Rect(100, 620, 220, 54)
        self.next_step_rect = pygame.Rect(550, 620, 220, 54)

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
        
        self.is_solving = False
        yield

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
        img = pygame.transform.smoothscale(img, (self.CELL_SIZE-18, self.CELL_SIZE-18))
        x = self.board_x + col * self.CELL_SIZE + 9
        y = self.board_y + row * self.CELL_SIZE + 9
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

    def draw_side_panel(self):
        # Draw panel background
        pygame.draw.rect(self.screen, self.PANEL_BG, 
                        (self.panel_x, self.panel_y, self.panel_width, self.panel_height),
                        border_radius=10)
        
        y = self.panel_y + 20
        # Title
        title = self.info_font.render("Simulated Annealing Info", True, self.FONT_COLOR)
        self.screen.blit(title, (self.panel_x + 20, y))
        y += 40

        # Parameters
        params = [
            f"Initial Temp: {self.initial_temperature}",
            f"Cooling Rate: {self.cooling_rate}",
            f"Min Temp: {self.min_temperature}",
            f"Max Iterations: {self.max_iterations}"
        ]
        
        for param in params:
            text = self.info_font.render(param, True, self.FONT_COLOR)
            self.screen.blit(text, (self.panel_x + 20, y))
            y += 30

        y += 20
        # Current state info
        if self.steps:
            step = self.steps[self.current_step]
            info = [
                f"Step: {self.current_step + 1}/{len(self.steps)}",
                f"Status: {step['description']}",
                f"Attacks: {step['energy']}"
            ]
            for text in info:
                text_surf = self.info_font.render(text, True, self.FONT_COLOR)
                self.screen.blit(text_surf, (self.panel_x + 20, y))
                y += 30

        # Current temperature and iteration
        if self.is_solving:
            y += 20
            current_info = [
                f"Current Temp: {self.current_temperature:.2f}",
                f"Iteration: {self.current_iteration}"
            ]
            for text in current_info:
                text_surf = self.info_font.render(text, True, self.FONT_COLOR)
                self.screen.blit(text_surf, (self.panel_x + 20, y))
                y += 30

    def draw_ui(self):
        self.screen.fill(self.BG_COLOR)
        # Title
        title = self.font.render("4-Queens Simulated Annealing", True, self.FONT_COLOR)
        self.screen.blit(title, (self.WINDOW_WIDTH//2 - title.get_width()//2, 30))
        
        # Draw board
        self.draw_board()
        for row, col in self.current_state:
            self.draw_queen(row, col)
            
        # Draw side panel
        self.draw_side_panel()
        
        # Draw buttons
        self.draw_button("Simulated Annealing", self.annealing_rect, True)
        self.draw_button("Solve", self.solve_rect, len(self.current_state) == self.n and not self.is_solving)
        self.draw_button("Reset", self.reset_rect, not self.is_solving)
        self.draw_button("Previous Step", self.prev_step_rect, self.current_step > 0 and not self.is_solving)
        self.draw_button("Next Step", self.next_step_rect, self.current_step < len(self.steps) - 1 and not self.is_solving)

    def handle_click(self, pos):
        if self.is_solving:
            return
        if self.annealing_rect.collidepoint(pos):
            self.mode = "annealing"
        elif self.solve_rect.collidepoint(pos) and len(self.current_state) == self.n:
            self.annealing_generator = self.simulated_annealing()
            self.is_solving = True
        elif self.reset_rect.collidepoint(pos):
            self.current_state = []
            self.steps = []
            self.current_step = 0
        elif self.prev_step_rect.collidepoint(pos) and self.current_step > 0:
            self.current_step -= 1
            self.current_state = self.steps[self.current_step]['state'].copy()
        elif self.next_step_rect.collidepoint(pos) and self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.current_state = self.steps[self.current_step]['state'].copy()
        elif (self.board_x <= pos[0] < self.board_x + self.BOARD_SIZE and
              self.board_y <= pos[1] < self.board_y + self.BOARD_SIZE):
            col = (pos[0] - self.board_x) // self.CELL_SIZE
            row = (pos[1] - self.board_y) // self.CELL_SIZE
            if not any(q[1] == col for q in self.current_state) and len(self.current_state) < self.n:
                self.current_state.append((row, col))
                self.move_sound.play()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
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
        "./assets/n_queens/queen.png"
    ]
    
    for f in required_files:
        if not os.path.exists(f):
            print(f"Missing required file: {f}")
            return

    gui = NQueensGUI()
    gui.run()

if __name__ == "__main__":
    main() 