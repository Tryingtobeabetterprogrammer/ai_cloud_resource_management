import random
import time
import json
from utils.ai_scaler import predict_servers

servers = 1
server_capacity = 50
sla_margin = 20
t = 0   
requests = 60

while True:
    requests = requests + random.randint(-10, 10)
    requests = max(20, min(200, requests))
    # AI prediction
    servers = predict_servers(requests)

    # safety rule to prevent SLA violation
    required_servers = (requests + sla_margin) // server_capacity + 1
    servers = max(servers, required_servers)

    total_capacity = servers * server_capacity

    print("\nTime:", t)
    print("Incoming Requests:", requests)
    print("AI Predicted Servers:", servers)
    print("Total Capacity:", total_capacity)

    # write metrics for dashboard
    with open("results/metrics.json", "w") as f:
        json.dump({
            "time": t,
            "requests": requests,
            "servers": servers,
            "capacity": total_capacity
        }, f)

    t += 1   # increase time

    time.sleep(2)