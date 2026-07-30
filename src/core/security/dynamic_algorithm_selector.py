"""
Dynamic Algorithm Selection for BLACK VEIL
Context-aware algorithm selection based on risk, trust, and performance
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for algorithm selection"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    PERFORMANCE = "performance"

class AlgorithmType(Enum):
    """Types of algorithms"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    HASH = "hash"
    KDF = "kdf"

@dataclass
class AlgorithmConfig:
    """Configuration for a selected algorithm"""
    name: str
    key_size: int
    mode: str
    performance_score: float
    security_score: float
    hardware_acceleration: bool

class DynamicAlgorithmSelector:
    """
    Selects appropriate algorithms based on context
    """
    
    def __init__(self):
        self.algorithm_pool = {
            AlgorithmType.SYMMETRIC: {
                'aes-256-gcm': {
                    'security': 1.0,
                    'performance': 0.8,
                    'hardware': True,
                    'key_size': 256
                },
                'chacha20-poly1305': {
                    'security': 0.95,
                    'performance': 0.9,
                    'hardware': False,
                    'key_size': 256
                },
                'aes-128-gcm': {
                    'security': 0.8,
                    'performance': 0.95,
                    'hardware': True,
                    'key_size': 128
                }
            },
            AlgorithmType.ASYMMETRIC: {
                'rsa-4096': {
                    'security': 1.0,
                    'performance': 0.3,
                    'hardware': True,
                    'key_size': 4096
                },
                'ecdsa-p384': {
                    'security': 0.95,
                    'performance': 0.7,
                    'hardware': True,
                    'key_size': 384
                },
                'ed25519': {
                    'security': 0.9,
                    'performance': 0.9,
                    'hardware': False,
                    'key_size': 256
                }
            },
            AlgorithmType.HASH: {
                'sha3-512': {
                    'security': 1.0,
                    'performance': 0.6,
                    'hardware': True,
                    'key_size': 512
                },
                'blake2b': {
                    'security': 0.95,
                    'performance': 0.9,
                    'hardware': False,
                    'key_size': 512
                },
                'sha-256': {
                    'security': 0.85,
                    'performance': 0.95,
                    'hardware': True,
                    'key_size': 256
                }
            },
            AlgorithmType.KDF: {
                'argon2id': {
                    'security': 1.0,
                    'performance': 0.3,
                    'hardware': False,
                    'key_size': 0
                },
                'pbkdf2-sha512': {
                    'security': 0.9,
                    'performance': 0.6,
                    'hardware': False,
                    'key_size': 0
                },
                'scrypt': {
                    'security': 0.95,
                    'performance': 0.4,
                    'hardware': False,
                    'key_size': 0
                }
            }
        }
    
    def select_algorithm(self, 
                        algorithm_type: AlgorithmType,
                        security_level: SecurityLevel,
                        context: Dict[str, Any]) -> AlgorithmConfig:
        """Select the best algorithm based on context"""
        algorithms = self.algorithm_pool.get(algorithm_type, {})
        if not algorithms:
            raise ValueError(f"No algorithms available for type {algorithm_type}")
        
        scored = []
        for name, props in algorithms.items():
            score = self._calculate_score(props, security_level, context)
            scored.append((score, name, props))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_name, best_props = scored[0]
        
        logger.info(f"Selected {best_name} with score {best_score:.2f}")
        
        return AlgorithmConfig(
            name=best_name,
            key_size=best_props.get('key_size', 256),
            mode='gcm' if 'gcm' in best_name else 'auto',
            performance_score=best_props.get('performance', 0.5),
            security_score=best_props.get('security', 0.5),
            hardware_acceleration=best_props.get('hardware', False)
        )
    
    def _calculate_score(self, props: Dict, 
                         security_level: SecurityLevel,
                         context: Dict) -> float:
        """Calculate algorithm score based on context"""
        score = 0.0
        
        security_weights = {
            SecurityLevel.CRITICAL: 1.0,
            SecurityLevel.HIGH: 0.8,
            SecurityLevel.MEDIUM: 0.5,
            SecurityLevel.LOW: 0.3,
            SecurityLevel.PERFORMANCE: 0.1
        }
        security_weight = security_weights.get(security_level, 0.5)
        
        security_score = props.get('security', 0.5)
        score += security_score * security_weight
        
        performance_weight = 1.0 - security_weight
        performance_score = props.get('performance', 0.5)
        score += performance_score * performance_weight
        
        if props.get('hardware', False) and context.get('hardware_acceleration', False):
            score += 0.1
        
        if context.get('high_throughput', False):
            score += 0.1 * props.get('performance', 0.5)
        
        if context.get('low_latency', False):
            score += 0.1 * props.get('performance', 0.5)
        
        return min(1.0, max(0.0, score))
    
    def get_recommended_algorithms(self, context: Dict) -> Dict:
        """Get recommended algorithms for all types"""
        security_level = self._determine_security_level(context)
        
        recommendations = {}
        for algo_type in AlgorithmType:
            try:
                config = self.select_algorithm(algo_type, security_level, context)
                recommendations[algo_type.value] = config
            except Exception as e:
                logger.error(f"Failed to select {algo_type}: {e}")
        
        return recommendations
    
    def _determine_security_level(self, context: Dict) -> SecurityLevel:
        """Determine security level from context"""
        risk_score = context.get('risk_score', 0.5)
        trust_score = context.get('trust_score', 0.5)
        threat_level = context.get('threat_level', 0.0)
        
        if risk_score > 0.8 or trust_score < 0.2 or threat_level > 0.7:
            return SecurityLevel.CRITICAL
        elif risk_score > 0.6 or trust_score < 0.4 or threat_level > 0.5:
            return SecurityLevel.HIGH
        elif risk_score > 0.4 or trust_score < 0.6 or threat_level > 0.3:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW
