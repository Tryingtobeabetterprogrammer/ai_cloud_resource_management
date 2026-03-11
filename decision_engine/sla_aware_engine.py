import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from ml_model.sla_prediction_model import SLAViolationPredictor
from utils.ai_scaler import predict_servers
import joblib

class SLAAwareDecisionEngine:
    def __init__(self):
        self.sla_predictor = SLAViolationPredictor()
        try:
            self.sla_predictor.load_model("ml_model/sla_violation_model.pkl")
            print("✅ SLA prediction model loaded successfully")
        except FileNotFoundError:
            print("⚠️  SLA model not found, training new model...")
            from ml_model.sla_prediction_model import train_sla_model
            predictor, accuracy = train_sla_model()
            self.sla_predictor = predictor
            print(f"✅ SLA model trained with accuracy: {accuracy:.4f}")
        
        # SLA thresholds and constraints
        self.sla_thresholds = {
            'max_response_time': 100,  # ms
            'max_cpu_usage': 80,       # percentage
            'max_memory_usage': 85,    # percentage
            'min_uptime': 99.0,        # percentage
            'max_cost_per_hour': 10.0, # dollars
            'safety_margin': 20         # extra capacity percentage
        }
        
        # Decision weights
        self.decision_weights = {
            'sla_compliance': 0.4,
            'cost_efficiency': 0.25,
            'resource_utilization': 0.2,
            'performance': 0.15
        }
        
    def analyze_current_state(self, metrics: Dict) -> Dict:
        """Analyze current system state and identify potential issues"""
        analysis = {
            'cpu_critical': metrics.get('cpu_usage', 0) > self.sla_thresholds['max_cpu_usage'],
            'memory_critical': metrics.get('memory_usage', 0) > self.sla_thresholds['max_memory_usage'],
            'response_critical': metrics.get('response_time', 0) > self.sla_thresholds['max_response_time'],
            'uptime_critical': metrics.get('uptime_percentage', 100) < self.sla_thresholds['min_uptime'],
            'cost_critical': metrics.get('cost_per_hour', 0) > self.sla_thresholds['max_cost_per_hour'],
            'utilization_high': (metrics.get('requests', 0) / metrics.get('capacity', 1)) > 0.9,
            'utilization_low': (metrics.get('requests', 0) / metrics.get('capacity', 1)) < 0.3
        }
        
        # Calculate risk score
        risk_factors = [
            analysis['cpu_critical'],
            analysis['memory_critical'],
            analysis['response_critical'],
            analysis['uptime_critical'],
            analysis['utilization_high']
        ]
        analysis['risk_score'] = sum(risk_factors) / len(risk_factors)
        
        return analysis
    
    def predict_sla_risk(self, metrics: Dict) -> Dict:
        """Predict SLA violation risk for current metrics"""
        try:
            prediction = self.sla_predictor.predict_sla_violation(metrics)
            return prediction
        except Exception as e:
            print(f"SLA prediction error: {e}")
            return {
                'sla_violation': 0,
                'violation_probability': 0.1,
                'normal_probability': 0.9
            }
    
    def evaluate_scaling_options(self, current_metrics: Dict) -> List[Dict]:
        """Evaluate different scaling options with SLA awareness"""
        current_servers = current_metrics.get('servers', 1)
        server_capacity = current_metrics.get('capacity', 50) // current_servers
        requests = current_metrics.get('requests', 0)
        
        options = []
        
        # Generate scaling options: scale down, keep, scale up, scale up more
        scaling_factors = [-1, 0, 1, 2]
        
        for factor in scaling_factors:
            new_servers = max(1, current_servers + factor)
            new_capacity = new_servers * server_capacity
            
            # Calculate metrics for this option
            option_metrics = current_metrics.copy()
            option_metrics.update({
                'servers': new_servers,
                'capacity': new_capacity,
                'cost_per_hour': new_servers * 1.25  # Assume $1.25 per server per hour
            })
            
            # Predict SLA risk
            sla_risk = self.predict_sla_risk(option_metrics)
            
            # Calculate scores
            sla_score = 1 - sla_risk['violation_probability']
            cost_score = 1 - (option_metrics['cost_per_hour'] / self.sla_thresholds['max_cost_per_hour'])
            utilization_score = min(requests / new_capacity, 1.0) if new_capacity > 0 else 0
            performance_score = 1 - (option_metrics.get('response_time', 50) / self.sla_thresholds['max_response_time'])
            
            # Normalize scores
            cost_score = max(0, min(1, cost_score))
            performance_score = max(0, min(1, performance_score))
            
            # Calculate weighted score
            total_score = (
                sla_score * self.decision_weights['sla_compliance'] +
                cost_score * self.decision_weights['cost_efficiency'] +
                utilization_score * self.decision_weights['resource_utilization'] +
                performance_score * self.decision_weights['performance']
            )
            
            options.append({
                'servers': new_servers,
                'capacity': new_capacity,
                'cost_per_hour': option_metrics['cost_per_hour'],
                'sla_violation_risk': sla_risk['violation_probability'],
                'utilization': utilization_score,
                'total_score': total_score,
                'action': self._get_action_description(factor, current_servers)
            })
        
        return sorted(options, key=lambda x: x['total_score'], reverse=True)
    
    def _get_action_description(self, factor: int, current_servers: int) -> str:
        """Get human-readable action description"""
        if factor == -1:
            return f"Scale down to {current_servers - 1} servers"
        elif factor == 0:
            return f"Maintain {current_servers} servers"
        elif factor == 1:
            return f"Scale up to {current_servers + 1} servers"
        elif factor == 2:
            return f"Scale up to {current_servers + 2} servers"
        else:
            return "Unknown action"
    
    def make_decision(self, current_metrics: Dict) -> Dict:
        """Make SLA-aware resource allocation decision"""
        # Analyze current state
        state_analysis = self.analyze_current_state(current_metrics)
        
        # Evaluate scaling options
        options = self.evaluate_scaling_options(current_metrics)
        
        # Select best option
        best_option = options[0] if options else None
        
        # Safety check: if high risk, force scale up
        if state_analysis['risk_score'] > 0.6 or best_option['sla_violation_risk'] > 0.3:
            # Find scale-up option with lowest risk
            scale_up_options = [opt for opt in options if opt['servers'] > current_metrics['servers']]
            if scale_up_options:
                best_option = min(scale_up_options, key=lambda x: x['sla_violation_risk'])
        
        decision = {
            'current_state': state_analysis,
            'recommended_action': best_option['action'] if best_option else 'No action',
            'recommended_servers': best_option['servers'] if best_option else current_metrics['servers'],
            'expected_capacity': best_option['capacity'] if best_option else current_metrics['capacity'],
            'expected_cost': best_option['cost_per_hour'] if best_option else current_metrics.get('cost_per_hour', 0),
            'sla_violation_risk': best_option['sla_violation_risk'] if best_option else 0.0,
            'confidence_score': best_option['total_score'] if best_option else 0.0,
            'all_options': options
        }
        
        return decision
    
    def get_resource_allocation_plan(self, current_metrics: Dict, forecast_requests: List[int]) -> Dict:
        """Create a resource allocation plan for forecasted requests"""
        plan = {
            'current_metrics': current_metrics,
            'forecast_periods': [],
            'recommendations': []
        }
        
        for i, future_requests in enumerate(forecast_requests):
            future_metrics = current_metrics.copy()
            future_metrics['requests'] = future_requests
            
            decision = self.make_decision(future_metrics)
            
            plan['forecast_periods'].append({
                'period': i + 1,
                'predicted_requests': future_requests,
                'recommended_servers': decision['recommended_servers'],
                'sla_violation_risk': decision['sla_violation_risk'],
                'estimated_cost': decision['expected_cost']
            })
        
        # Generate overall recommendations
        max_servers = max(period['recommended_servers'] for period in plan['forecast_periods'])
        avg_cost = np.mean([period['estimated_cost'] for period in plan['forecast_periods']])
        
        plan['recommendations'] = [
            f"Maintain minimum {max_servers} servers for the forecast period",
            f"Expected average cost: ${avg_cost:.2f} per hour",
            f"Monitor SLA violations closely during peak demand"
        ]
        
        return plan

# Global decision engine instance
decision_engine = SLAAwareDecisionEngine()

def make_sla_aware_decision(metrics: Dict) -> Dict:
    """Convenience function for making SLA-aware decisions"""
    return decision_engine.make_decision(metrics)
