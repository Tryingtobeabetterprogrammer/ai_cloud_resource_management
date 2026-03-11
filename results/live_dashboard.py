import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json
import os

server_capacity = 50
sla_margin = 20

requests_history = []
capacity_history = []
servers_history = []
time_steps = []

sla_violations_x = []
sla_violations_y = []

fig, ax = plt.subplots()
ax2 = ax.twinx()

def update(frame):

    global time_steps, requests_history, capacity_history, servers_history

    # if server hasn't started yet
    if not os.path.exists("results/metrics.json"):
        return

    with open("results/metrics.json") as f:
        data = json.load(f)

    t = data["time"]
    requests = data["requests"]
    servers = data["servers"]
    capacity = data["capacity"]

    if len(time_steps) > 0 and t <= time_steps[-1]:
        return

    # store history
    time_steps.append(t)
    requests_history.append(requests)
    capacity_history.append(capacity)
    servers_history.append(servers)

    # SLA violation check
    if capacity < requests + sla_margin:
        sla_violations_x.append(t)
        sla_violations_y.append(requests)

    ax.clear()
    ax2.clear()

    sla_limit = 150
    sla_line = [sla_limit for _ in time_steps]

    ax.plot(time_steps, requests_history, label="Requests")
    ax.plot(time_steps, capacity_history, label="Capacity")
    ax.plot(time_steps, sla_line, linestyle="--", label="SLA Limit")

    ax2.plot(time_steps, servers_history, color="green", label="Servers")

    ax.scatter(sla_violations_x, sla_violations_y, color="red", label="SLA Violation")

    ax.set_title("AI Cloud Autoscaling Dashboard")
    ax.set_xlabel("Time")
    ax.set_ylabel("System Metrics")
    ax2.set_ylabel("Servers")

    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")

    MAX_POINTS = 50

    time_steps = time_steps[-MAX_POINTS:]
    requests_history = requests_history[-MAX_POINTS:]
    capacity_history = capacity_history[-MAX_POINTS:]
    servers_history = servers_history[-MAX_POINTS:]

ani = FuncAnimation(fig, update, interval=1000)

plt.show()