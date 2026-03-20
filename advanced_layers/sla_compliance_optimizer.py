"""
SLA Compliance Optimizer
Optimizes system parameters to achieve 90-99% SLA compliance
"""

import numpy as np
from typing import Dict, List, Tuple
from advanced_layers.sla_risk_score import calculate_sla_risk
from advanced_layers.resource_optimization import select_best_vm
from advanced_layers.sla_compliance_tracking import calculate_sla_compliance

class SLAComplianceOptimizer:
    """Optimizes system for 90-99% SLA compliance"""
    
    def __init__(self):
        self.target_compliance = 95.0  # Target 95% compliance
        self.optimization_history = []
        
    def optimize_for_target_compliance(self, current_metrics: Dict) -> Dict:
        """Optimize system to achieve target SLA compliance"""
        
        # Calculate current risk
        current_risk = calculate_sla_risk(
            current_metrics.get('cpu_usage', 0),
            current_metrics.get('memory_usage', 0),
            current_metrics.get('response_time', 0),
            current_metrics.get('cpu_usage', 0)  # VM load proxy
        )
        
        # Calculate current compliance
        current_compliance = calculate_sla_compliance()
        compliance_rate = current_compliance.get('overall_compliance', 100)
        
        # Optimization recommendations
        recommendations = []
        
        if compliance_rate < 90:
            recommendations.extend(self._get_critical_improvements(current_risk, current_metrics))
        elif compliance_rate < 95:
            recommendations.extend(self._get_moderate_improvements(current_risk, current_metrics))
        elif compliance_rate < 99:
            recommendations.extend(self._get_minor_improvements(current_risk, current_metrics))
        
        # Calculate optimized parameters
        optimized_params = self._calculate_optimized_parameters(current_metrics, current_risk)
        
        return {
            'current_compliance': compliance_rate,
            'target_compliance': self.target_compliance,
            'current_risk': current_risk,
            'recommendations': recommendations,
            'optimized_parameters': optimized_params,
            'expected_improvement': self._estimate_improvement(current_metrics, optimized_params)
        }
    
    def _get_critical_improvements(self, risk: Dict, metrics: Dict) -> List[str]:
        """Get critical improvements for <90% compliance"""
        improvements = []
        
        if risk['risk_score'] > 0.7:
            improvements.append("🚨 CRITICAL: Scale up immediately - add 2-3 more servers")
            improvements.append("🔄 Redistribute all tasks to less loaded VMs")
            improvements.append("⚡ Enable aggressive auto-scaling")
        
        if metrics.get('cpu_usage', 0) > 80:
            improvements.append("💻 CPU critical - add 50% more CPU capacity")
        
        if metrics.get('memory_usage', 0) > 85:
            improvements.append("🧠 Memory critical - add 50% more memory")
        
        if metrics.get('response_time', 0) > 120:
            improvements.append("⏱️ Response time critical - optimize code and add cache")
        
        return improvements
    
    def _get_moderate_improvements(self, risk: Dict, metrics: Dict) -> List[str]:
        """Get moderate improvements for 90-95% compliance"""
        improvements = []
        
        if risk['risk_score'] > 0.5:
            improvements.append("⚠️ Scale up by 1-2 servers")
            improvements.append("🔄 Redistribute high-priority tasks")
        
        if metrics.get('cpu_usage', 0) > 70:
            improvements.append("💻 Increase CPU capacity by 25%")
        
        if metrics.get('memory_usage', 0) > 75:
            improvements.append("🧠 Increase memory by 25%")
        
        if metrics.get('response_time', 0) > 100:
            improvements.append("⏱️ Optimize response time - add caching")
        
        return improvements
    
    def _get_minor_improvements(self, risk: Dict, metrics: Dict) -> List[str]:
        """Get minor improvements for 95-99% compliance"""
        improvements = []
        
        if risk['risk_score'] > 0.3:
            improvements.append("📊 Monitor closely - consider scaling up 1 server")
            improvements.append("🎯 Optimize task distribution")
        
        if metrics.get('cpu_usage', 0) > 60:
            improvements.append("💻 Consider 10% more CPU capacity")
        
        if metrics.get('memory_usage', 0) > 65:
            improvements.append("🧠 Consider 10% more memory")
        
        return improvements
    
    def _calculate_optimized_parameters(self, current_metrics: Dict, risk: Dict) -> Dict:
        """Calculate optimized parameters for better SLA compliance"""
        
        current_cpu = current_metrics.get('cpu_usage', 0)
        current_memory = current_metrics.get('memory_usage', 0)
        current_servers = current_metrics.get('servers', 1)
        
        # Calculate optimal server count
        if risk['risk_score'] > 0.7:
            optimal_servers = current_servers + 2
        elif risk['risk_score'] > 0.5:
            optimal_servers = current_servers + 1
        elif risk['risk_score'] > 0.3:
            optimal_servers = max(current_servers, int(current_servers * 1.2))
        else:
            optimal_servers = current_servers
        
        # Calculate optimal capacity
        requests = current_metrics.get('requests', 0)
        optimal_capacity = int(requests * 1.3)  # 30% safety margin
        
        return {
            'optimal_servers': optimal_servers,
            'optimal_capacity': optimal_capacity,
            'target_cpu_usage': max(50, current_cpu * 0.8),  # Reduce by 20%
            'target_memory_usage': max(50, current_memory * 0.8),  # Reduce by 20%
            'target_response_time': 80,  # Target 80ms
            'safety_margin': 30  # 30% safety margin
        }
    
    def _estimate_improvement(self, current_metrics: Dict, optimized_params: Dict) -> Dict:
        """Estimate improvement with optimized parameters"""
        
        current_requests = current_metrics.get('requests', 0)
        current_capacity = current_metrics.get('capacity', 0)
        current_servers = current_metrics.get('servers', 1)
        
        optimized_capacity = optimized_params['optimal_capacity']
        optimized_servers = optimized_params['optimal_servers']
        
        # Calculate expected improvements
        capacity_improvement = ((optimized_capacity - current_capacity) / current_capacity * 100) if current_capacity > 0 else 0
        server_improvement = ((optimized_servers - current_servers) / current_servers * 100) if current_servers > 0 else 0
        
        # Estimate SLA compliance improvement
        current_compliance = calculate_sla_compliance().get('overall_compliance', 90)
        if capacity_improvement > 20:
            expected_compliance = min(99, current_compliance + 10)
        elif capacity_improvement > 10:
            expected_compliance = min(99, current_compliance + 5)
        else:
            expected_compliance = min(99, current_compliance + 2)
        
        return {
            'capacity_improvement_percent': capacity_improvement,
            'server_improvement_percent': server_improvement,
            'expected_compliance': expected_compliance,
            'improvement_confidence': 0.85  # 85% confidence in estimates
        }
    
    def generate_compliance_report(self) -> Dict:
        """Generate comprehensive SLA compliance report"""
        
        compliance = calculate_sla_compliance()
        
        return {
            'report_timestamp': str(np.datetime64('now')),
            'current_compliance': compliance.get('overall_compliance', 0),
            'target_compliance': self.target_compliance,
            'compliance_gap': self.target_compliance - compliance.get('overall_compliance', 0),
            'grade': compliance.get('compliance_grade', 'N/A'),
            'total_tasks': compliance.get('total_tasks', 0),
            'sla_violations': compliance.get('sla_violations', 0),
            'violation_rate': (compliance.get('sla_violations', 0) / max(1, compliance.get('total_tasks', 1))) * 100,
            'metric_breakdown': compliance.get('metric_compliance', {}),
            'recommendations': self._get_compliance_recommendations(compliance),
            'optimization_suggestions': self._get_optimization_suggestions(compliance)
        }
    
    def _get_compliance_recommendations(self, compliance: Dict) -> List[str]:
        """Get specific compliance recommendations"""
        recommendations = []
        compliance_rate = compliance.get('overall_compliance', 0)
        
        if compliance_rate < 90:
            recommendations.append("🚨 URGENT: System needs immediate optimization")
            recommendations.append("📈 Scale up resources by 50-100%")
            recommendations.append("🔄 Redistribute all active tasks")
        elif compliance_rate < 95:
            recommendations.append("⚠️ Monitor system closely")
            recommendations.append("📊 Consider scaling up by 25%")
            recommendations.append("🎯 Optimize task scheduling")
        elif compliance_rate < 99:
            recommendations.append("✅ Good performance with room for improvement")
            recommendations.append("🔍 Fine-tune resource allocation")
            recommendations.append("📈 Consider minor scaling adjustments")
        else:
            recommendations.append("🎉 EXCELLENT: Target achieved!")
            recommendations.append("📊 Maintain current performance")
            recommendations.append("🔍 Continue monitoring")
        
        return recommendations
    
    def _get_optimization_suggestions(self, compliance: Dict) -> List[str]:
        """Get optimization suggestions for better compliance"""
        suggestions = []
        
        # Analyze metric compliance
        metric_compliance = compliance.get('metric_compliance', {})
        
        for metric, data in metric_compliance.items():
            compliance_rate = data.get('compliance_percentage', 0)
            if compliance_rate < 90:
                suggestions.append(f"📊 {metric.replace('_', ' ').title()}: Improve by {100 - compliance_rate:.1f}%")
        
        return suggestions

# Global optimizer instance
sla_compliance_optimizer = SLAComplianceOptimizer()

def optimize_sla_compliance(current_metrics: Dict) -> Dict:
    """Optimize system for 90-99% SLA compliance"""
    return sla_compliance_optimizer.optimize_for_target_compliance(current_metrics)

def get_compliance_report() -> Dict:
    """Get comprehensive SLA compliance report"""
    return sla_compliance_optimizer.generate_compliance_report()
