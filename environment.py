import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

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

SPEED = 200


class Environment:
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

        self.frame_iteration = 0

        self.reset()

    def reset(self):
        self.snake = Snake(self.fieldW//2, self.fieldH//2)
        self.food = Food(self.fieldW, self.fieldH, self.snake.head.x + 1, self.snake.head.y + 1)
        self.score = 0

        self.frame_iteration = 0

    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self.snake.move(action)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.snake.is_collision(self.fieldW, self.fieldH) or self.frame_iteration > 100 * len(self.snake.body):
            game_over = True
            reward = -10
            return reward, game_over

        # 4. place new food or just move
        if self.snake.head == self.food.pt:
            self.score += 1
            reward = 10
            while self.food.pt in self.snake.body:
                self.food.place_food()
        else:
            self.snake.body.pop()
        
        # 5. update ui and clock
        self.update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over

    def update_ui(self):
        self.display.fill(BLACK)

        pygame.draw.rect(self.display, BLUE2, pygame.Rect(self.snake.head.x * self.cellSize,
                                                          self.snake.head.y * self.cellSize,
                                                          self.cellSize, self.cellSize))
        for pt in self.snake.body[1:]:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x * self.cellSize, pt.y * self.cellSize,
                                                              self.cellSize, self.cellSize))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.pt.x * self.cellSize, self.food.pt.y * self.cellSize,
                                                        self.cellSize, self.cellSize))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


class Snake:
    def __init__(self, w, h):
        self.direction = Direction.RIGHT

        self.head = Point(w, h)
        self.body = [self.head, Point(self.head.x - 1, self.head.y), Point(self.head.x - 2, self.head.y)]

    def move(self, action):
        # [straight, right, left]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += 1
        elif self.direction == Direction.LEFT:
            x -= 1
        elif self.direction == Direction.DOWN:
            y += 1
        elif self.direction == Direction.UP:
            y -= 1

        self.head = Point(x, y)
        self.body.insert(0, self.head)

    def is_collision(self, w, h):
        # hits boundary
        if self.head.x > w - 1 or self.head.x < 0 or self.head.y > h - 1 or self.head.y < 0:
            return True
        # hits itself
        if self.head in self.body[1:]:  # TODO remove last element check
            return True
        return False

    def is_collide_with_something(self, list_of_something):
        if self.head.x in list_of_something:
            return True
        return False


class Food:
    def __init__(self, field_width, field_height, x, y):
        self.pt = Point(x, y)
        self.fieldW = field_width
        self.fieldH = field_height

    def place_food(self):
        self.pt = Point(random.randint(0, self.fieldW - 1), random.randint(0, self.fieldH - 1))
