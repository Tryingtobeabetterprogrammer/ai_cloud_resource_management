#!/usr/bin/env python3
"""
AI Cloud Resource Management System
Main entry point for comprehensive cloud resource management platform

Features:
- Dataset preparation and processing
- SLA violation prediction model
- SLA-aware decision engine
- Task scheduling system
- Advanced resource allocation
- Real-time monitoring dashboard
"""

import os
import sys
import time
import json
import threading
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all components
from ml_model.sla_prediction_model import train_sla_model, SLAViolationPredictor
from decision_engine.sla_aware_engine import make_sla_aware_decision, SLAAwareDecisionEngine
from scheduler.task_scheduler import TaskScheduler, TaskPriority, sample_compute_task, sample_sla_critical_task
from resource_allocation.advanced_allocator import AdvancedResourceAllocator, initialize_default_servers
from utils.ai_scaler import predict_servers
# Import advanced layers
from advanced_layers.sla_risk_score import calculate_sla_risk
from advanced_layers.resource_optimization import select_best_vm
from advanced_layers.sla_compliance_tracking import calculate_sla_compliance
from advanced_layers.integrated_scheduler import schedule_task_with_advanced_layers, get_advanced_scheduler_status
# simulation imported only when needed

# Optional dashboard import
try:
    from results.live_dashboard import run_dashboard
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Dashboard not available: {e}")
    print("💡 Install with: pip install matplotlib")
    DASHBOARD_AVAILABLE = False
    run_dashboard = None


class AICloudResourceManager:
    """Main AI Cloud Resource Management System"""
    
    def __init__(self):
        print("🚀 Initializing AI Cloud Resource Management System...")
        
        # Initialize components
        self.sla_predictor = SLAViolationPredictor()
        self.decision_engine = SLAAwareDecisionEngine()
        self.task_scheduler = TaskScheduler(max_workers=4)
        self.resource_allocator = AdvancedResourceAllocator()
        
        # System state
        self.running = False
        self.metrics = {
            'start_time': datetime.now(),
            'total_requests': 0,
            'sla_violations': 0,
            'resource_allocations': 0,
            'tasks_completed': 0,
            'total_cost': 0.0
        }
        
        # Initialize models and servers
        self._initialize_system()
        
    def _initialize_system(self):
        """Initialize all system components"""
        try:
            # Train/load SLA prediction model
            print("📊 Loading SLA violation prediction model...")
            if os.path.exists("ml_model/sla_violation_model.pkl"):
                self.sla_predictor.load_model("ml_model/sla_violation_model.pkl")
                print("✅ SLA model loaded successfully")
            else:
                predictor, accuracy = train_sla_model()
                self.sla_predictor = predictor
                print(f"✅ SLA model trained with accuracy: {accuracy:.4f}")
            
            # Initialize server pool
            print("🖥️  Initializing server pool...")
            initialize_default_servers()
            
            # Start task scheduler
            print("⚡ Starting task scheduler...")
            self.task_scheduler.start()
            
            print("✅ System initialization complete!")
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            raise
    
    def start_monitoring(self):
        """Start the main monitoring loop"""
        print("🔍 Starting resource monitoring...")
        self.running = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        # Start dashboard thread
        dashboard_thread = threading.Thread(target=self._start_dashboard, daemon=True)
        dashboard_thread.start()
        
        print("📈 Monitoring system started...")
        print("🎯 System is now running! Press Ctrl+C to stop.")
        
        try:
            # Main loop
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down system...")
            self.stop()
    
    def _monitoring_loop(self):
        """Main monitoring loop for system metrics"""
        while self.running:
            try:
                # Generate simulated metrics
                current_metrics = self._generate_current_metrics()
                
                # Make SLA-aware decision
                decision = make_sla_aware_decision(current_metrics)
                
                # Update metrics
                self._update_system_metrics(current_metrics, decision)
                
                # Write metrics for dashboard
                self._write_metrics_file(current_metrics, decision)
                
                # Check for resource optimization opportunities
                if self.metrics['total_requests'] % 10 == 0:
                    self._optimize_resources()
                
                # Submit sample tasks periodically
                if self.metrics['total_requests'] % 5 == 0:
                    self._submit_sample_tasks(current_metrics)
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"⚠️  Monitoring error: {e}")
                time.sleep(5)
    
    def _generate_current_metrics(self) -> Dict:
        """Generate current system metrics"""
        import random
        
        # Base metrics with some randomness
        base_requests = 100 + random.randint(-50, 100)
        base_servers = max(1, int(base_requests / 50) + random.randint(-1, 1))
        
        return {
            'requests': base_requests,
            'servers': base_servers,
            'capacity': base_servers * 50,
            'response_time': 50 + random.randint(-20, 50),
            'cpu_usage': 60 + random.randint(-20, 30),
            'memory_usage': 65 + random.randint(-15, 25),
            'network_io': 80 + random.randint(-30, 40),
            'disk_io': 40 + random.randint(-15, 25),
            'task_priority': random.randint(1, 3),
            'cost_per_hour': base_servers * 1.25,
            'uptime_percentage': 95 + random.uniform(0, 4)
        }
    
    def _update_system_metrics(self, current_metrics: Dict, decision: Dict):
        """Update system-wide metrics"""
        self.metrics['total_requests'] += current_metrics['requests']
        
        if decision['sla_violation_risk'] > 0.3:
            self.metrics['sla_violations'] += 1
        
        self.metrics['resource_allocations'] += 1
        self.metrics['total_cost'] += decision['expected_cost'] / 3600  # Convert to per-second cost
    
    def _write_metrics_file(self, current_metrics: Dict, decision: Dict):
        """Write metrics to JSON file for dashboard"""
        metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': current_metrics,
            'decision': {
                'recommended_servers': decision['recommended_servers'],
                'sla_violation_risk': decision['sla_violation_risk'],
                'confidence_score': decision['confidence_score'],
                'recommended_action': decision['recommended_action']
            },
            'scheduler_status': self.task_scheduler.get_queue_status(),
            'resource_utilization': self.resource_allocator.get_resource_utilization(),
            'system_metrics_summary': {
                'total_requests': self.metrics['total_requests'],
                'sla_violations': self.metrics['sla_violations'],
                'total_cost': round(self.metrics['total_cost'], 4),
                'uptime': (datetime.now() - self.metrics['start_time']).total_seconds()
            }
        }
        
        try:
            with open("results/system_metrics.json", "w") as f:
                json.dump(metrics_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error writing metrics: {e}")
    
    def _optimize_resources(self):
        """Optimize resource allocation"""
        try:
            optimization = self.resource_allocator.optimize_allocation()
            if optimization['migrations'] or optimization['performance_improvements']:
                print("🔧 Resource optimization recommendations:")
                for migration in optimization['migrations']:
                    print(f"  📦 {migration['server_id']}: {migration['reason']}")
                for improvement in optimization['performance_improvements']:
                    print(f"  ⚡ {improvement['server_id']}: {improvement['recommendation']}")
        except Exception as e:
            print(f"⚠️  Resource optimization error: {e}")
    
    def _submit_sample_tasks(self, current_metrics: Dict):
        """Submit sample tasks based on current load"""
        try:
            # Submit tasks based on current load
            load_level = current_metrics['requests'] / 100
            
            if load_level > 1.5:
                # High load - submit critical tasks
                task_id = self.task_scheduler.submit_task(
                    name="SLA Critical Task",
                    callback=sample_sla_critical_task,
                    priority=TaskPriority.CRITICAL,
                    estimated_duration=0.5,
                    cpu_required=2.0,
                    memory_required=1024
                )
            elif load_level > 1.0:
                # Medium load - submit high priority tasks
                task_id = self.task_scheduler.submit_task(
                    name="High Priority Compute",
                    callback=sample_compute_task,
                    priority=TaskPriority.HIGH,
                    estimated_duration=1.0,
                    cpu_required=1.5,
                    memory_required=768,
                    args=(load_level, 2)
                )
            else:
                # Low load - submit normal tasks
                task_id = self.task_scheduler.submit_task(
                    name="Background Compute",
                    callback=sample_compute_task,
                    priority=TaskPriority.NORMAL,
                    estimated_duration=2.0,
                    cpu_required=1.0,
                    memory_required=512,
                    args=(load_level, 1)
                )
        except Exception as e:
            print(f"⚠️  Task submission error: {e}")
    
    def _start_dashboard(self):
        """Start monitoring dashboard"""
        if not DASHBOARD_AVAILABLE:
            print("📊 Dashboard not available - running in console mode only")
            print("💡 Install matplotlib for dashboard: pip install matplotlib")
            
            # Console monitoring loop
            while self.running:
                try:
                    time.sleep(10)  # Update console every 10 seconds
                    if self.running:
                        status = self.task_scheduler.get_queue_status()
                        print(f"📊 Active: {status['running_tasks']} tasks | "
                              f"Queue: {status['pending_tasks']} pending | "
                              f"Cost: ${self.metrics['total_cost']:.4f} | "
                              f"SLA Violations: {self.metrics['sla_violations']}")
                except Exception as e:
                    print(f"⚠️  Console monitoring error: {e}")
            return
        
        try:
            # Import here to avoid circular imports
            import matplotlib.pyplot as plt
            from matplotlib.animation import FuncAnimation
            
            print("📊 Starting enhanced dashboard...")
            # The dashboard will read from system_metrics.json
            run_dashboard()
        except Exception as e:
            print(f"⚠️  Dashboard error: {e}")
    
    def stop(self):
        """Stop system gracefully"""
        print("🛑 Stopping AI Cloud Resource Management System...")
        self.running = False
        
        # Stop task scheduler
        self.task_scheduler.stop()
        
        # Print final statistics
        print("\n📊 Final System Statistics:")
        print(f"  Total Requests Processed: {self.metrics['total_requests']:,}")
        print(f"  SLA Violations: {self.metrics['sla_violations']}")
        print(f"  Resource Allocations: {self.metrics['resource_allocations']:,}")
        print(f"  Total Cost: ${self.metrics['total_cost']:.2f}")
        print(f"  Uptime: {datetime.now() - self.metrics['start_time']}")
        
        print("✅ System shutdown complete!")
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            'running': self.running,
            'uptime': (datetime.now() - self.metrics['start_time']).total_seconds(),
            'metrics': self.metrics.copy(),
            'scheduler_status': self.task_scheduler.get_queue_status(),
            'resource_utilization': self.resource_allocator.get_resource_utilization()
        }
    
    def demonstrate_advanced_layers(self):
        """Demonstrate the three advanced layers in action"""
        print("\n🎯 === Advanced Layers Demonstration ===")
        
        # Sample VM pool
        vm_pool = [
            {'id': 'vm-1', 'cpu_capacity': 100, 'memory_capacity': 100, 'cpu_usage': 60, 'memory_usage': 70, 'latency': 50},
            {'id': 'vm-2', 'cpu_capacity': 100, 'memory_capacity': 100, 'cpu_usage': 30, 'memory_usage': 40, 'latency': 80},
            {'id': 'vm-3', 'cpu_capacity': 100, 'memory_capacity': 100, 'cpu_usage': 80, 'memory_usage': 85, 'latency': 30},
            {'id': 'vm-4', 'cpu_capacity': 100, 'memory_capacity': 100, 'cpu_usage': 20, 'memory_usage': 25, 'latency': 20}
        ]
        
        print("\n📊 Layer 1: SLA Risk Score Assessment")
        print("=" * 50)
        
        # Demonstrate SLA risk calculation
        current_metrics = self._generate_current_metrics()
        sla_risk = calculate_sla_risk(
            current_metrics['cpu_usage'],
            current_metrics['memory_usage'],
            current_metrics['response_time'],
            current_metrics['cpu_usage']  # Using CPU as VM load proxy
        )
        
        print(f"🎯 SLA Risk Score: {sla_risk['risk_score']:.3f}")
        print(f"   Risk Level: {sla_risk['risk_level']}")
        print(f"   Component Risks:")
        for component, risk in sla_risk['component_risks'].items():
            print(f"     {component}: {risk:.3f}")
        print("   Recommendations:")
        for rec in sla_risk['recommendations']:
            print(f"     {rec}")
        
        print("\n🧠 Layer 2: Resource Optimization Score")
        print("=" * 50)
        
        # Demonstrate VM selection optimization
        best_vm = select_best_vm(vm_pool)
        if best_vm:
            print(f"🎯 Best VM Selection: {best_vm['id']}")
            print(f"   Optimization Score: {best_vm['optimization_score']:.3f}")
            print(f"   Selection Reason: {best_vm['selection_reason']}")
            print(f"   Score Components:")
            components = best_vm.get('components', {})
            for comp, value in components.items():
                print(f"     {comp}: {value}")
        
        print("\n📈 Layer 3: SLA Compliance Tracking")
        print("=" * 50)
        
        # Demonstrate SLA compliance tracking
        compliance = calculate_sla_compliance()
        print(f"🎯 Overall Compliance: {compliance.get('overall_compliance', 0):.1f}%")
        print(f"   Weighted Compliance: {compliance.get('weighted_compliance', 0):.1f}%")
        print(f"   Compliance Grade: {compliance.get('compliance_grade', 'N/A')}")
        print(f"   Total Tasks: {compliance.get('total_tasks', 0)}")
        print(f"   SLA Violations: {compliance.get('sla_violations', 0)}")
        
        if 'metric_compliance' in compliance:
            print(f"   Metric Breakdown:")
            for metric, data in compliance['metric_compliance'].items():
                print(f"     {metric}: {data['compliance_percentage']:.1f}% (Grade: {self._get_compliance_grade_symbol(data['compliance_percentage'])})")
        
        print("\n🔗 Integration: All Three Layers Working Together")
        print("=" * 50)
        
        # Show integrated decision
        sample_task = {
            'id': 'demo-task',
            'type': 'compute',
            'requirements': {'cpu': 20, 'memory': 30},
            'expected_response_time': 100,
            'expected_availability': 99.9,
            'expected_throughput': 1000,
            'expected_error_rate': 0.01
        }
        
        task_id = schedule_task_with_advanced_layers(sample_task)
        if task_id:
            print(f"✅ Task scheduled with ID: {task_id}")
            print("   Used all three advanced layers for decision making")
        else:
            print("❌ Task scheduling failed")
        
        print("\n🎯 === Advanced Layers Demo Complete ===")
    
    def _get_compliance_grade_symbol(self, compliance_percentage: float) -> str:
        """Get symbol for compliance grade"""
        if compliance_percentage >= 95:
            return "🟢"
        elif compliance_percentage >= 85:
            return "🟡"
        elif compliance_percentage >= 75:
            return "🟠"
        else:
            return "🔴"
    
    def run_simulation(self, duration_minutes: int = 5):
        """Run a simulation for specified duration"""
        print(f"🎬 Running simulation for {duration_minutes} minutes...")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time and self.running:
            # Generate and process metrics
            current_metrics = self._generate_current_metrics()
            decision = make_sla_aware_decision(current_metrics)
            self._update_system_metrics(current_metrics, decision)
            self._write_metrics_file(current_metrics, decision)
            
            # Submit sample tasks
            if self.metrics['total_requests'] % 3 == 0:
                self._submit_sample_tasks(current_metrics)
            
            time.sleep(1)
        
        print("✅ Simulation completed!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Cloud Resource Management System")
    parser.add_argument("--mode", choices=["monitor", "simulation", "train", "demo"], 
                       default="monitor", help="System operation mode")
    parser.add_argument("--duration", type=int, default=5, 
                       help="Simulation duration in minutes")
    parser.add_argument("--dashboard", action="store_true", 
                       help="Start monitoring dashboard")
    
    args = parser.parse_args()
    
    try:
        # Create system instance
        system = AICloudResourceManager()
        
        if args.mode == "train":
            print("🎯 Training mode: Training SLA prediction model...")
            predictor, accuracy = train_sla_model()
            print(f"✅ Model training completed with accuracy: {accuracy:.4f}")
            
        elif args.mode == "simulation":
            print(f"🎬 Simulation mode: Running {args.duration} minute simulation...")
            system.run_simulation(duration_minutes=args.duration)
            
        elif args.mode == "demo":
            print("🎯 Demo mode: Demonstrating advanced layers...")
            system.demonstrate_advanced_layers()
            
        else:  # monitor mode
            print("🔍 Monitor mode: Starting continuous monitoring...")
            system.start_monitoring()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ System error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
