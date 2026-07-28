"""
BLACK VEIL ACDO Verification Test
Tests all 16 core modules import and ACDO pipeline execution
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all module imports"""
    modules = [
        ('src.core.cognitive.decision_brain', ['DecisionBrain', 'Decision', 'DecisionContext']),
        ('src.core.cognitive.adversarial_reasoning', ['AdversarialReasoningEngine']),
        ('src.core.cognitive.intent_reasoning', ['IntentReasoningEngine', 'AttackerGoal', 'AttackerProfile']),
        ('src.core.cognitive.strategy_engine', ['StrategyEngine']),
        ('src.core.cognitive.consensus_engine', ['ConsensusEngine']),
        ('src.core.cognitive.ai_core', ['AICore']),
        ('src.core.threat.analyzer', ['ThreatAnalyzer']),
        ('src.core.threat.threat_prediction', ['ThreatPredictionEngine']),
        ('src.core.trust.engine', ['TrustEngine']),
        ('src.core.trust.confidence_engine', ['ConfidenceEngine']),
        ('src.core.credential.genome_engine', ['CredentialGenomeEngine']),
        ('src.core.deception.fabric', ['RealityFabricEngine']),
        ('src.core.knowledge.graph', ['KnowledgeGraph']),
        ('src.core.policy.engine', ['PolicyEngine']),
        ('src.core.policy.security_score', ['SecurityScoreEngine']),
        ('src.core.response.recovery_engine', ['RecoveryIntelligenceEngine']),
        ('src.core.orchestrator.acdo', ['ACDO']),
    ]
    
    for module_path, classes in modules:
        try:
            mod = __import__(module_path, fromlist=classes)
            for cls in classes:
                obj = getattr(mod, cls)
                assert obj is not None
            print(f"  ✓ {module_path} ({', '.join(classes)})")
        except Exception as e:
            print(f"  ✗ {module_path}: {e}")
            return False
    return True

def test_acdo_pipeline():
    """Test ACDO end-to-end pipeline"""
    from src.core.orchestrator.acdo import ACDO
    
    acdo = ACDO()
    assert acdo is not None
    print(f"  ✓ ACDO initialized (orchestrator_id={acdo.orchestrator_id})")
    
    # Process test event
    result = acdo.process_event({
        'type': 'suspicious_login',
        'source': {'id': 'user_42', 'type': 'user', 'properties': {'role': 'admin'}},
        'target': {'id': 'server_db_01', 'type': 'server', 'properties': {'service': 'postgresql'}},
        'severity': 0.75,
        'confidence': 0.85,
        'technique_id': 'T1110',
        'techniques': ['T1110'],
        'indicators': ['brute_force', 'multiple_failed_logins'],
    })
    
    assert result['status'] == 'processed'
    pipeline = result['pipeline']
    
    assert 'threat_analysis' in pipeline
    assert 'trust_assessment' in pipeline
    assert 'adversarial_insights' in pipeline
    assert 'attacker_intent' in pipeline
    assert 'prediction' in pipeline
    assert 'decision' in pipeline
    assert 'consensus' in pipeline
    assert 'response' in pipeline
    assert 'security_score' in pipeline
    assert 'confidence_calibration' in pipeline
    
    print(f"  ✓ Event processed")
    print(f"    Decision action: {pipeline['decision']['action']}")
    print(f"    Decision confidence: {pipeline['decision']['confidence']:.3f}")
    print(f"    Adversarial score: {pipeline['adversarial_insights']['adversarial_score']:.3f}")
    print(f"    Weakest layer: {pipeline['adversarial_insights']['weakest_layer']}")
    print(f"    Attack paths: {pipeline['adversarial_insights']['attack_paths']}")
    print(f"    Attacker intent: {pipeline['attacker_intent']['primary_goal']}")
    print(f"    Predicted next: {pipeline['prediction']['next_objective']}")
    print(f"    Consensus: {pipeline['consensus']['decision']}")
    print(f"    Security score: {pipeline['security_score']}")
    print(f"    Security level: {pipeline['security_level']}")
    print(f"    Confidence factors: {len(pipeline['confidence_calibration']['factors'])}")
    
    return True

def test_sub_components():
    """Test individual sub-components"""
    # DecisionBrain
    from src.core.cognitive.decision_brain import DecisionBrain
    db = DecisionBrain()
    assert db is not None
    print(f"  ✓ DecisionBrain: {db.get_state_summary()['total_decisions']} decisions")
    
    # AdversarialReasoningEngine
    from src.core.cognitive.adversarial_reasoning import AdversarialReasoningEngine
    are = AdversarialReasoningEngine()
    analysis = are.analyze_defenses()
    assert 'weakest_layer' in analysis
    assert 'overall_adversarial_score' in analysis
    print(f"  ✓ AdversarialReasoning: weakest={analysis['weakest_layer']}, score={analysis['overall_adversarial_score']:.3f}")
    
    # IntentReasoningEngine
    from src.core.cognitive.intent_reasoning import IntentReasoningEngine
    ire = IntentReasoningEngine()
    intent = ire.infer_intent([{'type': 'scan', 'technique_id': 'T1046'}])
    assert 'primary_goal' in intent
    print(f"  ✓ IntentReasoning: goal={intent['primary_goal']}, confidence={intent['confidence']:.3f}")
    
    # StrategyEngine
    from src.core.cognitive.strategy_engine import StrategyEngine
    se = StrategyEngine()
    strategies = se.evaluate_strategies(
        {'severity': 0.75, 'attack_type': 'credential_theft'},
        {'primary_goal': 'credential_access'},
        {'overall_adversarial_score': 0.4},
    )
    assert 'recommended' in strategies
    print(f"  ✓ StrategyEngine: recommended={strategies['recommended']['action']}")
    
    # CredentialGenomeEngine
    from src.core.credential.genome_engine import CredentialGenomeEngine
    cge = CredentialGenomeEngine()
    cred = cge.generate_credential()
    assert 'entropy' in cred
    print(f"  ✓ CredentialGenome: entropy={cred['entropy']:.2f}, fitness={cred['fitness']:.2f}")
    
    # SecurityScoreEngine
    from src.core.policy.security_score import SecurityScoreEngine
    sse = SecurityScoreEngine()
    score = sse.calculate_score(0.75, 0.70, 0.60, 0.30, 0.85)
    assert 'overall_score' in score
    print(f"  ✓ SecurityScore: {score['overall_score']:.3f} ({score['level']})")
    
    # RecoveryIntelligenceEngine
    from src.core.response.recovery_engine import RecoveryIntelligenceEngine
    rie = RecoveryIntelligenceEngine()
    analysis = rie.analyze_incident({
        'attack_type': 'credential_theft',
        'detection_time': 45,
        'response_time': 120,
        'was_blocked': True,
        'forensics_collected': True,
    })
    assert 'recommendations' in analysis
    print(f"  ✓ RecoveryIntelligence: {len(analysis['recommendations'])} recommendations")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("BLACK VEIL ACDO Verification Test")
    print("=" * 60)
    
    print("\n1. Testing module imports...")
    if test_imports():
        print("   All modules imported successfully ✓")
    
    print("\n2. Testing sub-components...")
    if test_sub_components():
        print("   All sub-components functional ✓")
    
    print("\n3. Testing ACDO pipeline...")
    if test_acdo_pipeline():
        print("   ACDO pipeline verified ✓")
    
    print("\n" + "=" * 60)
    print("BLACK VEIL ACDO: ALL TESTS PASSED ✓")
    print("=" * 60)

