import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math
from decision_engine.sla_aware_engine import SLAAwareDecisionEngine
from scheduler.task_scheduler import TaskScheduler, TaskPriority

class AllocationStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    PERFORMANCE_BASED = "performance_based"
    COST_OPTIMIZED = "cost_optimized"
    SLA_AWARE = "sla_aware"
    HYBRID = "hybrid"

@dataclass
class ServerResource:
    server_id: str
    cpu_cores: float
    memory_mb: float
    storage_gb: float
    network_bandwidth: float
    cost_per_hour: float
    current_cpu_usage: float = 0.0
    current_memory_usage: float = 0.0
    current_storage_usage: float = 0.0
    current_network_usage: float = 0.0
    active_tasks: int = 0
    performance_score: float = 1.0
    uptime_percentage: float = 99.9
    response_time_ms: float = 50.0

@dataclass
class ResourceAllocation:
    task_id: str
    server_id: str
    cpu_allocated: float
    memory_allocated: float
    storage_allocated: float
    network_allocated: float
    estimated_completion_time: float
    cost: float

class AdvancedResourceAllocator:
    def __init__(self, strategy: AllocationStrategy = AllocationStrategy.HYBRID):
        self.strategy = strategy
        self.servers: Dict[str, ServerResource] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.allocation_history: List[ResourceAllocation] = []
        
        self.sla_engine = SLAAwareDecisionEngine()
        self.task_scheduler = TaskScheduler()
        
        # Allocation weights for different strategies
        self.allocation_weights = {
            'cpu_weight': 0.3,
            'memory_weight': 0.25,
            'cost_weight': 0.2,
            'performance_weight': 0.15,
            'network_weight': 0.1
        }
        
        # Performance thresholds
        self.thresholds = {
            'max_cpu_utilization': 0.8,
            'max_memory_utilization': 0.85,
            'max_task_per_server': 10,
            'min_performance_score': 0.7
        }
    
    def add_server(self, server: ServerResource):
        """Add a new server to the resource pool"""
        self.servers[server.server_id] = server
        print(f"Added server {server.server_id} to resource pool")
    
    def remove_server(self, server_id: str) -> bool:
        """Remove a server from the resource pool"""
        if server_id in self.servers:
            # Check if server has active allocations
            active_allocations = [alloc for alloc in self.allocations.values() 
                                 if alloc.server_id == server_id]
            if active_allocations:
                print(f"Cannot remove server {server_id}: {len(active_allocations)} active allocations")
                return False
            
            del self.servers[server_id]
            print(f"Removed server {server_id} from resource pool")
            return True
        return False
    
    def calculate_server_score(self, server: ServerResource, cpu_required: float, 
                            memory_required: float, network_required: float) -> float:
        """Calculate server suitability score for a task"""
        
        # Resource utilization scores (lower utilization = higher score)
        cpu_utilization = (server.current_cpu_usage + cpu_required) / server.cpu_cores
        memory_utilization = (server.current_memory_usage + memory_required) / server.memory_mb
        network_utilization = (server.current_network_usage + network_required) / server.network_bandwidth
        
        # Penalize if exceeding thresholds
        cpu_score = max(0, 1 - cpu_utilization) if cpu_utilization <= self.thresholds['max_cpu_utilization'] else 0
        memory_score = max(0, 1 - memory_utilization) if memory_utilization <= self.thresholds['max_memory_utilization'] else 0
        network_score = max(0, 1 - network_utilization)
        
        # Performance and cost scores
        performance_score = server.performance_score
        cost_score = 1 - (server.cost_per_hour / 10.0)  # Normalize to 0-1 range
        cost_score = max(0, min(1, cost_score))
        
        # Task load penalty
        load_penalty = min(server.active_tasks / self.thresholds['max_task_per_server'], 1.0)
        
        # Combined score
        total_score = (
            cpu_score * self.allocation_weights['cpu_weight'] +
            memory_score * self.allocation_weights['memory_weight'] +
            network_score * self.allocation_weights['network_weight'] +
            performance_score * self.allocation_weights['performance_weight'] +
            cost_score * self.allocation_weights['cost_weight'] -
            load_penalty * 0.2
        )
        
        return max(0, total_score)
    
    def find_best_server(self, cpu_required: float, memory_required: float, 
                        network_required: float, priority: TaskPriority) -> Optional[str]:
        """Find the best server for resource allocation based on strategy"""
        
        if not self.servers:
            return None
        
        candidate_servers = []
        
        for server_id, server in self.servers.items():
            # Check if server has enough resources
            if (server.cpu_cores >= server.current_cpu_usage + cpu_required and
                server.memory_mb >= server.current_memory_usage + memory_required and
                server.network_bandwidth >= server.current_network_usage + network_required):
                
                # Calculate score based on strategy
                if self.strategy == AllocationStrategy.ROUND_ROBIN:
                    score = server.active_tasks  # Fewer tasks = better
                elif self.strategy == AllocationStrategy.LEAST_LOADED:
                    score = -(server.current_cpu_usage + server.current_memory_usage)
                elif self.strategy == AllocationStrategy.PERFORMANCE_BASED:
                    score = server.performance_score
                elif self.strategy == AllocationStrategy.COST_OPTIMIZED:
                    score = -server.cost_per_hour
                elif self.strategy == AllocationStrategy.SLA_AWARE:
                    # Use SLA engine for scoring
                    metrics = {
                        'cpu_usage': (server.current_cpu_usage / server.cpu_cores) * 100,
                        'memory_usage': (server.current_memory_usage / server.memory_mb) * 100,
                        'response_time': server.response_time_ms,
                        'uptime_percentage': server.uptime_percentage,
                        'cost_per_hour': server.cost_per_hour,
                        'servers': 1,
                        'capacity': server.cpu_cores * 100,
                        'requests': int(cpu_required * 100)
                    }
                    decision = self.sla_engine.make_decision(metrics)
                    score = decision['confidence_score']
                else:  # HYBRID
                    score = self.calculate_server_score(server, cpu_required, memory_required, network_required)
                
                candidate_servers.append((server_id, score))
        
        if not candidate_servers:
            return None
        
        # Sort by score (descending) and return the best
        candidate_servers.sort(key=lambda x: x[1], reverse=True)
        return candidate_servers[0][0]
    
    def allocate_resources(self, task_id: str, cpu_required: float, memory_required: float,
                          storage_required: float, network_required: float,
                          priority: TaskPriority = TaskPriority.NORMAL,
                          estimated_duration: float = 1.0) -> Optional[ResourceAllocation]:
        """Allocate resources for a task"""
        
        server_id = self.find_best_server(cpu_required, memory_required, network_required, priority)
        
        if server_id is None:
            print(f"No suitable server found for task {task_id}")
            return None
        
        server = self.servers[server_id]
        
        # Create allocation
        allocation = ResourceAllocation(
            task_id=task_id,
            server_id=server_id,
            cpu_allocated=cpu_required,
            memory_allocated=memory_required,
            storage_allocated=storage_required,
            network_allocated=network_required,
            estimated_completion_time=estimated_duration,
            cost=server.cost_per_hour * (estimated_duration / 3600)
        )
        
        # Update server resources
        server.current_cpu_usage += cpu_required
        server.current_memory_usage += memory_required
        server.current_storage_usage += storage_required
        server.current_network_usage += network_required
        server.active_tasks += 1
        
        # Store allocation
        self.allocations[task_id] = allocation
        self.allocation_history.append(allocation)
        
        print(f"Allocated resources for task {task_id} on server {server_id}")
        return allocation
    
    def deallocate_resources(self, task_id: str) -> bool:
        """Deallocate resources for a completed task"""
        
        if task_id not in self.allocations:
            return False
        
        allocation = self.allocations[task_id]
        server = self.servers.get(allocation.server_id)
        
        if server:
            # Update server resources
            server.current_cpu_usage -= allocation.cpu_allocated
            server.current_memory_usage -= allocation.memory_allocated
            server.current_storage_usage -= allocation.storage_allocated
            server.current_network_usage -= allocation.network_allocated
            server.active_tasks -= 1
            
            print(f"Deallocated resources for task {task_id} from server {allocation.server_id}")
        
        # Remove allocation
        del self.allocations[task_id]
        return True
    
    def get_resource_utilization(self) -> Dict:
        """Get current resource utilization across all servers"""
        
        if not self.servers:
            return {}
        
        total_cpu = sum(server.cpu_cores for server in self.servers.values())
        total_memory = sum(server.memory_mb for server in self.servers.values())
        total_storage = sum(server.storage_gb for server in self.servers.values())
        total_network = sum(server.network_bandwidth for server in self.servers.values())
        
        used_cpu = sum(server.current_cpu_usage for server in self.servers.values())
        used_memory = sum(server.current_memory_usage for server in self.servers.values())
        used_storage = sum(server.current_storage_usage for server in self.servers.values())
        used_network = sum(server.current_network_usage for server in self.servers.values())
        
        return {
            'cpu_utilization': used_cpu / total_cpu if total_cpu > 0 else 0,
            'memory_utilization': used_memory / total_memory if total_memory > 0 else 0,
            'storage_utilization': used_storage / total_storage if total_storage > 0 else 0,
            'network_utilization': used_network / total_network if total_network > 0 else 0,
            'total_servers': len(self.servers),
            'active_allocations': len(self.allocations),
            'total_cost_per_hour': sum(server.cost_per_hour for server in self.servers.values())
        }
    
    def optimize_allocation(self) -> Dict:
        """Optimize current resource allocation"""
        
        optimization_results = {
            'migrations': [],
            'savings': 0.0,
            'performance_improvements': []
        }
        
        # Find underutilized servers
        for server_id, server in self.servers.items():
            cpu_util = server.current_cpu_usage / server.cpu_cores if server.cpu_cores > 0 else 0
            memory_util = server.current_memory_usage / server.memory_mb if server.memory_mb > 0 else 0
            
            if cpu_util < 0.3 and memory_util < 0.3 and server.active_tasks > 0:
                # Server is underutilized, consider migration
                optimization_results['migrations'].append({
                    'server_id': server_id,
                    'reason': 'Underutilized',
                    'cpu_utilization': cpu_util,
                    'memory_utilization': memory_util,
                    'active_tasks': server.active_tasks
                })
        
        # Find overloaded servers
        for server_id, server in self.servers.items():
            cpu_util = server.current_cpu_usage / server.cpu_cores if server.cpu_cores > 0 else 0
            memory_util = server.current_memory_usage / server.memory_mb if server.memory_mb > 0 else 0
            
            if cpu_util > 0.8 or memory_util > 0.8:
                # Server is overloaded, consider load balancing
                optimization_results['performance_improvements'].append({
                    'server_id': server_id,
                    'reason': 'Overloaded',
                    'cpu_utilization': cpu_util,
                    'memory_utilization': memory_util,
                    'recommendation': 'Migrate some tasks to other servers'
                })
        
        return optimization_results
    
    def predict_resource_needs(self, forecast_requests: List[int], 
                             time_horizon_hours: float) -> Dict:
        """Predict future resource needs based on request forecast"""
        
        if not forecast_requests:
            return {'recommended_servers': 0, 'estimated_cost': 0.0}
        
        avg_requests = np.mean(forecast_requests)
        peak_requests = max(forecast_requests)
        
        # Estimate CPU requirements (assume 1 CPU core per 100 requests)
        required_cpu = peak_requests / 100
        required_memory = required_cpu * 1024  # 1GB memory per CPU core
        
        # Find suitable servers
        suitable_servers = []
        for server_id, server in self.servers.items():
            if (server.cpu_cores >= required_cpu and 
                server.memory_mb >= required_memory):
                suitable_servers.append((server_id, server.cost_per_hour))
        
        # Sort by cost
        suitable_servers.sort(key=lambda x: x[1])
        
        if suitable_servers:
            best_server_id, best_cost = suitable_servers[0]
            total_cost = best_cost * time_horizon_hours
        else:
            # Need to provision new server
            best_server_id = "new_server"
            total_cost = 5.0 * time_horizon_hours  # Assume $5/hour for new server
        
        return {
            'recommended_servers': 1,
            'recommended_server_id': best_server_id,
            'estimated_cost': total_cost,
            'required_cpu': required_cpu,
            'required_memory': required_memory,
            'peak_requests': peak_requests,
            'average_requests': avg_requests
        }

# Global allocator instance
resource_allocator = AdvancedResourceAllocator()

def initialize_default_servers():
    """Initialize default server pool"""
    servers = [
        ServerResource("server-1", 4.0, 8192, 500, 1000, 2.50),
        ServerResource("server-2", 8.0, 16384, 1000, 2000, 5.00),
        ServerResource("server-3", 2.0, 4096, 250, 500, 1.25),
        ServerResource("server-4", 16.0, 32768, 2000, 4000, 10.00)
    ]
    
    for server in servers:
        resource_allocator.add_server(server)
    
    print("Initialized default server pool with 4 servers")
