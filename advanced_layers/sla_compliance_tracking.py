"""
SLA Compliance Tracking Module
Comprehensive SLA evaluation instead of just completion time
"""

import numpy as np
import time
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json

class SLAComplianceTracker:
    """Advanced SLA compliance tracking with multiple metrics"""
    
    def __init__(self):
        # SLA definitions for realistic compliance tracking
        self.sla_definitions = {
            'response_time': {
                'target': 120,           # More realistic: was 80ms
                'warning_threshold': 100,    # More realistic: was 60ms
                'critical_threshold': 150,   # More realistic: was 120ms
                'weight': 0.4              # 40% weight in overall compliance
            },
            'availability': {
                'target': 99.95,         # Stricter: was 99.9%
                'warning_threshold': 99.9,  # Stricter: was 99.5%
                'critical_threshold': 99.85,   # Stricter: was 99.0%
                'weight': 0.3              # 30% weight in overall compliance
            },
            'throughput': {
                'target': 1200,           # Higher: was 1000 rps
                'warning_threshold': 1000,     # Higher: was 800 rps
                'critical_threshold': 800,     # Higher: was 600 rps
                'weight': 0.2              # 20% weight in overall compliance
            },
            'error_rate': {
                'target': 0.005,           # Stricter: was 1% (0.01)
                'warning_threshold': 0.01,     # Stricter: was 2%
                'critical_threshold': 0.02,     # Stricter: was 5%
                'weight': 0.1              # 10% weight in overall compliance
            }
        }
        
        # Compliance tracking data
        self.compliance_data = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'sla_violations': 0,
            'metrics_history': [],
            'violation_details': []
        }
        
        # Current metrics
        self.current_metrics = {
            'response_time_samples': [],
            'availability_samples': [],
            'throughput_samples': [],
            'error_samples': []
        }
        
    def record_task_completion(self, completion_time: float, success: bool = True, 
                          response_time: float = None, availability: float = None,
                          throughput: float = None, error_rate: float = None):
        """Record task completion with comprehensive metrics"""
        self.compliance_data['total_tasks'] += 1
        
        if success:
            self.compliance_data['completed_tasks'] += 1
        else:
            self.compliance_data['sla_violations'] += 1
            self.compliance_data['violation_details'].append({
                'timestamp': datetime.now(),
                'completion_time': completion_time,
                'violation_type': 'task_failure',
                'metrics_at_violation': {
                    'response_time': response_time,
                    'availability': availability,
                    'throughput': throughput,
                    'error_rate': error_rate
                }
            })
        
        # Check SLA violations for each metric
        self._check_sla_violations(completion_time, response_time, availability, throughput, error_rate)
        
        # Store in history
        self._store_metrics_sample(response_time, availability, throughput, error_rate)
    
    def _check_sla_violations(self, completion_time: float, response_time: float = None,
                               availability: float = None, throughput: float = None, error_rate: float = None):
        """Check SLA violations for all metrics"""
        
        # Response time SLA
        if response_time is not None:
            if completion_time > self.sla_definitions['response_time']['target']:
                self.compliance_data['sla_violations'] += 1
                self.compliance_data['violation_details'].append({
                    'timestamp': datetime.now(),
                    'violation_type': 'response_time',
                    'actual_value': response_time,
                    'target_value': self.sla_definitions['response_time']['target'],
                    'severity': self._get_severity_level('response_time', response_time)
                })
        
        # Availability SLA
        if availability is not None:
            if availability < self.sla_definitions['availability']['target']:
                self.compliance_data['sla_violations'] += 1
                self.compliance_data['violation_details'].append({
                    'timestamp': datetime.now(),
                    'violation_type': 'availability',
                    'actual_value': availability,
                    'target_value': self.sla_definitions['availability']['target'],
                    'severity': self._get_severity_level('availability', availability)
                })
        
        # Throughput SLA
        if throughput is not None:
            if throughput < self.sla_definitions['throughput']['target']:
                self.compliance_data['sla_violations'] += 1
                self.compliance_data['violation_details'].append({
                    'timestamp': datetime.now(),
                    'violation_type': 'throughput',
                    'actual_value': throughput,
                    'target_value': self.sla_definitions['throughput']['target'],
                    'severity': self._get_severity_level('throughput', throughput)
                })
        
        # Error rate SLA
        if error_rate is not None:
            if error_rate > self.sla_definitions['error_rate']['target']:
                self.compliance_data['sla_violations'] += 1
                self.compliance_data['violation_details'].append({
                    'timestamp': datetime.now(),
                    'violation_type': 'error_rate',
                    'actual_value': error_rate,
                    'target_value': self.sla_definitions['error_rate']['target'],
                    'severity': self._get_severity_level('error_rate', error_rate)
                })
    
    def _get_severity_level(self, metric_type: str, actual_value: float) -> str:
        """Determine severity level for SLA violation"""
        sla_def = self.sla_definitions[metric_type]
        
        if actual_value >= sla_def['critical_threshold']:
            return 'CRITICAL'
        elif actual_value >= sla_def['warning_threshold']:
            return 'WARNING'
        else:
            return 'MINOR'
    
    def _store_metrics_sample(self, response_time: float = None, availability: float = None,
                           throughput: float = None, error_rate: float = None):
        """Store metrics samples for trend analysis"""
        if response_time is not None:
            self.current_metrics['response_time_samples'].append(response_time)
            if len(self.current_metrics['response_time_samples']) > 100:
                self.current_metrics['response_time_samples'] = self.current_metrics['response_time_samples'][-100:]
        
        if availability is not None:
            self.current_metrics['availability_samples'].append(availability)
            if len(self.current_metrics['availability_samples']) > 100:
                self.current_metrics['availability_samples'] = self.current_metrics['availability_samples'][-100:]
        
        if throughput is not None:
            self.current_metrics['throughput_samples'].append(throughput)
            if len(self.current_metrics['throughput_samples']) > 100:
                self.current_metrics['throughput_samples'] = self.current_metrics['throughput_samples'][-100:]
        
        if error_rate is not None:
            self.current_metrics['error_samples'].append(error_rate)
            if len(self.current_metrics['error_samples']) > 100:
                self.current_metrics['error_samples'] = self.current_metrics['error_samples'][-100:]
    
    def calculate_sla_compliance(self) -> Dict:
        """
        Calculate comprehensive SLA compliance
        
        Formula: sla_compliance = (1 - sla_violations/total_tasks) * 100
        Plus individual metric compliance scores
        """
        if self.compliance_data['total_tasks'] == 0:
            return {'overall_compliance': 100.0, 'status': 'NO_TASKS'}
        
        # Overall compliance (traditional)
        overall_compliance = (1 - self.compliance_data['sla_violations'] / self.compliance_data['total_tasks']) * 100
        
        # Individual metric compliance
        metric_compliance = {}
        
        for metric_name, sla_def in self.sla_definitions.items():
            samples = self.current_metrics[f'{metric_name}_samples']
            if samples:
                avg_value = np.mean(samples)
                
                # Calculate compliance percentage for this metric
                if metric_name in ['response_time', 'error_rate']:
                    # Lower is better for these metrics
                    compliance = max(0, min(100, (1 - avg_value / sla_def['target']) * 100))
                else:
                    # Higher is better for these metrics
                    compliance = max(0, min(100, (avg_value / sla_def['target']) * 100))
                
                metric_compliance[metric_name] = {
                    'average_value': avg_value,
                    'target_value': sla_def['target'],
                    'compliance_percentage': compliance,
                    'weight': sla_def['weight'],
                    'trend': self._calculate_metric_trend(samples)
                }
        
        # Weighted overall compliance
        weighted_compliance = 0
        total_weight = 0
        
        for metric_name, compliance_data in metric_compliance.items():
            weighted_score = compliance_data['compliance_percentage'] * compliance_data['weight']
            weighted_compliance += weighted_score
            total_weight += compliance_data['weight']
        
        final_weighted_compliance = weighted_compliance / total_weight if total_weight > 0 else 0
        
        return {
            'overall_compliance': overall_compliance,
            'weighted_compliance': final_weighted_compliance,
            'metric_compliance': metric_compliance,
            'total_tasks': self.compliance_data['total_tasks'],
            'completed_tasks': self.compliance_data['completed_tasks'],
            'sla_violations': self.compliance_data['sla_violations'],
            'compliance_grade': self._get_compliance_grade(final_weighted_compliance)
        }
    
    def _calculate_metric_trend(self, samples: List[float]) -> str:
        """Calculate trend for a metric"""
        if len(samples) < 10:
            return 'INSUFFICIENT_DATA'
        
        recent_avg = np.mean(samples[-10:])
        older_avg = np.mean(samples[-20:-10]) if len(samples) >= 20 else np.mean(samples[:10])
        
        if recent_avg > older_avg * 1.1:
            return 'DETERIORATING'
        elif recent_avg < older_avg * 0.9:
            return 'IMPROVING'
        else:
            return 'STABLE'
    
    def _get_compliance_grade(self, compliance_percentage: float) -> str:
        """Get letter grade for compliance percentage"""
        if compliance_percentage >= 99:
            return 'A+'
        elif compliance_percentage >= 95:
            return 'A'
        elif compliance_percentage >= 90:
            return 'B+'
        elif compliance_percentage >= 85:
            return 'B'
        elif compliance_percentage >= 80:
            return 'C+'
        elif compliance_percentage >= 75:
            return 'C'
        elif compliance_percentage >= 70:
            return 'D'
        else:
            return 'F'
    
    def get_violation_analysis(self) -> Dict:
        """Get detailed analysis of SLA violations"""
        if not self.compliance_data['violation_details']:
            return {'status': 'NO_VIOLATIONS'}
        
        # Group violations by type
        violation_counts = {}
        violation_severity = {'CRITICAL': 0, 'WARNING': 0, 'MINOR': 0}
        
        for violation in self.compliance_data['violation_details']:
            violation_type = violation['violation_type']
            severity = violation['severity']
            
            if violation_type not in violation_counts:
                violation_counts[violation_type] = 0
            violation_counts[violation_type] += 1
            violation_severity[severity] += 1
        
        # Calculate violation rates
        total_tasks = self.compliance_data['total_tasks']
        violation_rates = {}
        for violation_type, count in violation_counts.items():
            violation_rates[violation_type] = (count / total_tasks) * 100 if total_tasks > 0 else 0
        
        return {
            'total_violations': len(self.compliance_data['violation_details']),
            'violation_counts': violation_counts,
            'violation_rates': violation_rates,
            'severity_breakdown': violation_severity,
            'most_common_violation': max(violation_counts.items(), key=lambda x: x[1])[0] if violation_counts else None,
            'violation_trend': self._calculate_violation_trend()
        }
    
    def _calculate_violation_trend(self) -> str:
        """Calculate trend in violations over time"""
        if len(self.compliance_data['violation_details']) < 5:
            return 'INSUFFICIENT_DATA'
        
        # Group violations by time windows
        recent_violations = len([v for v in self.compliance_data['violation_details'] 
                                if v['timestamp'] > datetime.now() - timedelta(hours=1)])
        older_violations = len([v for v in self.compliance_data['violation_details'] 
                               if v['timestamp'] <= datetime.now() - timedelta(hours=1)])
        
        if recent_violations > older_violations * 1.2:
            return 'INCREASING'
        elif recent_violations < older_violations * 0.8:
            return 'DECREASING'
        else:
            return 'STABLE'
    
    def generate_compliance_report(self) -> Dict:
        """Generate comprehensive compliance report"""
        compliance = self.calculate_sla_compliance()
        violation_analysis = self.get_violation_analysis()
        
        return {
            'report_timestamp': datetime.now().isoformat(),
            'compliance_summary': compliance,
            'violation_analysis': violation_analysis,
            'recommendations': self._generate_compliance_recommendations(compliance, violation_analysis),
            'sla_definitions': self.sla_definitions
        }
    
    def _generate_compliance_recommendations(self, compliance: Dict, violation_analysis: Dict) -> List[str]:
        """Generate recommendations based on compliance analysis"""
        recommendations = []
        
        overall_compliance = compliance['weighted_compliance']
        
        if overall_compliance < 90:
            recommendations.append("🚨 CRITICAL: Overall SLA compliance below 90% - immediate action required")
        elif overall_compliance < 95:
            recommendations.append("⚠️ WARNING: SLA compliance below 95% - improvement needed")
        else:
            recommendations.append("✅ GOOD: SLA compliance is healthy")
        
        # Metric-specific recommendations
        for metric_name, metric_data in compliance['metric_compliance'].items():
            if metric_data['compliance_percentage'] < 90:
                recommendations.append(f"📊 {metric_name.replace('_', ' ').title()}: {metric_data['compliance_percentage']:.1f}% compliance - investigate")
        
        return recommendations

# Global compliance tracker instance
sla_compliance_tracker = SLAComplianceTracker()

def track_sla_compliance(completion_time: float, success: bool = True, 
                      response_time: float = None, availability: float = None,
                      throughput: float = None, error_rate: float = None):
    """Convenience function for SLA compliance tracking"""
    return sla_compliance_tracker.record_task_completion(completion_time, success, response_time, availability, throughput, error_rate)

def calculate_sla_compliance() -> Dict:
    """
    Calculate current SLA compliance
    
    Formula: sla_compliance = (1 - sla_violations/total_tasks) * 100
    Plus comprehensive metric analysis
    """
    return sla_compliance_tracker.calculate_sla_compliance()
