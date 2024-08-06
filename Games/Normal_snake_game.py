import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Game settings
GRID_SIZE = 20
GRID_WIDTH = 60  # Increased to 60
GRID_HEIGHT = 30  # Increased to 30
WINDOW_WIDTH = GRID_SIZE * GRID_WIDTH
WINDOW_HEIGHT = GRID_SIZE * GRID_HEIGHT + 80  # Extra space for score
GAME_AREA_TOP = 80

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False
        self.color = GREEN

    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Check for collision with walls
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False
        
        # Check for collision with self
        if new_head in self.body:
            return False
        
        self.body.insert(0, new_head)
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

class Food:
    def __init__(self):
        self.position = self.get_random_position()
        self.color = RED

    def get_random_position(self):
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.Font(pygame.font.get_default_font(), 36)
        self.small_font = pygame.font.Font(pygame.font.get_default_font(), 24)
        
        self.reset_game()

    def reset_game(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.change_direction(UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction(RIGHT)
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_c and self.game_over:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_1:
                    self.snake.color = GREEN
                elif event.key == pygame.K_2:
                    self.snake.color = BLUE
                elif event.key == pygame.K_3:
                    self.snake.color = YELLOW
                elif event.key == pygame.K_4:
                    self.food.color = RED
                elif event.key == pygame.K_5:
                    self.food.color = PURPLE
                elif event.key == pygame.K_6:
                    self.food.color = WHITE

    def update(self):
        if not self.game_over:
            if not self.snake.move():
                self.game_over = True
            
            if self.snake.get_head() == self.food.position:
                self.snake.grow = True
                self.score += 10
                self.food = Food()

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw game border
        pygame.draw.rect(self.screen, WHITE, (0, GAME_AREA_TOP, WINDOW_WIDTH, WINDOW_HEIGHT - GAME_AREA_TOP), 2)
        
        # Draw score
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # Draw snake
        for segment in self.snake.body:
            pygame.draw.rect(self.screen, self.snake.color, 
                             (segment[0] * GRID_SIZE, 
                              segment[1] * GRID_SIZE + GAME_AREA_TOP, 
                              GRID_SIZE, GRID_SIZE))
        
        # Draw food
        pygame.draw.rect(self.screen, self.food.color, 
                         (self.food.position[0] * GRID_SIZE, 
                          self.food.position[1] * GRID_SIZE + GAME_AREA_TOP, 
                          GRID_SIZE, GRID_SIZE))

        if self.game_over:
            self.draw_end_screen()
        
        pygame.display.flip()

    def draw_end_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        message_text = self.font.render("GAME OVER", True, WHITE)
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