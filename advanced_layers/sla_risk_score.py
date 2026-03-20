"""
Advanced SLA Risk Assessment Module
Multi-dimensional SLA risk scoring instead of simple thresholds
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class SLARiskScoreModel:
    """Advanced SLA Risk Score Model with multi-factor assessment"""
    
    def __init__(self):
        # Risk weights - can be tuned based on business requirements
        self.risk_weights = {
            'cpu_weight': 0.3,      # 30% weight to CPU usage
            'memory_weight': 0.3,    # 30% weight to memory usage  
            'latency_weight': 0.2,    # 20% weight to latency
            'load_weight': 0.2         # 20% weight to VM load
        }
        
        # Risk thresholds for better SLA compliance
        self.risk_thresholds = {
            'minimal': 0.1,      # Stricter: was 0.2
            'low': 0.25,         # Stricter: was 0.4
            'medium': 0.4,       # Stricter: was 0.6
            'high': 0.6,         # Stricter: was 0.8
            'critical': 0.8      # Stricter: was 1.0
        }
        
        # Metric thresholds for normalization
        self.thresholds = {
            'cpu_max': 100,         # Maximum CPU percentage
            'memory_max': 100,      # Maximum memory percentage
            'latency_max': 300,     # Maximum latency in ms
            'load_max': 100         # Maximum VM load percentage
        }
        
        # Historical risk data for trend analysis
        self.risk_history = []
        self.max_history_size = 100
        
    def calculate_sla_risk(self, cpu: float, memory: float, latency: float, vm_load: float) -> Dict:
        """
        Calculate SLA Risk Score using multiple metrics
        
        Formula: risk = (0.3 * cpu/100) + (0.3 * memory/100) + (0.2 * latency/300) + (0.2 * vm_load/100)
        """
        # Normalize each metric to 0-1 range
        cpu_risk = min(cpu / self.thresholds['cpu_max'], 1.0)
        memory_risk = min(memory / self.thresholds['memory_max'], 1.0)
        latency_risk = min(latency / self.thresholds['latency_max'], 1.0)
        load_risk = min(vm_load / self.thresholds['load_max'], 1.0)
        
        # Calculate weighted risk score
        risk_score = (
            self.risk_weights['cpu_weight'] * cpu_risk +
            self.risk_weights['memory_weight'] * memory_risk +
            self.risk_weights['latency_weight'] * latency_risk +
            self.risk_weights['load_weight'] * load_risk
        )
        
        # Determine risk level
        if risk_score > 0.8:
            risk_level = "CRITICAL"
        elif risk_score > 0.6:
            risk_level = "HIGH"
        elif risk_score > 0.4:
            risk_level = "MEDIUM"
        elif risk_score > 0.2:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        # Store in history for trend analysis
        self._store_risk_history(risk_score, {
            'cpu': cpu, 'memory': memory, 'latency': latency, 'vm_load': vm_load
        })
        
        component_risks = {
            'cpu_risk': cpu_risk,
            'memory_risk': memory_risk,
            'latency_risk': latency_risk,
            'load_risk': load_risk
        }
        
        recommendations = self._generate_risk_recommendations(risk_score, cpu_risk, memory_risk, latency_risk, load_risk)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'component_risks': component_risks,
            'recommendations': recommendations,
            'thresholds': self.risk_thresholds,
            'trend': self._analyze_risk_trend() if len(self.risk_history) > 1 else 'INSUFFICIENT_DATA'
        }
    
    def _store_risk_history(self, risk_score: float, metrics: Dict):
        """Store risk score in history for trend analysis"""
        self.risk_history.append({
            'timestamp': datetime.now(),
            'risk_score': risk_score,
            'metrics': metrics
        })
        
        # Keep history size manageable
        if len(self.risk_history) > self.max_history_size:
            self.risk_history = self.risk_history[-self.max_history_size:]
    
    def _analyze_risk_trend(self) -> Dict:
        """Analyze risk trend over time"""
        if len(self.risk_history) < 5:
            return {'trend': 'INSUFFICIENT_DATA', 'direction': 0}
        
        recent_scores = [entry['risk_score'] for entry in self.risk_history[-10:]]
        older_scores = [entry['risk_score'] for entry in self.risk_history[-20:-10]] if len(self.risk_history) >= 20 else recent_scores[:5]
        
        recent_avg = np.mean(recent_scores)
        older_avg = np.mean(older_scores)
        
        trend_direction = recent_avg - older_avg
        
        if trend_direction > 0.1:
            trend = 'DETERIORATING'
        elif trend_direction < -0.1:
            trend = 'IMPROVING'
        else:
            trend = 'STABLE'
        
        return {
            'trend': trend,
            'direction': trend_direction,
            'recent_average': recent_avg,
            'older_average': older_avg
        }
    
    def _generate_risk_recommendations(self, risk_score: float, cpu_risk: float, 
                                   memory_risk: float, latency_risk: float, load_risk: float) -> List[str]:
        """Generate recommendations based on risk factors"""
        recommendations = []
        
        if risk_score > 0.6:
            recommendations.append("🚨 High SLA Risk → redistribute load immediately")
        elif risk_score > 0.4:
            recommendations.append("⚠️ Medium SLA Risk → monitor closely")
        else:
            recommendations.append("✅ Low SLA Risk → normal operation")
        
        # Specific component recommendations
        if cpu_risk > 0.7:
            recommendations.append("💻 High CPU usage → scale up or optimize CPU-intensive tasks")
        if memory_risk > 0.7:
            recommendations.append("🧠 High memory usage → add memory or optimize memory usage")
        if latency_risk > 0.7:
            recommendations.append("⏱️ High latency → optimize network or move to closer server")
        if load_risk > 0.7:
            recommendations.append("📊 High VM load → distribute tasks across more VMs")
        
        return recommendations
    
    def get_risk_summary(self) -> Dict:
        """Get comprehensive risk summary"""
        if not self.risk_history:
            return {'status': 'NO_DATA'}
        
        current_risk = self.risk_history[-1]['risk_score']
        trend = self._analyze_risk_trend()
        
        return {
            'current_risk_score': current_risk,
            'current_risk_level': self.risk_history[-1].get('risk_level', 'UNKNOWN'),
            'trend_analysis': trend,
            'historical_stats': {
                'average_risk': np.mean([entry['risk_score'] for entry in self.risk_history]),
                'max_risk': max([entry['risk_score'] for entry in self.risk_history]),
                'min_risk': min([entry['risk_score'] for entry in self.risk_history]),
                'data_points': len(self.risk_history)
            }
        }

# Global risk model instance
sla_risk_model = SLARiskScoreModel()

def calculate_sla_risk(cpu: float, memory: float, latency: float, vm_load: float) -> Dict:
    """
    Convenience function for SLA risk calculation
    
    Formula: risk = (0.3 * cpu/100) + (0.3 * memory/100) + (0.2 * latency/300) + (0.2 * vm_load/100)
    """
    return sla_risk_model.calculate_sla_risk(cpu, memory, latency, vm_load)
