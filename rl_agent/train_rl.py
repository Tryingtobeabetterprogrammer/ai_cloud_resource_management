import random
from rl_agent.q_learning_agent import QLearningAgent

agent = QLearningAgent()

servers = 2
server_capacity = 50

for episode in range(1000):

    requests = random.randint(10,200)

    state = agent.get_state(requests, servers)

    action = agent.choose_action(state)

    servers = max(1, servers + action)

    capacity = servers * server_capacity

    if capacity >= requests:
        reward = 10
    else:
        reward = -10

    next_state = agent.get_state(requests, servers)

    agent.update_q(state, action, reward, next_state)

print("Training complete")