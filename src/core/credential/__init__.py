"""
Credential Intelligence Layer - DCMM Implementation
Research Contribution: Dynamic Credential Mutation Model (DCMM)
"""
from .genome_engine import CredentialGenomeEngine
from .rotation import RotationEngine
from .credential_health import CredentialHealthEngine
from .revocation import RevocationEngine
from .distribution import DistributionEngine
from .credential_audit import CredentialAuditEngine

__all__ = [
    'CredentialGenomeEngine', 'RotationEngine', 'CredentialHealthEngine',
    'RevocationEngine', 'DistributionEngine', 'CredentialAuditEngine',
]

