import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json
import os
import time
from datetime import datetime

server_capacity = 50
sla_margin = 20

requests_history = []
capacity_history = []
servers_history = []
time_steps = []

sla_violations_x = []
sla_violations_y = []

fig, ax = plt.subplots(figsize=(12, 8))
ax2 = ax.twinx()

def update(frame):
    global time_steps, requests_history, capacity_history, servers_history

    # Check for system metrics file
    if not os.path.exists("results/system_metrics.json"):
        return

    try:
        with open("results/system_metrics.json") as f:
            data = json.load(f)
        
        # Extract system metrics
        system_metrics = data.get('system_metrics', {})
        decision_data = data.get('decision', {})
        
        requests = system_metrics.get('requests', 0)
        servers = system_metrics.get('servers', 0)
        capacity = system_metrics.get('capacity', 0)
        
        # Add to history
        current_time = len(time_steps)
        time_steps.append(current_time)
        requests_history.append(requests)
        servers_history.append(servers)
        capacity_history.append(capacity)
        
        # Keep only last 50 data points
        if len(time_steps) > 50:
            time_steps = time_steps[-50:]
            requests_history = requests_history[-50:]
            servers_history = servers_history[-50:]
            capacity_history = capacity_history[-50:]
        
        # Clear and redraw
        ax.clear()
        ax2.clear()
        
        # Plot requests and capacity
        ax.plot(time_steps, requests_history, 'b-', label='Requests', linewidth=2, marker='o', markersize=4)
        ax.plot(time_steps, capacity_history, 'g--', label='Capacity', linewidth=2, marker='s', markersize=4)
        ax.plot(time_steps, servers_history, 'r-', label='Servers', linewidth=2, marker='^', markersize=4)
        
        # Plot SLA violations if any
        sla_risk = decision_data.get('sla_violation_risk', 0)
        if sla_risk > 0.3:
            ax2.plot(time_steps[-1], sla_risk * 100, 'ro', markersize=12, label='SLA Risk', alpha=0.7)
        
        # Set labels and title
        ax.set_xlabel('Time Steps', fontsize=12)
        ax.set_ylabel('Requests / Servers', color='b', fontsize=12)
        ax2.set_ylabel('SLA Risk %', color='r', fontsize=12)
        
        ax.set_title(f'AI Cloud Resource Management - Real-time Monitoring\n'
                    f'Current: {requests} requests, {servers} servers, {capacity} capacity\n'
                    f'SLA Risk: {sla_risk:.3f} | Confidence: {decision_data.get("confidence_score", 0):.3f}', 
                    fontsize=14, fontweight='bold')
        
        # Add legends
        ax.legend(loc='upper left', fontsize=10)
        ax2.legend(loc='upper right', fontsize=10)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Set y-axis limits with better scaling
        if len(requests_history) > 0:
            max_val = max(max(requests_history), max(capacity_history), max(servers_history))
            ax.set_ylim(0, max_val * 1.2)
            ax2.set_ylim(0, 100)
        
        # Add SLA threshold line
        ax.axhline(y=server_capacity, color='orange', linestyle=':', alpha=0.7, label='SLA Threshold')
        
        # Add current values as text
        ax.text(0.02, 0.98, f'Requests: {requests}', transform=ax.transAxes, 
                fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.text(0.02, 0.92, f'Servers: {servers}', transform=ax.transAxes, 
                fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        ax.text(0.02, 0.86, f'Capacity: {capacity}', transform=ax.transAxes, 
                fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        
        # Add timestamp
        timestamp = data.get('timestamp', datetime.now().isoformat())
        ax.text(0.98, 0.02, f'Updated: {timestamp[-8:]}', transform=ax.transAxes, 
                fontsize=9, horizontalalignment='right', alpha=0.7)
        
    except Exception as e:
        print(f"Dashboard update error: {e}")
        return

def run_dashboard():
    """Run the live dashboard"""
    print("📊 Starting Live Dashboard...")
    print("📈 Monitoring real-time system metrics")
    print("💡 The dashboard will update every 2 seconds with live data")
    print("🎯 Make sure the main system is running to see live updates")
    
    # Create animation
    ani = FuncAnimation(fig, update, interval=2000, cache_frame_data=False)
    
    plt.tight_layout()
    plt.show()
    return ani

def run_dashboard_standalone():
    """Run dashboard with sample data for testing"""
    print("📊 Running Dashboard with Sample Data...")
    
    # Create sample data points
    sample_requests = [120, 135, 150, 140, 165, 180, 175, 190, 185, 200]
    sample_servers = [3, 3, 4, 4, 4, 4, 5, 5, 5, 5]
    sample_capacity = [150, 150, 200, 200, 200, 200, 250, 250, 250, 250]
    
    global time_steps, requests_history, servers_history, capacity_history
    
    # Load sample data
    for i in range(len(sample_requests)):
        time_steps.append(i)
        requests_history.append(sample_requests[i])
        servers_history.append(sample_servers[i])
        capacity_history.append(sample_capacity[i])
    
    # Plot the data
    ax.plot(time_steps, requests_history, 'b-', label='Requests', linewidth=2, marker='o', markersize=6)
    ax.plot(time_steps, capacity_history, 'g--', label='Capacity', linewidth=2, marker='s', markersize=6)
    ax.plot(time_steps, servers_history, 'r-', label='Servers', linewidth=2, marker='^', markersize=6)
    
    # Add SLA threshold line
    ax.axhline(y=server_capacity, color='orange', linestyle=':', alpha=0.7, label='SLA Threshold')
    
    # Set labels and title
    ax.set_xlabel('Time Steps', fontsize=12)
    ax.set_ylabel('Requests / Servers', color='b', fontsize=12)
    ax.set_title('AI Cloud Resource Management - Sample Data Visualization\n'
                'Showing: Requests, Capacity, and Servers over time', 
                fontsize=14, fontweight='bold')
    
    # Add legend and grid
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Set y-axis limits
    ax.set_ylim(0, max(max(requests_history), max(capacity_history)) * 1.2)
    
    # Add sample data annotations
    ax.text(0.02, 0.98, 'Sample Data Demo', transform=ax.transAxes, 
            fontsize=12, verticalalignment='top', 
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.show()
