import pygame
import random
import sys
from heapq import heappop, heappush
from collections import deque

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (0, 255, 100)
BLACK = (10, 10, 10)
GRAY = (30, 30, 30)
LIGHT_GREEN = (0, 200, 100)
BLUE = (0, 150, 255)

# Game settings
GRID_SIZE = 20
GRID_WIDTH = 60  # Doubled from 30 to 60
GRID_HEIGHT = 30
WINDOW_WIDTH = GRID_SIZE * GRID_WIDTH
WINDOW_HEIGHT = GRID_SIZE * GRID_HEIGHT + 80  # Extra space for score
GAME_AREA_TOP = 80

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
ALL_DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

class Snake:
    def __init__(self):
        self.body = deque([(GRID_WIDTH // 2, GRID_HEIGHT // 2)])
        self.direction = RIGHT
        self.grow = False
        self.ghost_trail = deque(maxlen=5)  # Store last 5 positions for ghost trail

    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Wrap around screen edges
        new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
        
        # Check for collision with self
        if new_head in list(self.body)[1:]:
            return False  # Game over
        
        self.ghost_trail.appendleft(self.body[-1])  # Add current tail to ghost trail
        self.body.appendleft(new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        return True

    def change_direction(self, new_direction):
        # Ensure the snake cannot reverse direction
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def get_head(self):
        return self.body[0]

class Apple:
    def __init__(self, snake):
        self.snake = snake
        self.position = self.get_random_position()

    def get_random_position(self):
        available_positions = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if (x, y) not in self.snake.body]
        if available_positions:
            return random.choice(available_positions)
        return None  # No available positions, game won

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Neon Snake")
        self.clock = pygame.time.Clock()
        
        # Use built-in Pygame font
        self.font = pygame.font.Font(pygame.font.get_default_font(), 36)
        self.small_font = pygame.font.Font(pygame.font.get_default_font(), 24)
        
        self.reset_game()

    def reset_game(self):
        self.snake = Snake()
        self.apple = Apple(self.snake)
        self.score = 0
        self.game_over = False
        self.game_won = False

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def astar(self, start, goal):
        open_set = []
        heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            _, current = heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for direction in ALL_DIRECTIONS:
                neighbor = ((current[0] + direction[0]) % GRID_WIDTH, (current[1] + direction[1]) % GRID_HEIGHT)
                if neighbor not in self.snake.body:
                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                        if neighbor not in [i[1] for i in open_set]:
                            heappush(open_set, (f_score[neighbor], neighbor))

        return []

    def find_safe_path(self):
        head = self.snake.get_head()
        path = self.astar(head, self.apple.position)

        if not path:
            # If no path is found, try to avoid immediate collision
            return self.avoid_collision_path()

        return path

    def avoid_collision_path(self):
        head = self.snake.get_head()
        possible_moves = [direction for direction in ALL_DIRECTIONS if self.is_safe_step((head[0] + direction[0], head[1] + direction[1]))]
        if possible_moves:
            return [(head[0] + direction[0], head[1] + direction[1]) for direction in possible_moves]
        return []

    def is_safe_step(self, step):
        # Check if the step is safe (i.e., it doesn't lead to a collision)
        step = (step[0] % GRID_WIDTH, step[1] % GRID_HEIGHT)  # Wrap around screen edges
        return step not in self.snake.body

    def update_snake_direction(self):
        head = self.snake.get_head()
        path = self.find_safe_path()

        if path:
            next_step = path[1] if len(path) > 1 else path[0]
            delta = ((next_step[0] - head[0] + GRID_WIDTH) % GRID_WIDTH, (next_step[1] - head[1] + GRID_HEIGHT) % GRID_HEIGHT)
            self.snake.change_direction(delta)
        else:
            # No valid path found; continue in current direction
            self.snake.change_direction(self.snake.direction)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (self.game_over or self.game_won):
                    self.reset_game()
                elif event.key == pygame.K_c and (self.game_over or self.game_won):
                    pygame.quit()
                    sys.exit()

    def update(self):
        if not self.game_over and not self.game_won:
            self.update_snake_direction()
            if not self.snake.move():
                self.game_over = True

            if self.snake.get_head() == self.apple.position:
                self.snake.grow = True
                self.score += 10
                new_apple = Apple(self.snake)
                if new_apple.position is None:
                    self.game_won = True
                else:
                    self.apple = new_apple

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw game border
        pygame.draw.rect(self.screen, BLUE, (0, GAME_AREA_TOP, WINDOW_WIDTH, WINDOW_HEIGHT - GAME_AREA_TOP), 2)
        
        # Draw score
        score_text = self.font.render(f"SCORE: {self.score}", True, BLUE)
        self.screen.blit(score_text, (20, 20))
        
        # Draw ghost trail
        for segment in self.snake.ghost_trail:
            pygame.draw.rect(self.screen, LIGHT_GREEN, 
                             (segment[0] * GRID_SIZE, 
                              segment[1] * GRID_SIZE + GAME_AREA_TOP, 
                              GRID_SIZE, GRID_SIZE))
        
        # Draw snake
        for segment in self.snake.body:
            pygame.draw.rect(self.screen, GREEN, 
                             (segment[0] * GRID_SIZE, 
                              segment[1] * GRID_SIZE + GAME_AREA_TOP, 
                              GRID_SIZE, GRID_SIZE))
        
        # Draw apple
        if self.apple.position:
            pygame.draw.circle(self.screen, RED, 
                               (self.apple.position[0] * GRID_SIZE + GRID_SIZE // 2, 
                                self.apple.position[1] * GRID_SIZE + GAME_AREA_TOP + GRID_SIZE // 2), 
                               GRID_SIZE // 2)

        # Draw grid
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, GAME_AREA_TOP), (x, WINDOW_HEIGHT))
        for y in range(GAME_AREA_TOP, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y))

        if self.game_over:
            self.draw_end_screen("GAME OVER")
        elif self.game_won:
            self.draw_end_screen("YOU WIN!")
        
        pygame.display.flip()

    def draw_end_screen(self, message):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        message_text = self.font.render(message, True, WHITE)
        restart_text = self.small_font.render("Press 'R' to Restart or 'C' to Close", True, WHITE)
        
        self.screen.blit(message_text, (WINDOW_WIDTH // 2 - message_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 30))

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(10)  # Adjust game speed here

if __name__ == "__main__":
    game = Game()
    game.run()