#!/usr/bin/env python3
"""Test dashboard with sample data"""

import json
import os
from datetime import datetime

# Create sample metrics data for testing
sample_data = {
    "timestamp": datetime.now().isoformat(),
    "system_metrics": {
        "requests": 150,
        "servers": 3,
        "capacity": 150,
        "response_time": 85,
        "cpu_usage": 75,
        "memory_usage": 80,
        "network_io": 90,
        "disk_io": 40,
        "task_priority": 2,
        "cost_per_hour": 3.75,
        "uptime_percentage": 98.5
    },
    "decision": {
        "recommended_servers": 4,
        "sla_violation_risk": 0.65,
        "confidence_score": 0.85,
        "recommended_action": "Scale up to 4 servers"
    },
    "scheduler_status": {
        "running_tasks": 2,
        "pending_tasks": 5,
        "completed_tasks": 25
    },
    "resource_utilization": {
        "total_servers": 4,
        "active_servers": 3,
        "average_cpu_usage": 75.0,
        "average_memory_usage": 80.0
    }
}

# Ensure results directory exists
os.makedirs("results", exist_ok=True)

# Write sample data
with open("results/system_metrics.json", "w") as f:
    json.dump(sample_data, f, indent=2)

print("✅ Sample metrics data created for dashboard testing")
print("📊 Dashboard will now show actual data when run")

# Now run the dashboard
from results.live_dashboard import run_dashboard
print("🎯 Starting dashboard with sample data...")
run_dashboard()
