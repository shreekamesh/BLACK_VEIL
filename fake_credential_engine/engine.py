"""
BLACK VEIL V5 — Fake Credential Engine
Credential lifecycle management, deployment, and tracking operations
"""
import hashlib
import secrets
import string
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FakeCredential:
    """A managed fake credential with lifecycle state"""
    credential_id: str
    service: str
    username: str
    password_hash: str
    credential_type: str          # SSH, HTTP, FTP, DB, API
    status: str                   # ACTIVE, MUTATED, DETECTED, EXPIRED
    generation: int
    lifetime_sec: int
    created_at: str
    last_used_at: Optional[str] = None
    mutated_count: int = 0
    parent_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class FakeCredentialEngine:
    """
    Fake Credential Engine for managing deceptive credentials.
    
    Handles:
    - Credential generation with realistic patterns
    - Lifecycle tracking (deploy, detect, expire, rotate)
    - Deployment to honeypot/decoy services
    - Interaction tracking
    """

    def __init__(self):
        self._credentials: dict[str, FakeCredential] = {}
        self._deployed: dict[str, list[str]] = {}  # service -> credential_ids

        logger.info("Fake Credential Engine initialized")

    def generate_credential(
        self,
        service: str,
        credential_type: str = "API",
        username: Optional[str] = None,
        lifetime_sec: Optional[int] = None,
    ) -> FakeCredential:
        """Generate a new fake credential"""
        credential_id = str(uuid.uuid4())
        username = username or self._generate_username(service)
        password = self._generate_password()
        now = datetime.now(timezone.utc)

        credential = FakeCredential(
            credential_id=credential_id,
            service=service,
            username=username,
            password_hash=hashlib.sha256(password.encode()).hexdigest(),
            credential_type=credential_type,
            status="ACTIVE",
            generation=0,
            lifetime_sec=lifetime_sec or 86400,
            created_at=now.isoformat(),
            metadata={
                "length": len(password),
                "entropy": self._estimate_entropy(password),
                "source": service,
            },
        )

        self._credentials[credential_id] = credential

        logger.info(f"Fake credential generated for {service}: {credential_id[:8]}...")

        return credential

    def deploy_to_service(self, service_name: str, credential_id: str) -> bool:
        """Deploy a credential to a specific service"""
        if credential_id not in self._credentials:
            logger.warning(f"Cannot deploy unknown credential: {credential_id}")
            return False

        if service_name not in self._deployed:
            self._deployed[service_name] = []
        self._deployed[service_name].append(credential_id)
        logger.info(f"Credential {credential_id[:8]}... deployed to {service_name}")
        return True

    def record_use(self, credential_id: str) -> None:
        """Record that a credential was used (detected/accessed by attacker)"""
        if credential_id in self._credentials:
            self._credentials[credential_id].last_used_at = datetime.now(timezone.utc).isoformat()
            self._credentials[credential_id].mutated_count += 1
            logger.info(f"Credential used: {credential_id[:8]}...")

    def mark_detected(self, credential_id: str) -> None:
        """Mark a credential as detected by attacker"""
        if credential_id in self._credentials:
            self._credentials[credential_id].status = "DETECTED"
            logger.info(f"Credential detected by attacker: {credential_id[:8]}...")

    def rotate_credential(self, credential_id: str) -> Optional[FakeCredential]:
        """Rotate (regenerate) a credential"""
        if credential_id not in self._credentials:
            return None

        old = self._credentials[credential_id]
        new_cred = self.generate_credential(
            service=old.service,
            credential_type=old.credential_type,
            lifetime_sec=old.lifetime_sec,
        )
        new_cred.parent_id = credential_id
        new_cred.generation = old.generation + 1
        old.status = "MUTATED"

        logger.info(f"Credential rotated: {credential_id[:8]}... -> {new_cred.credential_id[:8]}...")
        return new_cred

    def list_active(self) -> list[FakeCredential]:
        """List all active credentials"""
        return [c for c in self._credentials.values() if c.status == "ACTIVE"]

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of Fake Credential Engine state"""
        active = self.list_active()
        return {
            "total_credentials": len(self._credentials),
            "active_credentials": len(active),
            "deployed_services": len(self._deployed),
            "avg_generation": round(
                sum(c.generation for c in self._credentials.values()) / max(1, len(self._credentials)), 2
            ),
        }

    @staticmethod
    def _generate_username(service: str) -> str:
        """Generate realistic username based on service"""
        prefixes = ["svc", "bot", "api", "app", "admin", "deploy", "ci", "backup"]
        return f"{secrets.choice(prefixes)}_{service}_{secrets.token_hex(4)}"

    @staticmethod
    def _generate_password(length: int = 24) -> str:
        """Generate a realistic-looking password"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def _estimate_entropy(value: str) -> float:
        """Estimate Shannon entropy of a string"""
        import math
        if not value:
            return 0.0
        counts = [
            sum(1 for c in value if c.islower()),
            sum(1 for c in value if c.isupper()),
            sum(1 for c in value if c.isdigit()),
            sum(1 for c in value if not c.isalnum()),
        ]
        probs = [c / len(value) for c in counts if c > 0]
        return -sum(p * math.log2(p) for p in probs) if probs else 0.0

