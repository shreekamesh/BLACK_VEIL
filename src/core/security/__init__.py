"""
BLACK VEIL Dynamic Security Layer
100% Dynamic - No Static Methods

Core Philosophy: Every encryption operation is unique.
- Keys rotate based on time, usage, events, risk, entropy
- Algorithms selected dynamically by context
- Parameters mutate continuously
- Self-healing with automatic rotation
- Forward secrecy guaranteed
- Context-Aware: Kerckhoffs-inspired dynamic parameters
- Deception Fabric: Fake encryption artifacts for attacker confusion
"""
from .dynamic_encryption import (
    DynamicEncryptionEngine, EncryptionContext, DynamicKey,
    SecurityContext, ContextAwareEncryptionEngine,
    EncryptionRealityFabric, DynamicEncryptionPolicyEngine,
    DynamicEncryptionSystem
)
from .dynamic_hasher import DynamicPasswordHasher
from .dynamic_jwt import DynamicJWTManager
from .dynamic_tls import DynamicTLSManager
from .rotation_monitor import RotationMonitor

__all__ = [
    # Legacy (backward compatible)
    'DynamicEncryptionEngine', 'EncryptionContext', 'DynamicKey',
    'DynamicPasswordHasher', 'DynamicJWTManager', 'DynamicTLSManager',
    'RotationMonitor',
    # New Kerckhoffs-inspired components
    'SecurityContext', 'ContextAwareEncryptionEngine',
    'EncryptionRealityFabric', 'DynamicEncryptionPolicyEngine',
    'DynamicEncryptionSystem',
]

