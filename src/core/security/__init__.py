"""
BLACK VEIL Security Module
"""

# Existing
from .dynamic_encryption import (
    DynamicEncryptionEngine,
    EncryptionContext,
    DynamicKey
)

# New encryption modules
from .dynamic_algorithm_selector import (
    DynamicAlgorithmSelector,
    SecurityLevel,
    AlgorithmType,
    AlgorithmConfig
)

from .risk_adaptive_encryption import (
    RiskAdaptiveEncryption,
    EncryptionStrength,
    EncryptionPolicy
)

from .key_rotation_manager import (
    KeyRotationManager,
    KeyInfo
)

from .communication_security import (
    CommunicationSecurity,
    ProtocolVersion,
    CipherSuite,
    SecurityContext
)

from .timing_security import (
    TimingSecurity,
    TimingProtection
)

__all__ = [
    # Existing
    'DynamicEncryptionEngine',
    'EncryptionContext',
    'DynamicKey',
    
    # New
    'DynamicAlgorithmSelector',
    'SecurityLevel',
    'AlgorithmType',
    'AlgorithmConfig',
    'RiskAdaptiveEncryption',
    'EncryptionStrength',
    'EncryptionPolicy',
    'KeyRotationManager',
    'KeyInfo',
    'CommunicationSecurity',
    'ProtocolVersion',
    'CipherSuite',
    'SecurityContext',
    'TimingSecurity',
    'TimingProtection'
]
