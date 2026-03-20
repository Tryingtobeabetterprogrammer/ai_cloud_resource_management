"""
Resource Optimization Score Module
Multi-criteria VM selection instead of simple load-based selection
"""

import numpy as np
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class ResourceOptimizationScore:
    """Advanced VM selection with multi-parameter optimization scoring"""
    
    def __init__(self):
        # Optimization weights tuned for 90-99% SLA compliance
        self.optimization_weights = {
            'cpu_free_weight': 0.45,     # More focus on CPU availability
            'memory_free_weight': 0.35,   # Good memory consideration
            'latency_penalty_weight': 0.2 # Reduced latency penalty for better distribution
        }
        
        # VM performance history for learning
        self.vm_performance_history = {}
        
    def select_best_vm(self, vms: List[Dict]) -> Optional[Dict]:
        """
        Select best VM using multi-criteria optimization score
        
        Score formula: score = (0.5 * cpu_free) + (0.3 * mem_free) - (0.2 * latency)
        """
        if not vms:
            return None
        
        best_vm = None
        best_score = -float('inf')
        vm_scores = []
        
        for vm in vms:
            score = self._calculate_vm_score(vm)
            vm_scores.append({
                'vm_id': vm.get('id', 'unknown'),
                'score': score,
                'components': self._get_score_components(vm)
            })
            
            if score > best_score:
                best_score = score
                best_vm = vm.copy()
                best_vm['optimization_score'] = score
                best_vm['selection_reason'] = self._get_selection_reason(vm)
        
        # Store scores for analysis
        self._store_vm_scores(vm_scores)
        
        return best_vm
    
    def _calculate_vm_score(self, vm: Dict) -> float:
        """Calculate optimization score for a single VM"""
        # Extract VM metrics
        cpu_usage = vm.get('cpu_usage', 0)
        memory_usage = vm.get('memory_usage', 0)
        latency = vm.get('latency', 0)
        cpu_capacity = vm.get('cpu_capacity', 100)
        memory_capacity = vm.get('memory_capacity', 100)
        
        # Calculate available resources
        cpu_free = (cpu_capacity - cpu_usage) / cpu_capacity * 100
        memory_free = (memory_capacity - memory_usage) / memory_capacity * 100
        
        # Normalize latency (lower is better, so we subtract)
        normalized_latency = min(latency / 100, 1.0)  # Assume 100ms as baseline
        
        # Calculate weighted score
        score = (
            self.optimization_weights['cpu_free_weight'] * cpu_free +
            self.optimization_weights['memory_free_weight'] * memory_free -
            self.optimization_weights['latency_penalty_weight'] * normalized_latency
        )
        
        return max(score, 0)  # Ensure non-negative
    
    def _get_score_components(self, vm: Dict) -> Dict:
        """Get individual score components for analysis"""
        cpu_usage = vm.get('cpu_usage', 0)
        memory_usage = vm.get('memory_usage', 0)
        latency = vm.get('latency', 0)
        cpu_capacity = vm.get('cpu_capacity', 100)
        memory_capacity = vm.get('memory_capacity', 100)
        
        cpu_free = (cpu_capacity - cpu_usage) / cpu_capacity * 100
        memory_free = (memory_capacity - memory_usage) / memory_capacity * 100
        normalized_latency = min(latency / 100, 1.0)
        
        return {
            'cpu_free_percent': cpu_free,
            'memory_free_percent': memory_free,
            'latency_penalty': normalized_latency,
            'raw_cpu_usage': cpu_usage,
            'raw_memory_usage': memory_usage,
            'raw_latency': latency
        }
    
    def _get_selection_reason(self, vm: Dict) -> str:
        """Generate human-readable selection reason"""
        components = self._get_score_components(vm)
        
        reasons = []
        if components['cpu_free_percent'] > 50:
            reasons.append(f"High CPU availability ({components['cpu_free_percent']:.1f}%)")
        if components['memory_free_percent'] > 50:
            reasons.append(f"High memory availability ({components['memory_free_percent']:.1f}%)")
        if components['latency_penalty'] < 0.3:
            reasons.append(f"Low latency ({components['raw_latency']:.1f}ms)")
        
        return "; ".join(reasons) if reasons else "Balanced resource availability"
    
    def _store_vm_scores(self, vm_scores: List[Dict]):
        """Store VM scores for learning and analysis"""
        for vm_score in vm_scores:
            vm_id = vm_score['vm_id']
            if vm_id not in self.vm_performance_history:
                self.vm_performance_history[vm_id] = []
            
            self.vm_performance_history[vm_id].append({
                'timestamp': datetime.now(),
                'score': vm_score['score'],
                'components': vm_score['components']
            })
            
            # Keep history manageable
            if len(self.vm_performance_history[vm_id]) > 100:
                self.vm_performance_history[vm_id] = self.vm_performance_history[vm_id][-100:]
    
    def rank_all_vms(self, vms: List[Dict]) -> List[Dict]:
        """Rank all VMs by optimization score"""
        scored_vms = []
        
        for vm in vms:
            score = self._calculate_vm_score(vm)
            scored_vms.append({
                'vm': vm,
                'optimization_score': score,
                'rank': 0,  # Will be set after sorting
                'selection_reason': self._get_selection_reason(vm)
            })
        
        # Sort by score (descending)
        scored_vms.sort(key=lambda x: x['optimization_score'], reverse=True)
        
        # Assign ranks
        for i, vm_data in enumerate(scored_vms):
            vm_data['rank'] = i + 1
        
        return scored_vms
    
    def get_optimization_insights(self) -> Dict:
        """Get insights from VM selection history"""
        if not self.vm_performance_history:
            return {'status': 'NO_DATA'}
        
        insights = {
            'total_vms_evaluated': len(self.vm_performance_history),
            'vm_performance': {},
            'selection_patterns': {}
        }
        
        # Average performance per VM
        for vm_id, history in self.vm_performance_history.items():
            if history:
                scores = [entry['score'] for entry in history]
                insights['vm_performance'][vm_id] = {
                    'average_score': np.mean(scores),
                    'max_score': max(scores),
                    'min_score': min(scores),
                    'selection_count': len(history),
                    'score_std': np.std(scores)
                }
        
        return insights
    
    def adaptive_weight_optimization(self, performance_feedback: Dict):
        """Adapt weights based on performance feedback"""
        # Simple adaptive learning based on success rates
        if performance_feedback.get('cpu_efficiency', 0) < 0.7:
            # Increase CPU weight if CPU efficiency is low
            self.optimization_weights['cpu_free_weight'] = min(
                self.optimization_weights['cpu_free_weight'] * 1.1, 0.8
            )
        
        if performance_feedback.get('memory_efficiency', 0) < 0.7:
            # Increase memory weight if memory efficiency is low
            self.optimization_weights['memory_free_weight'] = min(
                self.optimization_weights['memory_free_weight'] * 1.1, 0.8
            )
        
        # Normalize weights to sum to 1.0
        total_weight = sum(self.optimization_weights.values())
        for key in self.optimization_weights:
            self.optimization_weights[key] /= total_weight

# Global optimizer instance
resource_optimizer = ResourceOptimizationScore()

def select_best_vm(vms: List[Dict]) -> Optional[Dict]:
    """
    Convenience function for VM selection
    
    Uses multi-criteria optimization instead of simple load-based selection
    """
    return resource_optimizer.select_best_vm(vms)

def calculate_vm_optimization_score(vm: Dict) -> float:
    """
    Calculate optimization score for a single VM
    
    Score formula: score = (0.5 * cpu_free) + (0.3 * mem_free) - (0.2 * latency)
    """
    return resource_optimizer._calculate_vm_score(vm)
