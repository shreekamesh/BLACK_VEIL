"""
Risk-Adaptive Encryption for BLACK VEIL
Encryption strength adapts based on risk level
"""

from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
import logging
from src.core.security.dynamic_algorithm_selector import DynamicAlgorithmSelector, SecurityLevel

logger = logging.getLogger(__name__)

class EncryptionStrength(Enum):
    """Encryption strength levels"""
    MAXIMUM = "maximum"
    STRONG = "strong"
    BALANCED = "balanced"
    FAST = "fast"

@dataclass
class EncryptionPolicy:
    """Encryption policy based on risk"""
    algorithm: str
    key_size: int
    iteration_count: int
    memory_cost: int
    time_cost: int
    strength: EncryptionStrength

class RiskAdaptiveEncryption:
    """Adapts encryption strength based on risk assessment"""
    
    def __init__(self):
        self.algorithm_selector = DynamicAlgorithmSelector()
        
    def get_encryption_policy(self, context: Dict[str, Any]) -> EncryptionPolicy:
        """Get encryption policy based on risk context"""
        risk = self._calculate_effective_risk(context)
        strength = self._determine_strength(risk, context)
        algorithm = self._select_algorithm(strength, context)
        params = self._adjust_parameters(algorithm, risk, context)
        
        return EncryptionPolicy(
            algorithm=algorithm,
            key_size=params['key_size'],
            iteration_count=params.get('iterations', 100000),
            memory_cost=params.get('memory_cost', 64),
            time_cost=params.get('time_cost', 3),
            strength=strength
        )
    
    def _calculate_effective_risk(self, context: Dict) -> float:
        """Calculate effective risk score"""
        risk_score = context.get('risk_score', 0.5)
        trust_score = context.get('trust_score', 0.5)
        threat_level = context.get('threat_level', 0.0)
        sensitivity = context.get('data_sensitivity', 0.5)
        
        effective_risk = (
            risk_score * 0.35 +
            (1 - trust_score) * 0.25 +
            threat_level * 0.25 +
            sensitivity * 0.15
        )
        
        return min(1.0, max(0.0, effective_risk))
    
    def _determine_strength(self, risk: float, context: Dict) -> EncryptionStrength:
        """Determine encryption strength based on risk"""
        if risk > 0.8:
            return EncryptionStrength.MAXIMUM
        elif risk > 0.6:
            return EncryptionStrength.STRONG
        elif risk > 0.3:
            return EncryptionStrength.BALANCED
        else:
            return EncryptionStrength.FAST
    
    def _select_algorithm(self, strength: EncryptionStrength, context: Dict) -> str:
        """Select algorithm based on strength level"""
        algorithms = {
            EncryptionStrength.MAXIMUM: 'aes-256-gcm',
            EncryptionStrength.STRONG: 'aes-256-gcm',
            EncryptionStrength.BALANCED: 'chacha20-poly1305',
            EncryptionStrength.FAST: 'chacha20-poly1305'
        }
        return algorithms.get(strength, 'aes-256-gcm')
    
    def _adjust_parameters(self, algorithm: str, risk: float, context: Dict) -> Dict:
        """Adjust encryption parameters based on risk"""
        params = {'key_size': 256}
        
        if risk > 0.8:
            params['iterations'] = 200000
            params['memory_cost'] = 128
            params['time_cost'] = 5
        elif risk > 0.6:
            params['iterations'] = 150000
            params['memory_cost'] = 96
            params['time_cost'] = 4
        elif risk > 0.3:
            params['iterations'] = 100000
            params['memory_cost'] = 64
            params['time_cost'] = 3
        else:
            params['iterations'] = 50000
            params['memory_cost'] = 32
            params['time_cost'] = 2
        
        return params
    
    def get_encryption_recommendations(self, context: Dict) -> Dict:
        """Get encryption recommendations"""
        policy = self.get_encryption_policy(context)
        
        return {
            'algorithm': policy.algorithm,
            'key_size': policy.key_size,
            'strength': policy.strength.value,
            'iteration_count': policy.iteration_count,
            'memory_cost': policy.memory_cost,
            'time_cost': policy.time_cost,
            'recommendation': f"Use {policy.algorithm} with {policy.key_size}-bit keys"
        }
