import numpy as np
import random

class QLearningAgent:

    def __init__(self):

        self.actions = [-1, 0, 1]  # remove, keep, add server
        self.q_table = {}

        self.learning_rate = 0.1
        self.discount = 0.9
        self.epsilon = 0.1

    def get_state(self, requests, servers):

        return (requests // 50, servers)

    def choose_action(self, state):

        if random.uniform(0,1) < self.epsilon:
            return random.choice(self.actions)

        if state not in self.q_table:
            self.q_table[state] = [0,0,0]

        return self.actions[np.argmax(self.q_table[state])]

    def update_q(self, state, action, reward, next_state):

        if state not in self.q_table:
            self.q_table[state] = [0,0,0]

        if next_state not in self.q_table:
            self.q_table[next_state] = [0,0,0]

        action_index = self.actions.index(action)

        best_future = max(self.q_table[next_state])

        self.q_table[state][action_index] += self.learning_rate * (
            reward + self.discount * best_future - self.q_table[state][action_index]
        )