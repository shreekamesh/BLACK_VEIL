#!/usr/bin/env python3
"""
Test BLACK VEIL Encryption Enhancements
"""

import time
import json
from src.core.security import (
    DynamicAlgorithmSelector,
    RiskAdaptiveEncryption,
    KeyRotationManager,
    CommunicationSecurity,
    TimingSecurity,
    SecurityLevel,
    AlgorithmType
)

def test_dynamic_algorithm_selector():
    print("=" * 60)
    print("1. Testing Dynamic Algorithm Selector")
    print("=" * 60)
    
    selector = DynamicAlgorithmSelector()
    
    context = {
        'risk_score': 0.8,
        'trust_score': 0.3,
        'threat_level': 0.7,
        'hardware_acceleration': True,
        'high_throughput': False,
        'low_latency': True
    }
    
    recommendations = selector.get_recommended_algorithms(context)
    
    for algo_type, config in recommendations.items():
        print(f"{algo_type}: {config.name} (Key Size: {config.key_size})")
        print(f"  Performance: {config.performance_score:.2f}, Security: {config.security_score:.2f}")
    
    print()

def test_risk_adaptive_encryption():
    print("=" * 60)
    print("2. Testing Risk-Adaptive Encryption")
    print("=" * 60)
    
    adapter = RiskAdaptiveEncryption()
    
    contexts = [
        {'risk_score': 0.9, 'trust_score': 0.1, 'threat_level': 0.8, 'data_sensitivity': 0.9},
        {'risk_score': 0.5, 'trust_score': 0.6, 'threat_level': 0.3, 'data_sensitivity': 0.5},
        {'risk_score': 0.2, 'trust_score': 0.9, 'threat_level': 0.1, 'data_sensitivity': 0.2}
    ]
    
    for ctx in contexts:
        policy = adapter.get_encryption_policy(ctx)
        print(f"Risk: {ctx['risk_score']:.1f} → {policy.strength.value}")
        print(f"  Algorithm: {policy.algorithm}, Key Size: {policy.key_size}")
        print(f"  Iterations: {policy.iteration_count}, Memory: {policy.memory_cost}MB")
        print()

def test_key_rotation():
    print("=" * 60)
    print("3. Testing Key Rotation Manager")
    print("=" * 60)
    
    manager = KeyRotationManager()
    
    # Generate keys
    key1 = manager.generate_key('short_lived')
    key2 = manager.generate_key('medium_lived')
    key3 = manager.generate_key('long_lived')
    
    print(f"Generated keys:")
    print(f"  {key1.id}: {key1.status}, expires {key1.expires_at.strftime('%H:%M')}")
    print(f"  {key2.id}: {key2.status}, expires {key2.expires_at.strftime('%H:%M')}")
    print(f"  {key3.id}: {key3.status}, expires {key3.expires_at.strftime('%H:%M')}")
    
    # Check rotation
    rotation_needed = manager.check_rotation_needed()
    print(f"\nKeys needing rotation: {rotation_needed}")
    
    # Rotate one key
    if key1.id in rotation_needed:
        new_key = manager.rotate_key(key1.id, "expired")
        print(f"\nRotated {key1.id} → {new_key.id}")
    
    metrics = manager.get_rotation_metrics()
    print(f"\nRotation Metrics: {metrics}")

def test_communication_security():
    print("\n" + "=" * 60)
    print("4. Testing Communication Security")
    print("=" * 60)
    
    comm = CommunicationSecurity()
    
    session = comm.establish_secure_channel(
        peer_id="client-001",
        certificate_pin="pin-123456"
    )
    
    print(f"Secure channel established with {session['peer_id']}")
    print(f"Protocol: {session['protocol']}")
    print(f"Certificate Pinned: {session['certificate_pinned']}")
    
    security_info = comm.get_session_security("client-001")
    print(f"\nSession Security:")
    print(f"  HSTS Enforced: {security_info['hsts_enforced']}")
    print(f"  Age: {security_info['age_seconds']:.0f} seconds")
    
    metrics = comm.get_security_metrics()
    print(f"\nSecurity Metrics: {metrics}")

def test_timing_security():
    print("\n" + "=" * 60)
    print("5. Testing Timing Security")
    print("=" * 60)
    
    timing = TimingSecurity()
    
    # Test operation with timing protection
    def sensitive_operation():
        return {"status": "success", "data": "sensitive"}
    
    start = time.time()
    result = timing.protect_operation(sensitive_operation)
    elapsed = (time.time() - start) * 1000
    
    print(f"Operation completed in {elapsed:.2f}ms")
    print(f"Result: {result}")
    
    # Test padding
    original = "Hello World"
    padded = timing.pad_response(original, min_size=100)
    print(f"Original size: {len(original)}, Padded size: {len(padded)}")
    
    metrics = timing.get_timing_metrics()
    print(f"\nTiming Metrics: {metrics}")

def run_all_tests():
    print("\n" + "=" * 60)
    print("🔐 BLACK VEIL ENCRYPTION ENHANCEMENTS TEST")
    print("=" * 60 + "\n")
    
    test_dynamic_algorithm_selector()
    test_risk_adaptive_encryption()
    test_key_rotation()
    test_communication_security()
    test_timing_security()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
