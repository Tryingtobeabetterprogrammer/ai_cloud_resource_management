import heapq
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
import json

class TaskPriority(Enum):
    CRITICAL = 1    # SLA-critical tasks
    HIGH = 2        # High priority user requests
    NORMAL = 3      # Standard processing
    LOW = 4         # Background tasks
    MAINTENANCE = 5 # Maintenance tasks

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    estimated_duration: float = 1.0  # seconds
    cpu_required: float = 1.0  # CPU cores
    memory_required: float = 512  # MB
    deadline: Optional[datetime] = None
    callback: Optional[Callable] = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        # For priority queue: lower priority number = higher priority
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        # If same priority, earlier deadline wins
        if self.deadline and other.deadline:
            return self.deadline < other.deadline
        if self.deadline:
            return True
        if other.deadline:
            return False
        # Finally, earlier creation time wins
        return self.created_at < other.created_at

class TaskScheduler:
    def __init__(self, max_workers: int = 4, max_cpu: float = 8.0, max_memory: float = 16384):
        self.max_workers = max_workers
        self.max_cpu = max_cpu
        self.max_memory = max_memory
        
        self.task_queue = []  # Priority queue
        self.running_tasks = {}  # task_id -> Task
        self.completed_tasks = {}  # task_id -> Task
        self.failed_tasks = {}  # task_id -> Task
        
        self.current_cpu = 0.0
        self.current_memory = 0.0
        self.active_workers = 0
        
        self.scheduler_lock = threading.Lock()
        self.worker_threads = []
        self.running = False
        
        # Metrics
        self.metrics = {
            'tasks_submitted': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'average_wait_time': 0.0,
            'average_execution_time': 0.0,
            'sla_violations': 0
        }
    
    def start(self):
        """Start the task scheduler"""
        if self.running:
            return
        
        self.running = True
        # Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, name=f"Worker-{i}")
            worker.daemon = True
            worker.start()
            self.worker_threads.append(worker)
        
        print(f"Task scheduler started with {self.max_workers} workers")
    
    def stop(self):
        """Stop the task scheduler"""
        self.running = False
        # Wait for workers to finish
        for worker in self.worker_threads:
            worker.join(timeout=5)
        print("Task scheduler stopped")
    
    def submit_task(self, 
                   name: str,
                   callback: Callable,
                   priority: TaskPriority = TaskPriority.NORMAL,
                   estimated_duration: float = 1.0,
                   cpu_required: float = 1.0,
                   memory_required: float = 512,
                   deadline: Optional[datetime] = None,
                   max_retries: int = 3,
                   *args,
                   **kwargs) -> str:
        """Submit a new task to the scheduler"""
        
        task = Task(
            name=name,
            priority=priority,
            estimated_duration=estimated_duration,
            cpu_required=cpu_required,
            memory_required=memory_required,
            deadline=deadline,
            callback=callback,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries
        )
        
        with self.scheduler_lock:
            heapq.heappush(self.task_queue, task)
            self.metrics['tasks_submitted'] += 1
        
        print(f"Task submitted: {task.name} (ID: {task.id[:8]})")
        return task.id
    
    def _worker_loop(self):
        """Main worker thread loop"""
        while self.running:
            task = self._get_next_task()
            if task is None:
                time.sleep(0.1)  # No tasks available, wait
                continue
            
            self._execute_task(task)
    
    def _get_next_task(self) -> Optional[Task]:
        """Get the next available task that can be executed"""
        with self.scheduler_lock:
            while self.task_queue:
                task = heapq.heappop(self.task_queue)
                
                # Check if we have enough resources
                if (self.current_cpu + task.cpu_required <= self.max_cpu and
                    self.current_memory + task.memory_required <= self.max_memory and
                    self.active_workers < self.max_workers):
                    
                    # Check if task missed deadline
                    if task.deadline and datetime.now() > task.deadline:
                        task.status = TaskStatus.FAILED
                        task.error = "Deadline missed"
                        self.failed_tasks[task.id] = task
                        self.metrics['tasks_failed'] += 1
                        self.metrics['sla_violations'] += 1
                        continue
                    
                    return task
                
                # Can't execute now, put back and break
                heapq.heappush(self.task_queue, task)
                break
        
        return None
    
    def _execute_task(self, task: Task):
        """Execute a task"""
        with self.scheduler_lock:
            self.running_tasks[task.id] = task
            self.current_cpu += task.cpu_required
            self.current_memory += task.memory_required
            self.active_workers += 1
            
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
        
        try:
            print(f"Executing task: {task.name} (ID: {task.id[:8]})")
            
            # Execute the callback
            start_time = time.time()
            result = task.callback(*task.args, **task.kwargs)
            execution_time = time.time() - start_time
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Update metrics
            with self.scheduler_lock:
                self.metrics['tasks_completed'] += 1
                wait_time = (task.started_at - task.created_at).total_seconds()
                self._update_average_metrics(wait_time, execution_time)
            
            print(f"Task completed: {task.name} (ID: {task.id[:8]}) in {execution_time:.2f}s")
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count <= task.max_retries:
                # Retry the task
                task.status = TaskStatus.PENDING
                task.started_at = None
                with self.scheduler_lock:
                    heapq.heappush(self.task_queue, task)
                print(f"Task failed, retrying: {task.name} (ID: {task.id[:8]}) - Attempt {task.retry_count}")
            else:
                # Max retries exceeded
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                with self.scheduler_lock:
                    self.failed_tasks[task.id] = task
                    self.metrics['tasks_failed'] += 1
                print(f"Task failed permanently: {task.name} (ID: {task.id[:8]}) - {task.error}")
        
        finally:
            # Release resources
            with self.scheduler_lock:
                self.current_cpu -= task.cpu_required
                self.current_memory -= task.memory_required
                self.active_workers -= 1
                
                if task.status == TaskStatus.COMPLETED:
                    self.completed_tasks[task.id] = task
                
                # Remove from running tasks
                if task.id in self.running_tasks:
                    del self.running_tasks[task.id]
    
    def _update_average_metrics(self, wait_time: float, execution_time: float):
        """Update average wait and execution time metrics"""
        completed = self.metrics['tasks_completed']
        if completed == 1:
            self.metrics['average_wait_time'] = wait_time
            self.metrics['average_execution_time'] = execution_time
        else:
            self.metrics['average_wait_time'] = (
                (self.metrics['average_wait_time'] * (completed - 1) + wait_time) / completed
            )
            self.metrics['average_execution_time'] = (
                (self.metrics['average_execution_time'] * (completed - 1) + execution_time) / completed
            )
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get the status of a specific task"""
        with self.scheduler_lock:
            for task_dict in [self.running_tasks, self.completed_tasks, self.failed_tasks]:
                if task_id in task_dict:
                    task = task_dict[task_id]
                    return {
                        'id': task.id,
                        'name': task.name,
                        'status': task.status.value,
                        'priority': task.priority.name,
                        'created_at': task.created_at.isoformat(),
                        'started_at': task.started_at.isoformat() if task.started_at else None,
                        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                        'error': task.error,
                        'retry_count': task.retry_count
                    }
            
            # Check if in queue
            for task in self.task_queue:
                if task.id == task_id:
                    return {
                        'id': task.id,
                        'name': task.name,
                        'status': task.status.value,
                        'priority': task.priority.name,
                        'created_at': task.created_at.isoformat(),
                        'started_at': None,
                        'completed_at': None,
                        'error': None,
                        'retry_count': task.retry_count
                    }
        
        return None
    
    def get_queue_status(self) -> Dict:
        """Get current queue and system status"""
        with self.scheduler_lock:
            return {
                'pending_tasks': len(self.task_queue),
                'running_tasks': len(self.running_tasks),
                'completed_tasks': len(self.completed_tasks),
                'failed_tasks': len(self.failed_tasks),
                'active_workers': self.active_workers,
                'cpu_utilization': self.current_cpu,
                'memory_utilization': self.current_memory,
                'metrics': self.metrics.copy()
            }
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        with self.scheduler_lock:
            for i, task in enumerate(self.task_queue):
                if task.id == task_id:
                    task.status = TaskStatus.CANCELLED
                    task.completed_at = datetime.now()
                    self.task_queue.pop(i)
                    heapq.heapify(self.task_queue)
                    print(f"Task cancelled: {task.name} (ID: {task_id[:8]})")
                    return True
        return False
    
    def get_pending_tasks_by_priority(self) -> Dict[str, int]:
        """Get count of pending tasks by priority"""
        priority_counts = {priority.name: 0 for priority in TaskPriority}
        
        with self.scheduler_lock:
            for task in self.task_queue:
                priority_counts[task.priority.name] += 1
        
        return priority_counts

# Global scheduler instance
scheduler = TaskScheduler()

# Example task functions
def sample_compute_task(duration: float, complexity: int = 1):
    """Sample computational task"""
    time.sleep(duration)
    return {"result": f"Computation completed", "complexity": complexity}

def sample_io_task(data_size: int):
    """Sample I/O task"""
    time.sleep(data_size / 1000)  # Simulate I/O time
    return {"processed_bytes": data_size}

def sample_sla_critical_task():
    """Sample SLA-critical task"""
    time.sleep(0.5)
    return {"sla_status": "compliant", "timestamp": datetime.now().isoformat()}
