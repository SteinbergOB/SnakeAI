import torch
import random
import numpy as np
from collections import deque
from environment import Environment, Direction, Point
from model import LinearQNet, QTrainer
from statistics import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.net = LinearQNet(11, 256, 3)
        self.trainer = QTrainer(self.net, lr=LR, gamma=self.gamma)
        self.env = Environment()

        self.plot_scores = []
        self.plot_mean_scores = []
        self.total_score = 0
        self.mean_score = 0
        self.record = 0

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, next_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_state(self):
        snake = self.env.snake
        food = self.env.food.pt
        point_l = Point(snake.head.x - 20, snake.head.y)
        point_r = Point(snake.head.x + 20, snake.head.y)
        point_u = Point(snake.head.x, snake.head.y - 20)
        point_d = Point(snake.head.x, snake.head.y + 20)

        dir_l = snake.direction == Direction.LEFT
        dir_r = snake.direction == Direction.RIGHT
        dir_u = snake.direction == Direction.UP
        dir_d = snake.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and snake.is_collide_with_something([point_r])) or
            (dir_l and snake.is_collide_with_something([point_l])) or
            (dir_u and snake.is_collide_with_something([point_u])) or
            (dir_d and snake.is_collide_with_something([point_d])),

            # Danger right
            (dir_u and snake.is_collide_with_something([point_r])) or
            (dir_d and snake.is_collide_with_something([point_l])) or
            (dir_l and snake.is_collide_with_something([point_u])) or
            (dir_r and snake.is_collide_with_something([point_d])),

            # Danger left
            (dir_d and snake.is_collide_with_something([point_r])) or
            (dir_u and snake.is_collide_with_something([point_l])) or
            (dir_r and snake.is_collide_with_something([point_u])) or
            (dir_l and snake.is_collide_with_something([point_d])),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            food.x < snake.head.x,  # food left
            food.x > snake.head.x,  # food right
            food.y < snake.head.y,  # food up
            food.y > snake.head.y  # food down
        ]

        return np.array(state, dtype=int)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        action = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            action[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.net(state0)
            move = torch.argmax(prediction).item()
            action[move] = 1

        return action

    def train(self):
        while True:
            # get old state
            state_old = self.get_state()

            # get move
            action_old = self.get_action(state_old)

            # perform move and get new state
            reward, done = self.env.change_all(action_old)
            state_new = self.get_state()

            # train short memory
            self.train_short_memory(state_old, action_old, reward, state_new, done)

            # remember
            self.remember(state_old, action_old, reward, state_new, done)

            if done:
                # train long memory, plot result
                self.n_games += 1
                self.train_long_memory()

                if self.env.score > self.record:
                    self.record = self.env.score
                    self.net.save()

                print('Game', self.n_games, 'Score', self.env.score, 'Record:', self.record)

                self.plot_scores.append(self.env.score)
                self.total_score += self.env.score
                self.mean_score = self.total_score / self.n_games
                self.plot_mean_scores.append(self.mean_score)
                plot(self.plot_scores, self.plot_mean_scores)
                self.env.reset()


if __name__ == '__main__':
    agent = Agent()

    agent.train()
