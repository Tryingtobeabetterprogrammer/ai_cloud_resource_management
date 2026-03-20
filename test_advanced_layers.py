#!/usr/bin/env python3
"""Test script for advanced layers"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing SLA Risk Score...")
    from advanced_layers.sla_risk_score import calculate_sla_risk
    risk = calculate_sla_risk(75, 80, 120, 60)
    print(f"✅ SLA Risk Score: {risk['risk_score']:.3f}")
    
    print("\nTesting Resource Optimization...")
    from advanced_layers.resource_optimization import select_best_vm
    vms = [
        {'id': 'vm-1', 'cpu_capacity': 100, 'memory_capacity': 100, 'cpu_usage': 30, 'memory_usage': 40, 'latency': 50},
        {'id': 'vm-2', 'cpu_capacity': 100, 'memory_capacity': 100, 'cpu_usage': 60, 'memory_usage': 70, 'latency': 80}
    ]
    best_vm = select_best_vm(vms)
    print(f"✅ Best VM: {best_vm['id']} (Score: {best_vm['optimization_score']:.3f})")
    
    print("\nTesting SLA Compliance Tracking...")
    from advanced_layers.sla_compliance_tracking import calculate_sla_compliance
    compliance = calculate_sla_compliance()
    print(f"✅ Compliance: {compliance.get('overall_compliance', 0):.1f}%")
    
    print("\n🎯 All Advanced Layers Working Successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
