import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.SysFont('Arial', 25, bold=True)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

SPEED = 20


class SnakeGame:
    def __init__(self, window_width=640, window_height=480, cell_size=20):
        self.fieldW = window_width//cell_size
        self.fieldH = window_height//cell_size
        self.cellSize = cell_size
        # init display
        self.display = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        
        self.snake = None
        self.food = None
        self.score = 0

        self.direction = Direction.RIGHT
        
        self.reset()

    def reset(self):
        self.snake = [Point(self.fieldW//2, self.fieldH//2), Point(self.fieldW//2 - 1, self.fieldH//2), Point(self.fieldW//2 -2, self.fieldH//2)]
        self.place_food()
        self.score = 0
        
    def place_food(self):
        x = random.randint(0, self.fieldW)
        y = random.randint(0, self.fieldH)
        self.food = Point(x, y)
        if self.food in self.snake:
            self.place_food()
        
    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN
        
        # 2. move
        self.move(self.direction)
        
        # 3. check if game over
        game_over = False
        if self.is_collision(self.fieldW, self.fieldH):
            game_over = True
            return game_over, self.score
            
        # 4. place new food or just move
        if self.snake[0] == self.food:
            self.score += 1
            self.place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self.update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score
    
    def is_collision(self, w, h):
        # hits boundary
        if self.snake[0].x > w - 1 or self.snake[0].x < 0 or self.snake[0].y > h - 1 or self.snake[0].y < 0:
            return True
        # hits itself
        if self.snake[0] in self.snake[1:]:
            return True
        
        return False
        
    def update_ui(self):
        self.display.fill(BLACK)
        
        pygame.draw.rect(self.display, BLUE2, pygame.Rect(self.snake[0].x * self.cellSize,
                                                          self.snake[0].y * self.cellSize,
                                                          self.cellSize, self.cellSize))
        for pt in self.snake[1:]:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x * self.cellSize, pt.y * self.cellSize,
                                                              self.cellSize, self.cellSize))
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x * self.cellSize, self.food.y * self.cellSize,
                                                        self.cellSize, self.cellSize))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def move(self, direction):
        x = self.snake[0].x
        y = self.snake[0].y
        if direction == Direction.RIGHT:
            x += 1
        elif direction == Direction.LEFT:
            x -= 1
        elif direction == Direction.DOWN:
            y += 1
        elif direction == Direction.UP:
            y -= 1
            
        head = Point(x, y)
        self.snake.insert(0, head)
            

if __name__ == '__main__':
    game = SnakeGame()
    
    # game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            break
        
    print('Final Score', score)

    pygame.quit()
