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
        self.mode = "genetic"
        self.steps = []
        self.current_step = 0
        self.is_solving = False
        self.ga_generator = None  # Generator for GA steps
        
        # Genetic Algorithm parameters
        self.population_size = 20  # Reduced for faster convergence
        self.mutation_rate = 0.2   # Increased mutation rate
        self.elite_size = 2
        self.generations = 50      # Reduced generations
        self.current_generation = 0
        self.population = []
        self.best_fitness_history = []
        self.solution_found = False
        
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
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("4-Queens Genetic Algorithm Visualizer")
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
        self.board_x = (self.WINDOW_WIDTH - self.BOARD_SIZE) // 2
        self.board_y = 100
        self.genetic_rect = pygame.Rect(120, 700, 220, 54)
        self.solve_rect = pygame.Rect(370, 700, 180, 54)
        self.reset_rect = pygame.Rect(580, 700, 180, 54)
        self.prev_step_rect = pygame.Rect(120, 620, 220, 54)
        self.next_step_rect = pygame.Rect(580, 620, 220, 54)

    def count_attacks(self, state):
        attacks = 0
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                if state[i][0] == state[j][0]:
                    attacks += 1
                if abs(state[i][0] - state[j][0]) == abs(state[i][1] - state[j][1]):
                    attacks += 1
        return attacks

    def record_step(self, state, score, move_description=""):
        self.steps.append({
            'state': state.copy(),
            'score': score,
            'description': move_description
        })
        self.current_step = len(self.steps) - 1

    def fitness(self, state):
        return -self.count_attacks(state)

    def create_initial_population(self, seed_state=None):
        population = []
        if seed_state:
            population.append(seed_state)
        for _ in range(self.population_size - len(population)):
            state = [(random.randint(0, self.n-1), col) for col in range(self.n)]
            population.append(state)
        return population

    def select_parent(self, population):
        tournament_size = 3
        tournament = random.sample(population, tournament_size)
        return max(tournament, key=self.fitness)

    def crossover(self, parent1, parent2):
        crossover_point = random.randint(0, self.n-1)
        return parent1[:crossover_point] + parent2[crossover_point:]

    def mutate(self, state):
        if random.random() < self.mutation_rate:
            col = random.randint(0, self.n-1)
            new_row = random.randint(0, self.n-1)
            state[col] = (new_row, col)
        return state

    def genetic_algorithm(self):
        self.solution_found = False
        self.population = self.create_initial_population(seed_state=self.current_state.copy())
        self.current_generation = 0
        self.best_fitness_history = []
        self.steps = []
        
        # Initial evaluation
        initial_best = max([(state, self.fitness(state)) for state in self.population], key=lambda x: x[1])
        self.record_step(initial_best[0], initial_best[1], "Initial Population")
        self.current_state = initial_best[0]
        yield
        
        while self.current_generation < self.generations and not self.solution_found:
            fitness_scores = [(state, self.fitness(state)) for state in self.population]
            best_state = max(fitness_scores, key=lambda x: x[1])
            self.best_fitness_history.append(best_state[1])
            
            # Record current best state
            self.record_step(best_state[0], best_state[1], 
                           f"Generation {self.current_generation + 1}")
            self.current_state = best_state[0]
            
            if best_state[1] == 0:
                self.solution_found = True
                self.record_step(best_state[0], best_state[1], "Solution Found!")
                yield
                break
            
            # Create new population
            new_population = []
            sorted_pop = sorted(fitness_scores, key=lambda x: x[1], reverse=True)
            new_population.extend([s for s, _ in sorted_pop[:self.elite_size]])
            
            while len(new_population) < self.population_size:
                parent1 = self.select_parent(self.population)
                parent2 = self.select_parent(self.population)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            
            self.population = new_population
            self.current_generation += 1
            yield
        
        self.is_solving = False
        if self.solution_found:
            self.win_sound.play()

    def draw_board(self):
        pygame.draw.rect(self.screen, self.BOARD_BG, (self.board_x-8, self.board_y-8, self.BOARD_SIZE+16, self.BOARD_SIZE+16), border_radius=16)
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

    def draw_queen(self, row, col):
        img = pygame.image.load("./assets/n_queens/queen.png")
        img = pygame.transform.smoothscale(img, (self.CELL_SIZE-18, self.CELL_SIZE-18))
        x = self.board_x + col * self.CELL_SIZE + 9
        y = self.board_y + row * self.CELL_SIZE + 9
        self.screen.blit(img, (x, y))

    def draw_ui(self):
        self.screen.fill(self.BG_COLOR)
        title = self.font.render("4-Queens Genetic Algorithm", True, self.FONT_COLOR)
        self.screen.blit(title, (self.WINDOW_WIDTH//2 - title.get_width()//2, 30))
        self.draw_board()
        for row, col in self.current_state:
            self.draw_queen(row, col)
        self.draw_button("Genetic Algorithm", self.genetic_rect, True)
        self.draw_button("Solve", self.solve_rect, len(self.current_state) == self.n and not self.is_solving)
        self.draw_button("Reset", self.reset_rect, not self.is_solving)
        self.draw_button("Previous Step", self.prev_step_rect, self.current_step > 0 and not self.is_solving)
        self.draw_button("Next Step", self.next_step_rect, self.current_step < len(self.steps) - 1 and not self.is_solving)
        
        if self.steps:
            step = self.steps[self.current_step]
            y = self.board_y + self.BOARD_SIZE + 40
            texts = [
                f"Step {self.current_step + 1}/{len(self.steps)}",
                step['description'],
                f"Attacks: {-step['score']}"
            ]
            for text in texts:
                text_surf = self.small_font.render(text, True, self.FONT_COLOR)
                self.screen.blit(text_surf, (self.WINDOW_WIDTH//2 - text_surf.get_width()//2, y))
                y += 32

    def handle_click(self, pos):
        if self.is_solving:
            return
        if self.genetic_rect.collidepoint(pos):
            self.mode = "genetic"
        elif self.solve_rect.collidepoint(pos) and len(self.current_state) == self.n:
            self.ga_generator = self.genetic_algorithm()
            self.is_solving = True
        elif self.reset_rect.collidepoint(pos):
            self.current_state = []
            self.steps = []
            self.current_step = 0
            self.best_fitness_history = []
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

            # Process GA steps
            if self.is_solving and self.ga_generator:
                try:
                    next(self.ga_generator)
                except StopIteration:
                    self.is_solving = False
                    self.ga_generator = None

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