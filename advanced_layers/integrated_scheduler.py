"""
Advanced Integrated Scheduler
Combines SLA Risk Assessment, Resource Optimization, and SLA Compliance Tracking
"""

import time
import threading
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Import advanced layers
from advanced_layers.sla_risk_score import calculate_sla_risk, sla_risk_model
from advanced_layers.resource_optimization import select_best_vm, resource_optimizer
from advanced_layers.sla_compliance_tracking import track_sla_compliance, calculate_sla_compliance

class AdvancedIntegratedScheduler:
    """Advanced scheduler that integrates all three advanced layers"""
    
    def __init__(self):
        self.running = False
        self.active_tasks = {}
        self.completed_tasks = {}
        self.vm_pool = []
        self.decision_history = []
        
        # Performance metrics
        self.scheduler_metrics = {
            'total_decisions': 0,
            'sla_violations_prevented': 0,
            'optimization_improvements': 0,
            'compliance_rate': 0.0
        }
        
    def add_vm_to_pool(self, vm: Dict):
        """Add a VM to the resource pool"""
        vm_id = vm.get('id', f"vm-{len(self.vm_pool)}")
        vm['id'] = vm_id
        vm['added_timestamp'] = datetime.now()
        self.vm_pool.append(vm)
        print(f"🖥️  Added VM {vm_id} to pool")
    
    def schedule_task(self, task: Dict) -> Optional[str]:
        """
        Schedule task using advanced multi-layer decision making
        
        Process:
        1. Calculate SLA Risk Score
        2. Select best VM using Resource Optimization Score
        3. Track SLA Compliance
        """
        task_id = task.get('id', f"task-{int(time.time())}")
        task['scheduled_at'] = datetime.now()
        
        print(f"📋 Scheduling task {task_id}")
        
        # Layer 1: SLA Risk Assessment
        current_load = self._calculate_current_system_load()
        sla_risk = calculate_sla_risk(
            current_load['cpu_usage'],
            current_load['memory_usage'],
            current_load['avg_latency'],
            current_load['vm_load']
        )
        
        print(f"🎯 SLA Risk Assessment: {sla_risk['risk_level']} ({sla_risk['risk_score']:.3f})")
        
        # Decision based on SLA risk
        if sla_risk['risk_score'] > 0.6:
            print("🚨 High SLA Risk → redistribute load")
            # Find less loaded VMs
            suitable_vms = self._find_suitable_vms_for_high_risk(task)
        else:
            print("✅ Low SLA Risk → schedule task")
            # Use all available VMs
            suitable_vms = [vm for vm in self.vm_pool if self._is_vm_available(vm, task)]
        
        if not suitable_vms:
            print("❌ No suitable VMs available")
            return None
        
        # Layer 2: Resource Optimization Score for VM Selection
        selected_vm = select_best_vm(suitable_vms)
        
        if selected_vm:
            print(f"🎯 Selected VM {selected_vm['id']} (Score: {selected_vm['optimization_score']:.3f})")
            print(f"   Reason: {selected_vm['selection_reason']}")
        else:
            print("❌ VM selection failed")
            return None
        
        # Assign task to VM
        task['assigned_vm'] = selected_vm['id']
        task['sla_risk_at_scheduling'] = sla_risk
        task['vm_selection_score'] = selected_vm['optimization_score']
        
        # Update VM load
        self._update_vm_load(selected_vm['id'], task)
        
        # Store active task
        self.active_tasks[task_id] = task
        
        # Layer 3: SLA Compliance Tracking
        self._track_task_for_compliance(task_id, task)
        
        # Record decision
        self._record_decision(task, sla_risk, selected_vm)
        
        return task_id
    
    def _calculate_current_system_load(self) -> Dict:
        """Calculate current system-wide load metrics"""
        if not self.vm_pool:
            return {'cpu_usage': 0, 'memory_usage': 0, 'avg_latency': 0, 'vm_load': 0}
        
        total_cpu = sum(vm.get('cpu_usage', 0) for vm in self.vm_pool)
        total_memory = sum(vm.get('memory_usage', 0) for vm in self.vm_pool)
        total_capacity = sum(vm.get('cpu_capacity', 100) for vm in self.vm_pool)
        avg_latency = sum(vm.get('latency', 0) for vm in self.vm_pool) / len(self.vm_pool)
        
        return {
            'cpu_usage': total_cpu / len(self.vm_pool),
            'memory_usage': total_memory / len(self.vm_pool),
            'avg_latency': avg_latency,
            'vm_load': (total_cpu / total_capacity) * 100 if total_capacity > 0 else 0
        }
    
    def _find_suitable_vms_for_high_risk(self, task: Dict) -> List[Dict]:
        """Find VMs suitable for high-risk scenarios (prefer less loaded)"""
        suitable_vms = []
        
        for vm in self.vm_pool:
            if not self._is_vm_available(vm, task):
                continue
            
            # For high risk, prefer VMs with lower load
            cpu_load = vm.get('cpu_usage', 0) / vm.get('cpu_capacity', 100) * 100
            memory_load = vm.get('memory_usage', 0) / vm.get('memory_capacity', 100) * 100
            
            # Only consider VMs with load < 70%
            if cpu_load < 70 and memory_load < 70:
                suitable_vms.append(vm)
        
        return suitable_vms
    
    def _is_vm_available(self, vm: Dict, task: Dict) -> bool:
        """Check if VM is available for task"""
        vm_requirements = task.get('requirements', {})
        
        # Check resource availability
        required_cpu = vm_requirements.get('cpu', 0)
        required_memory = vm_requirements.get('memory', 0)
        
        available_cpu = vm.get('cpu_capacity', 100) - vm.get('cpu_usage', 0)
        available_memory = vm.get('memory_capacity', 100) - vm.get('memory_usage', 0)
        
        return available_cpu >= required_cpu and available_memory >= required_memory
    
    def _update_vm_load(self, vm_id: str, task: Dict):
        """Update VM load after task assignment"""
        for vm in self.vm_pool:
            if vm['id'] == vm_id:
                requirements = task.get('requirements', {})
                vm['cpu_usage'] = vm.get('cpu_usage', 0) + requirements.get('cpu', 0)
                vm['memory_usage'] = vm.get('memory_usage', 0) + requirements.get('memory', 0)
                vm['last_task_assigned'] = datetime.now()
                break
    
    def _track_task_for_compliance(self, task_id: str, task: Dict):
        """Track task for SLA compliance monitoring"""
        # Start compliance tracking for this task
        track_sla_compliance(
            completion_time=0,  # Will be updated on completion
            success=True,
            response_time=task.get('expected_response_time', 100),
            availability=task.get('expected_availability', 99.9),
            throughput=task.get('expected_throughput', 1000),
            error_rate=task.get('expected_error_rate', 0.01)
        )
    
    def _record_decision(self, task: Dict, sla_risk: Dict, selected_vm: Dict):
        """Record scheduling decision for analysis"""
        decision = {
            'timestamp': datetime.now(),
            'task_id': task.get('id'),
            'task_type': task.get('type', 'unknown'),
            'sla_risk_assessment': sla_risk,
            'vm_selection': {
                'vm_id': selected_vm['id'],
                'optimization_score': selected_vm['optimization_score'],
                'selection_reason': selected_vm['selection_reason']
            },
            'system_load_at_decision': self._calculate_current_system_load()
        }
        
        self.decision_history.append(decision)
        self.scheduler_metrics['total_decisions'] += 1
        
        # Update performance metrics
        if sla_risk['risk_score'] > 0.6:
            self.scheduler_metrics['sla_violations_prevented'] += 1
        
        if selected_vm['optimization_score'] > 0.7:
            self.scheduler_metrics['optimization_improvements'] += 1
    
    def complete_task(self, task_id: str, success: bool = True, 
                   completion_time: float = None, metrics: Dict = None):
        """Mark task as completed and update compliance"""
        if task_id not in self.active_tasks:
            print(f"⚠️  Task {task_id} not found in active tasks")
            return
        
        task = self.active_tasks[task_id]
        task['completed_at'] = datetime.now()
        task['success'] = success
        task['completion_time'] = completion_time or time.time()
        
        # Update VM load (release resources)
        if 'assigned_vm' in task:
            self._release_vm_resources(task['assigned_vm'], task)
        
        # Update SLA compliance tracking
        track_sla_compliance(
            completion_time=task['completion_time'],
            success=success,
            response_time=metrics.get('response_time') if metrics else None,
            availability=metrics.get('availability') if metrics else None,
            throughput=metrics.get('throughput') if metrics else None,
            error_rate=metrics.get('error_rate') if metrics else None
        )
        
        # Move to completed tasks
        self.completed_tasks[task_id] = task
        del self.active_tasks[task_id]
        
        print(f"✅ Task {task_id} completed successfully" if success else f"❌ Task {task_id} failed")
    
    def _release_vm_resources(self, vm_id: str, task: Dict):
        """Release VM resources after task completion"""
        for vm in self.vm_pool:
            if vm['id'] == vm_id:
                requirements = task.get('requirements', {})
                vm['cpu_usage'] = max(0, vm.get('cpu_usage', 0) - requirements.get('cpu', 0))
                vm['memory_usage'] = max(0, vm.get('memory_usage', 0) - requirements.get('memory', 0))
                vm['last_task_completed'] = datetime.now()
                break
    
    def get_scheduler_status(self) -> Dict:
        """Get comprehensive scheduler status"""
        current_compliance = calculate_sla_compliance()
        
        return {
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'vm_pool_size': len(self.vm_pool),
            'total_decisions': self.scheduler_metrics['total_decisions'],
            'sla_violations_prevented': self.scheduler_metrics['sla_violations_prevented'],
            'optimization_improvements': self.scheduler_metrics['optimization_improvements'],
            'current_compliance': current_compliance,
            'system_load': self._calculate_current_system_load(),
            'vm_pool_status': self._get_vm_pool_status()
        }
    
    def _get_vm_pool_status(self) -> List[Dict]:
        """Get status of all VMs in pool"""
        vm_status = []
        
        for vm in self.vm_pool:
            cpu_util = (vm.get('cpu_usage', 0) / vm.get('cpu_capacity', 100)) * 100
            memory_util = (vm.get('memory_usage', 0) / vm.get('memory_capacity', 100)) * 100
            
            vm_status.append({
                'id': vm['id'],
                'cpu_utilization': cpu_util,
                'memory_utilization': memory_util,
                'latency': vm.get('latency', 0),
                'status': 'available' if cpu_util < 90 and memory_util < 90 else 'loaded',
                'last_activity': vm.get('last_task_assigned', vm.get('added_timestamp'))
            })
        
        return vm_status
    
    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        # Get insights from resource optimizer
        optimization_insights = resource_optimizer.get_optimization_insights()
        
        # Get SLA risk summary
        risk_summary = sla_risk_model.get_risk_summary()
        
        # Get compliance report
        compliance_report = calculate_sla_compliance()
        
        return {
            'report_timestamp': datetime.now().isoformat(),
            'scheduler_metrics': self.scheduler_metrics,
            'optimization_insights': optimization_insights,
            'sla_risk_summary': risk_summary,
            'compliance_report': compliance_report,
            'decision_patterns': self._analyze_decision_patterns(),
            'recommendations': self._generate_performance_recommendations()
        }
    
    def _analyze_decision_patterns(self) -> Dict:
        """Analyze patterns in scheduling decisions"""
        if not self.decision_history:
            return {'status': 'NO_DATA'}
        
        recent_decisions = self.decision_history[-50:]  # Last 50 decisions
        
        # Analyze VM selection patterns
        vm_selection_counts = {}
        risk_level_distribution = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'MINIMAL': 0}
        
        for decision in recent_decisions:
            vm_id = decision['vm_selection']['vm_id']
            vm_selection_counts[vm_id] = vm_selection_counts.get(vm_id, 0) + 1
            
            risk_level = decision['sla_risk_assessment']['risk_level']
            risk_level_distribution[risk_level] += 1
        
        return {
            'total_decisions_analyzed': len(recent_decisions),
            'most_selected_vm': max(vm_selection_counts.items(), key=lambda x: x[1])[0] if vm_selection_counts else None,
            'vm_selection_distribution': vm_selection_counts,
            'risk_level_distribution': risk_level_distribution,
            'average_optimization_score': np.mean([d['vm_selection']['optimization_score'] for d in recent_decisions])
        }
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Analyze scheduler metrics
        if self.scheduler_metrics['total_decisions'] > 0:
            prevention_rate = (self.scheduler_metrics['sla_violations_prevented'] / self.scheduler_metrics['total_decisions']) * 100
            
            if prevention_rate > 30:
                recommendations.append("🎯 Excellent SLA violation prevention rate")
            elif prevention_rate < 10:
                recommendations.append("⚠️ Low SLA violation prevention - consider adjusting risk thresholds")
        
        # VM pool recommendations
        if len(self.vm_pool) < 3:
            recommendations.append("💡 Consider adding more VMs to improve resource optimization options")
        
        # Compliance recommendations
        current_compliance = calculate_sla_compliance()
        if current_compliance.get('weighted_compliance', 100) < 90:
            recommendations.append("🚨 SLA compliance below 90% - immediate attention required")
        
        return recommendations

# Global advanced scheduler instance
advanced_scheduler = AdvancedIntegratedScheduler()

def schedule_task_with_advanced_layers(task: Dict) -> Optional[str]:
    """
    Convenience function for advanced task scheduling
    
    Integrates:
    1. SLA Risk Score Assessment
    2. Resource Optimization Score for VM Selection  
    3. SLA Compliance Tracking
    """
    return advanced_scheduler.schedule_task(task)

def get_advanced_scheduler_status() -> Dict:
    """Get comprehensive advanced scheduler status"""
    return advanced_scheduler.get_scheduler_status()
