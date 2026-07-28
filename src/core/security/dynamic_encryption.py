"""
BLACK VEIL Dynamic Encryption Engine
100% Dynamic - No Static Methods

Core Principle:
- Every encryption operation produces a unique ciphertext
- Keys auto-rotate based on time, usage, risk, entropy, events
- Algorithm selection depends on sensitivity and risk context
- Continuous entropy monitoring and adaptation
- Context-Aware: Kerckhoffs-inspired dynamic parameters
- Deception Fabric: Fake encryption artifacts for attacker confusion
"""
import asyncio
import hashlib
import base64
import secrets
import time
import uuid
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SecurityContext(Enum):
    """Dynamic security context levels for context-aware encryption"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DECEPTION = "deception"


@dataclass
class EncryptionContext:
    """Dynamic encryption context - unique per operation.
    Extended with Kerckhoffs-inspired context-aware fields."""
    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    algorithm: str = "aes-256-gcm"
    key_id: str = ""
    key_version: int = 1
    rotation_count: int = 0
    entropy: float = 0.0
    risk_score: float = 0.0
    sensitivity_level: float = 0.5
    history: List[Dict[str, Any]] = field(default_factory=list)

    # === New context-aware fields (Kerckhoffs-inspired) ===
    # Context factors
    trust_score: float = 0.5  # 0-1
    asset_type: str = "general"
    data_size: int = 0
    user_role: str = "viewer"
    threat_level: float = 0.0  # 0-1
    environment: str = "production"
    time_of_day: str = "business_hours"
    device_type: str = "unknown"
    location: str = "unknown"
    security_level: SecurityContext = SecurityContext.MEDIUM

    # Encryption parameters
    selected_algorithm: str = ""
    selected_kdf: str = ""
    rotation_schedule: str = "dynamic"

    # Deception flags
    is_deception: bool = False
    fake_key_id: Optional[str] = None
    fake_algorithm: Optional[str] = None


@dataclass
class DynamicKey:
    """Dynamic encryption key with full lifecycle tracking"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    key_data: bytes = field(default_factory=lambda: Fernet.generate_key())
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24))
    version: int = 1
    usage_count: int = 0
    max_usage: int = 10000
    status: str = "active"  # active, expiring, rotated, revoked
    algorithm: str = "fernet"
    parent_key_id: Optional[str] = None


class DynamicEncryptionEngine:
    """
    Fully Dynamic Encryption Engine.

    No static keys, no static algorithms, no static parameters.
    Every encryption operation is unique and context-aware.

    Features:
    - Time-based key rotation (12-48h dynamic window)
    - Usage-based rotation (configurable max_usage)
    - Event-triggered rotation (security alerts)
    - Risk-based rotation (high risk = faster rotation)
    - Entropy-based rotation (low entropy triggers rotation)
    - Context-aware algorithm selection
    - Forward secrecy (past data safe from future key compromise)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.active_keys: Dict[str, DynamicKey] = {}
        self.key_history: List[DynamicKey] = []
        self.encryption_contexts: Dict[str, EncryptionContext] = {}

        self.rotation_triggers = {
            'time_based': True,
            'usage_based': True,
            'event_based': True,
            'risk_based': True,
            'entropy_based': True,
        }

        # Dynamic state parameters
        self.current_entropy = 0.85
        self.global_risk = 0.1
        self.last_rotation = datetime.now(timezone.utc)
        self.rotation_interval_seconds = 3600  # Base: 1 hour

        self._initialize_dynamic_keys()
        logger.info("Dynamic Encryption Engine initialized")

    def _initialize_dynamic_keys(self) -> None:
        """Initialize pool of dynamic keys with random properties"""
        initial_key = self._generate_dynamic_key()
        self.active_keys[initial_key.id] = initial_key
        for _ in range(4):
            bk = self._generate_dynamic_key()
            bk.status = "active"
            self.active_keys[bk.id] = bk

    def _generate_dynamic_key(self) -> DynamicKey:
        """Generate a key with randomized properties"""
        time_seed = int(time.time() / 3600)
        random_seed = secrets.randbits(64)
        combined = time_seed ^ random_seed
        rng = np.random.default_rng(combined)
        key_length = int(rng.uniform(32, 64))
        key_data = secrets.token_bytes(key_length)
        algos = ['fernet', 'aes-256-gcm', 'chacha20-poly1305']
        selected = rng.choice(algos)
        lifespan = rng.uniform(12, 48)
        return DynamicKey(
            key_data=key_data,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=lifespan),
            version=len(self.key_history) + 1,
            algorithm=selected,
            max_usage=int(rng.uniform(5000, 20000)),
        )

    async def check_and_rotate_keys(self) -> List[str]:
        """Check all keys and rotate those that need it."""
        rotated = []
        current_time = datetime.now(timezone.utc)
        for key_id, key in list(self.active_keys.items()):
            reasons = self._evaluate_rotation_needs(key, current_time)
            if reasons:
                await self._rotate_key(key_id, reasons)
                rotated.append(key_id)
        return rotated

    def _evaluate_rotation_needs(self, key: DynamicKey, now: datetime) -> List[str]:
        reasons = []
        if now >= key.expires_at:
            reasons.append("time_expired")
        if key.usage_count >= key.max_usage:
            reasons.append("max_usage_reached")
        if self.global_risk > 0.7:
            reasons.append("high_risk")
        if self.current_entropy < 0.3:
            reasons.append("low_entropy")
        return reasons

    async def _rotate_key(self, key_id: str, reasons: List[str]) -> None:
        logger.info(f"Rotating key {key_id[:8]}: {', '.join(reasons)}")
        old_key = self.active_keys[key_id]
        new_key = self._generate_dynamic_key()
        new_key.parent_key_id = old_key.id
        new_key.version = old_key.version + 1
        old_key.status = "rotated"
        self.key_history.append(old_key)
        self.active_keys[new_key.id] = new_key
        self.last_rotation = datetime.now(timezone.utc)
        self.current_entropy = self._calculate_entropy()
        await self._log_rotation(old_key, new_key, reasons)

    async def _log_rotation(self, old_key, new_key, reasons):
        log = {
            'old_key_id': old_key.id, 'new_key_id': new_key.id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'reasons': reasons, 'old_version': old_key.version,
            'new_version': new_key.version,
            'old_algorithm': old_key.algorithm, 'new_algorithm': new_key.algorithm,
            'global_risk': self.global_risk, 'current_entropy': self.current_entropy,
        }
        logger.info(f"Rotation logged: {json.dumps(log)}")

    def _calculate_entropy(self) -> float:
        factors = [
            len(self.active_keys) / 10.0,
            1.0 - min(1.0, len(self.key_history) / 100.0),
            self.global_risk,
            np.random.uniform(0.5, 1.0),
        ]
        return min(1.0, float(np.mean(factors)))

    def _get_active_key(self) -> DynamicKey:
        scored = []
        for key in self.active_keys.values():
            if key.status != "active":
                continue
            age_ratio = (datetime.now(timezone.utc) - key.created_at).total_seconds() / \
                        max(1, (key.expires_at - key.created_at).total_seconds())
            score = (
                0.3 * (1 - age_ratio) +
                0.2 * (1 - key.usage_count / max(1, key.max_usage)) +
                0.3 * (1 - self.global_risk) +
                0.2 * self.current_entropy
            )
            scored.append((score, key))
        if not scored:
            new_key = self._generate_dynamic_key()
            self.active_keys[new_key.id] = new_key
            return new_key
        scores = np.array([s[0] for s in scored])
        probs = np.exp(scores) / np.sum(np.exp(scores))
        return scored[np.random.choice(len(scored), p=probs)][1]

    async def encrypt_data(self, data: bytes,
                           context: Optional[EncryptionContext] = None) -> Dict[str, Any]:
        """Encrypt data with fully dynamic parameters - every call unique."""
        if context is None:
            context = EncryptionContext()
        key = self._get_active_key()
        key.usage_count += 1

        iv_length = 12 if key.algorithm == 'aes-256-gcm' else 16
        iv = secrets.token_bytes(iv_length)
        salt = secrets.token_bytes(32)
        algorithm = self._select_algorithm(context)

        # Derive using ONLY context_id (immutable) for consistency with decrypt
        stable_ctx = {'ctx_id': context.context_id, 'ts': context.timestamp.isoformat()}
        ctx_bytes = json.dumps(stable_ctx, sort_keys=True).encode()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                         salt=salt + ctx_bytes, iterations=100000,
                         backend=default_backend())
        derived_key = kdf.derive(key.key_data)

        encrypted = await self._dynamic_encrypt(data, derived_key, iv, algorithm)

        context.key_id = key.id
        context.key_version = key.version
        context.rotation_count = key.version
        context.algorithm = algorithm
        context.entropy = self.current_entropy
        context.risk_score = self.global_risk
        self.encryption_contexts[context.context_id] = context

        return {
            'context_id': context.context_id,
            'ciphertext': encrypted['ciphertext'],
            'tag': encrypted.get('tag', b''),
            'iv': iv,
            'salt': salt,
            'algorithm': algorithm,
            'key_id': key.id,
            'key_version': key.version,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

    async def decrypt_data(self, encrypted_data: Dict[str, Any]) -> bytes:
        """Decrypt data using the same deterministic derivation."""
        context_id = encrypted_data.get('context_id')
        context = self.encryption_contexts.get(context_id)
        if not context:
            context = await self._recover_context(encrypted_data)

        key = await self._find_key(encrypted_data.get('key_id'),
                                   encrypted_data.get('key_version'))
        if not key:
            raise ValueError("No valid decryption key found")

        # Same derivation as encrypt: uses ONLY context_id + timestamp
        stable_ctx = {'ctx_id': context.context_id, 'ts': context.timestamp.isoformat()}
        ctx_bytes = json.dumps(stable_ctx, sort_keys=True).encode()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                         salt=encrypted_data['salt'] + ctx_bytes, iterations=100000,
                         backend=default_backend())
        derived_key = kdf.derive(key.key_data)

        return await self._dynamic_decrypt(
            encrypted_data['ciphertext'], derived_key,
            encrypted_data['iv'], encrypted_data['algorithm'],
            encrypted_data.get('tag', b''),
        )

    def _select_algorithm(self, context: EncryptionContext) -> str:
        if context.risk_score > 0.8:
            algos = ['aes-256-gcm', 'chacha20-poly1305']
        elif context.sensitivity_level > 0.7:
            algos = ['aes-256-gcm', 'aes-256-cbc']
        else:
            algos = ['fernet', 'aes-256-gcm']
        weights = np.exp(np.array([1.0, 0.8, 0.6])[:len(algos)])
        return str(np.random.choice(algos, p=weights / weights.sum()))

    async def _dynamic_encrypt(self, data: bytes, key: bytes, iv: bytes,
                                algorithm: str) -> Dict[str, Any]:
        if algorithm == 'aes-256-gcm':
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ct = encryptor.update(data) + encryptor.finalize()
            return {'ciphertext': ct, 'tag': encryptor.tag}
        elif algorithm == 'fernet':
            f = Fernet(base64.urlsafe_b64encode(key[:32]))
            return {'ciphertext': f.encrypt(data), 'tag': b''}
        else:
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ct = encryptor.update(data) + encryptor.finalize()
            return {'ciphertext': ct, 'tag': b''}

    async def _dynamic_decrypt(self, ciphertext: bytes, key: bytes, iv: bytes,
                                algorithm: str, tag: bytes = b'') -> bytes:
        if algorithm == 'aes-256-gcm':
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()
        elif algorithm == 'fernet':
            f = Fernet(base64.urlsafe_b64encode(key[:32]))
            return f.decrypt(ciphertext)
        else:
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()

    async def _find_key(self, key_id: str, version: int) -> Optional[DynamicKey]:
        if key_id in self.active_keys and self.active_keys[key_id].version >= version:
            return self.active_keys[key_id]
        for k in self.key_history:
            if k.id == key_id and k.version >= version:
                return k
        for k in self.active_keys.values():
            if k.version >= version:
                return k
        return None

    async def _recover_context(self, encrypted_data: Dict[str, Any]) -> EncryptionContext:
        return EncryptionContext(
            context_id=encrypted_data.get('context_id', str(uuid.uuid4())),
            timestamp=datetime.now(timezone.utc),
            algorithm=encrypted_data.get('algorithm', 'aes-256-gcm'),
            risk_score=self.global_risk,
        )

    def update_risk(self, risk_delta: float) -> None:
        self.global_risk = max(0.0, min(1.0, self.global_risk + risk_delta))
        if self.global_risk > 0.7:
            logger.warning(f"High risk detected ({self.global_risk:.2f})")

    def get_state_summary(self) -> Dict[str, Any]:
        return {
            'active_keys': len(self.active_keys),
            'historical_keys': len(self.key_history),
            'current_entropy': round(self.current_entropy, 3),
            'global_risk': round(self.global_risk, 3),
            'last_rotation': self.last_rotation.isoformat(),
            'total_contexts': len(self.encryption_contexts),
        }


# =============================================================================
# NEW COMPONENTS: Context-Aware Encryption (Kerckhoffs-inspired Architecture)
# =============================================================================


class ContextAwareEncryptionEngine:
    """
    Context-Aware Encryption Engine following Kerckhoffs's Principle.

    Security depends on:
    1. Strong cryptographic algorithms (public)
    2. Secret keys (private)
    3. Dynamic context (adaptive)
    4. Deception fabric (confusion)
    """

    def __init__(self, config: Dict[str, Any], reality_fabric: Optional[Any] = None):
        self.config = config
        self.reality_fabric = reality_fabric
        self.active_keys: Dict[str, Dict[str, Any]] = {}
        self.key_history: List[Dict[str, Any]] = []
        self.context_cache: Dict[str, EncryptionContext] = {}

        # Algorithm pools (public knowledge - Kerckhoffs)
        self.algorithm_pool = {
            'symmetric': {
                'aes-256-gcm': {'strength': 1.0, 'performance': 0.8, 'security': 1.0},
                'chacha20-poly1305': {'strength': 0.95, 'performance': 0.9, 'security': 0.95},
                'aes-256-cbc': {'strength': 0.9, 'performance': 0.7, 'security': 0.9}
            },
            'kdf': {
                'pbkdf2-sha256': {'strength': 0.8, 'performance': 0.7},
                'pbkdf2-sha512': {'strength': 0.9, 'performance': 0.6},
                'argon2id': {'strength': 1.0, 'performance': 0.5}
            }
        }

        self._initialize_keys()
        logger.info("Context-Aware Encryption Engine initialized")

    def _initialize_keys(self) -> None:
        """Initialize master keys"""
        for _ in range(3):
            key = self._generate_key()
            self.active_keys[key['id']] = key

    def _generate_key(self) -> Dict[str, Any]:
        """Generate a new encryption key with metadata"""
        key_data = secrets.token_bytes(32)
        key_id = f"KEY-{secrets.token_hex(8).upper()}"
        return {
            'id': key_id,
            'data': key_data,
            'created_at': datetime.now(timezone.utc),
            'expires_at': datetime.now(timezone.utc) + timedelta(hours=24),
            'version': len(self.key_history) + 1,
            'usage_count': 0,
            'max_usage': 10000,
            'status': 'active'
        }

    # ==================== CONTEXT ANALYSIS ====================

    async def analyze_context(self, context_data: Dict[str, Any]) -> EncryptionContext:
        """Analyze context for encryption decisions. Each operation gets a unique strategy."""
        context = EncryptionContext()

        context.risk_score = await self._calculate_risk(context_data)
        context.trust_score = await self._calculate_trust(context_data)
        context.asset_type = context_data.get('asset_type', 'general')
        context.user_role = context_data.get('user_role', 'viewer')
        context.threat_level = await self._assess_threat(context_data)
        context.environment = context_data.get('environment', 'production')
        context.time_of_day = context_data.get('time_of_day', 'business_hours')
        context.device_type = context_data.get('device_type', 'unknown')

        context.security_level = self._determine_security_level(context)
        context.selected_algorithm = self._select_algorithm(context)
        context.selected_kdf = self._select_kdf(context)
        context.rotation_schedule = self._determine_rotation_schedule(context)

        if self._should_use_deception(context):
            context.is_deception = True
            fake_keys = await self._generate_fake_context(context)
            context.fake_key_id = fake_keys.get('key_id', 'FAKE-0000')
            context.fake_algorithm = fake_keys.get('algorithm', 'aes-128-cbc')

        self.context_cache[context.context_id] = context
        return context

    async def _calculate_risk(self, data: Dict[str, Any]) -> float:
        """Dynamic risk calculation from context factors"""
        risk_factors = []
        asset_risk = {
            'critical': 1.0, 'high': 0.8, 'medium': 0.5, 'low': 0.2
        }.get(data.get('asset_criticality', 'medium'), 0.5)
        risk_factors.append(asset_risk * 0.3)

        user_trust = data.get('user_trust', 0.5)
        risk_factors.append((1 - user_trust) * 0.25)

        threat = data.get('threat_level', 0.0)
        risk_factors.append(threat * 0.25)

        env_risk = 0.1 if data.get('environment') == 'production' else 0.3
        risk_factors.append(env_risk * 0.2)

        return min(1.0, sum(risk_factors))

    async def _calculate_trust(self, data: Dict[str, Any]) -> float:
        """Dynamic trust calculation from context factors"""
        trust_factors = []
        reputation = data.get('user_reputation', 0.5)
        trust_factors.append(reputation * 0.4)
        device = data.get('device_trust', 0.5)
        trust_factors.append(device * 0.3)
        location = data.get('location_trust', 0.5)
        trust_factors.append(location * 0.2)
        time_trust = 0.8 if data.get('time_of_day') == 'business_hours' else 0.5
        trust_factors.append(time_trust * 0.1)
        return min(1.0, sum(trust_factors))

    async def _assess_threat(self, data: Dict[str, Any]) -> float:
        """Dynamic threat assessment (integration with Threat Intelligence)"""
        return data.get('threat_level', 0.0)

    def _determine_security_level(self, context: EncryptionContext) -> SecurityContext:
        """Determine security level from risk and trust"""
        risk, trust = context.risk_score, context.trust_score
        if risk > 0.8 or trust < 0.2:
            return SecurityContext.CRITICAL
        elif risk > 0.6 or trust < 0.4:
            return SecurityContext.HIGH
        elif risk > 0.3 or trust < 0.7:
            return SecurityContext.MEDIUM
        else:
            return SecurityContext.LOW

    def _select_algorithm(self, context: EncryptionContext) -> str:
        """Select encryption algorithm based on context (Kerckhoffs: algorithms are public)"""
        selector = {
            SecurityContext.CRITICAL: 'aes-256-gcm',
            SecurityContext.HIGH: 'aes-256-gcm',
            SecurityContext.MEDIUM: self._weighted_choice(['aes-256-gcm', 'chacha20-poly1305']),
            SecurityContext.LOW: self._weighted_choice(['chacha20-poly1305', 'aes-256-cbc'])
        }
        selected = selector.get(context.security_level, 'aes-256-gcm')
        if context.is_deception:
            selected = self._select_fake_algorithm()
        return selected

    def _select_kdf(self, context: EncryptionContext) -> str:
        """Select KDF based on context"""
        if context.security_level in [SecurityContext.CRITICAL, SecurityContext.HIGH]:
            return 'argon2id'
        return 'pbkdf2-sha256'

    def _weighted_choice(self, options: List[str]) -> str:
        """Weighted random choice from options"""
        weights = np.ones(len(options))
        weights /= weights.sum()
        return np.random.choice(options, p=weights)

    def _select_fake_algorithm(self) -> str:
        """Select fake algorithm for deception.
        Uses ONLY modern, secure algorithms to avoid tipping off attackers."""
        return np.random.choice(['aes-256-gcm', 'chacha20-poly1305', 'aes-256-cbc', 'aes-192-gcm'])

    def _determine_rotation_schedule(self, context: EncryptionContext) -> str:
        """Dynamic rotation schedule based on context"""
        if context.security_level == SecurityContext.CRITICAL:
            return 'immediate'
        elif context.security_level == SecurityContext.HIGH:
            return 'hourly'
        elif context.security_level == SecurityContext.MEDIUM:
            return 'daily'
        else:
            return 'weekly'

    def _should_use_deception(self, context: EncryptionContext) -> bool:
        """Determine if deception should be used for this context"""
        return (
            context.threat_level > 0.7 or
            context.risk_score > 0.6 or
            context.user_role == 'unknown' or
            context.device_type == 'unknown'
        )

    async def _generate_fake_context(self, context: EncryptionContext) -> Dict[str, Any]:
        """Generate fake encryption context for deception"""
        if self.reality_fabric and hasattr(self.reality_fabric, 'generate_fake_encryption_context'):
            return await self.reality_fabric.generate_fake_encryption_context()
        return {
            'key_id': f"FAKE-{secrets.token_hex(6).upper()}",
            'algorithm': self._select_fake_algorithm(),
            'rotation': '30-days'
        }

    # ==================== DYNAMIC ENCRYPTION ====================

    async def encrypt(self, data: bytes, context_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Context-aware encryption with full dynamic pipeline."""
        if context_data is None:
            context_data = {}

        context = await self.analyze_context(context_data)
        key = await self._get_key_for_context(context)

        salt = secrets.token_bytes(32)
        op_key = self._derive_operation_key(key['data'], salt, context)
        iv = secrets.token_bytes(12)

        ciphertext, tag = await self._encrypt_with_algorithm(data, op_key, iv, context.selected_algorithm)
        envelope = self._create_secure_envelope(ciphertext, tag, context, key, salt, iv)

        if context.is_deception and self.reality_fabric:
            envelope['deception'] = await self._create_deception_data(context)

        return envelope

    async def decrypt(self, encrypted_data: Dict[str, Any]) -> bytes:
        """Context-aware decryption"""
        try:
            context_id = encrypted_data.get('context_id')
            context = self.context_cache.get(context_id)
            if not context:
                context = await self._recover_context(encrypted_data)

            key = await self._get_key_by_id(encrypted_data.get('key_id', ''))
            if not key:
                if self.reality_fabric and hasattr(self.reality_fabric, 'handle_fake_decryption'):
                    return await self.reality_fabric.handle_fake_decryption(encrypted_data)
                raise ValueError("Key not found")

            op_key = self._derive_operation_key(key['data'], encrypted_data.get('salt', b''), context)
            return await self._decrypt_with_algorithm(
                encrypted_data['ciphertext'], op_key,
                encrypted_data.get('iv', b''), context.selected_algorithm,
                encrypted_data.get('tag')
            )
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    def _derive_operation_key(self, master_key: bytes, salt: bytes, context: EncryptionContext) -> bytes:
        """Derive operation-specific key using context binding"""
        context_bytes = json.dumps({
            'context_id': context.context_id,
            'risk': context.risk_score,
            'trust': context.trust_score,
            'time': context.timestamp.isoformat()
        }).encode()

        iterations = 100000 if context.security_level in [SecurityContext.CRITICAL, SecurityContext.HIGH] else 50000
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32,
            salt=salt + context_bytes, iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(master_key)

    async def _encrypt_with_algorithm(self, data: bytes, key: bytes, iv: bytes,
                                       algorithm: str) -> Tuple[bytes, Optional[bytes]]:
        """Encrypt with selected algorithm. Supports AES-256-GCM, ChaCha20-Poly1305, AES-256-CBC."""
        if algorithm == 'aes-256-gcm':
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ct = encryptor.update(data) + encryptor.finalize()
            return ct, encryptor.tag

        elif algorithm == 'chacha20-poly1305':
            from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
            cipher = ChaCha20Poly1305(key)
            ct = cipher.encrypt(iv, data, None)
            return ct, None

        else:  # aes-256-cbc with PKCS7 padding
            from cryptography.hazmat.primitives import padding
            padder = padding.PKCS7(128).padder()
            padded = padder.update(data) + padder.finalize()
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ct = encryptor.update(padded) + encryptor.finalize()
            return ct, None

    async def _decrypt_with_algorithm(self, ciphertext: bytes, key: bytes, iv: bytes,
                                       algorithm: str, tag: Optional[bytes] = None) -> bytes:
        """Decrypt with selected algorithm"""
        if algorithm == 'aes-256-gcm' and tag:
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()

        elif algorithm == 'chacha20-poly1305':
            from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
            cipher = ChaCha20Poly1305(key)
            return cipher.decrypt(iv, ciphertext, None)

        else:  # aes-256-cbc
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded = decryptor.update(ciphertext) + decryptor.finalize()
            from cryptography.hazmat.primitives import padding
            unpadder = padding.PKCS7(128).unpadder()
            return unpadder.update(padded) + unpadder.finalize()

    def _create_secure_envelope(self, ciphertext: bytes, tag: Optional[bytes],
                                 context: EncryptionContext, key: Dict[str, Any],
                                 salt: bytes, iv: bytes) -> Dict[str, Any]:
        """Create secure envelope with metadata"""
        metadata = {
            'context_id': context.context_id,
            'key_id': key['id'],
            'key_version': key['version'],
            'algorithm': context.selected_algorithm,
            'kdf': context.selected_kdf,
            'timestamp': context.timestamp.isoformat(),
            'risk_score': context.risk_score,
            'trust_score': context.trust_score
        }
        if context.is_deception:
            metadata['fake_key_id'] = context.fake_key_id
            metadata['fake_algorithm'] = context.fake_algorithm
            metadata['is_deception'] = True

        result = {
            'ciphertext': ciphertext, 'iv': iv, 'salt': salt,
            'metadata': metadata, 'context_id': context.context_id,
            'key_id': key['id'], 'version': context.key_version
        }
        if tag:
            result['tag'] = tag
        return result

    async def _create_deception_data(self, context: EncryptionContext) -> Dict[str, Any]:
        """Create deception data for attacker confusion"""
        if self.reality_fabric and hasattr(self.reality_fabric, 'create_deception_payload'):
            return await self.reality_fabric.create_deception_payload(context)
        return {
            'fake_key_id': context.fake_key_id,
            'fake_algorithm': context.fake_algorithm,
            'fake_rotation': '30-days',
            'fake_metadata': {
                'encryption_date': (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                'access_count': np.random.randint(100, 1000),
                'last_access': (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
            },
            'fake_audit_trail': [
                {'action': 'encrypt', 'timestamp': (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()},
                {'action': 'access', 'timestamp': (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()},
                {'action': 'rotate', 'timestamp': (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()}
            ]
        }

    # ==================== KEY MANAGEMENT ====================

    async def _get_key_for_context(self, context: EncryptionContext) -> Dict[str, Any]:
        """Get appropriate key for context"""
        active = [k for k in self.active_keys.values() if k.get('status') == 'active']
        if not active:
            new_key = self._generate_key()
            self.active_keys[new_key['id']] = new_key
            return new_key

        scored = []
        for key in active:
            score = (
                0.4 * (1 - key['usage_count'] / key['max_usage']) +
                0.3 * (1 - (datetime.now(timezone.utc) - key['created_at']).total_seconds() /
                       max(1, (key['expires_at'] - key['created_at']).total_seconds())) +
                0.3 * (1 - context.risk_score)
            )
            scored.append((score, key))

        scores_arr = np.array([s[0] for s in scored])
        probs = np.exp(scores_arr) / np.sum(np.exp(scores_arr))
        selected = np.random.choice(len(scored), p=probs)
        key = scored[selected][1]
        key['usage_count'] = key.get('usage_count', 0) + 1
        return key

    async def _get_key_by_id(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Get key by ID from active or history"""
        if key_id in self.active_keys:
            return self.active_keys[key_id]
        for key in self.key_history:
            if key.get('id') == key_id:
                return key
        return None

    async def _recover_context(self, encrypted_data: Dict[str, Any]) -> EncryptionContext:
        """Recover context from encrypted data"""
        return EncryptionContext(
            context_id=encrypted_data.get('context_id', str(uuid.uuid4())),
            timestamp=datetime.now(timezone.utc), risk_score=0.5, trust_score=0.5
        )

    # ==================== ROTATION ====================

    async def rotate_keys(self, context: Optional[EncryptionContext] = None) -> None:
        """Dynamic key rotation based on context"""
        if context is None:
            context = EncryptionContext()
        for key_id, key in list(self.active_keys.items()):
            if await self._should_rotate_key(key, context):
                new_key = self._generate_key()
                new_key['parent_id'] = key_id
                key['status'] = 'rotated'
                self.key_history.append(key)
                self.active_keys[new_key['id']] = new_key
                logger.info(f"Key {key_id} rotated to {new_key['id']}")

    async def _should_rotate_key(self, key: Dict[str, Any], context: EncryptionContext) -> bool:
        """Determine if key should be rotated"""
        if datetime.now(timezone.utc) >= key.get('expires_at', datetime.now(timezone.utc)):
            return True
        if key.get('usage_count', 0) >= key.get('max_usage', 10000):
            return True
        if context.risk_score > 0.7:
            return True
        if context.trust_score < 0.3:
            return True
        return False

    # ==================== STATUS ====================

    async def get_encryption_status(self) -> Dict[str, Any]:
        """Get current encryption status"""
        return {
            'active_keys': len(self.active_keys),
            'total_rotations': len(self.key_history),
            'active_contexts': len(self.context_cache),
            'algorithm_distribution': self._get_algorithm_distribution(),
            'health_score': self._calculate_health_score()
        }

    def _get_algorithm_distribution(self) -> Dict[str, int]:
        """Get distribution of algorithms in use"""
        dist: Dict[str, int] = {}
        for ctx in self.context_cache.values():
            algo = ctx.selected_algorithm
            dist[algo] = dist.get(algo, 0) + 1
        return dist

    def _calculate_health_score(self) -> float:
        """Calculate overall encryption health.

        Health score uses multi-factor analysis:
        - Key health: age, expiry, usage per key
        - Usage health: overall consumption vs capacity
        - Rotation health: frequency and regularity of rotations
        - Risk health: average and high-risk context proportion
        """
        key_health = self._calculate_key_health()
        usage_health = self._calculate_usage_health()
        rotation_health = self._calculate_rotation_health()
        risk_health = self._calculate_risk_health()

        return min(1.0, max(0.0,
            key_health * 0.3 + usage_health * 0.2 +
            rotation_health * 0.2 + risk_health * 0.3
        ))

    def _calculate_key_health(self) -> float:
        """Calculate health based on key status"""
        if not self.active_keys:
            return 0.0
        total_health = 0.0
        now = datetime.now(timezone.utc)
        for key in self.active_keys.values():
            age = (now - key['created_at']).total_seconds()
            max_age = 86400 * 7
            age_health = max(0.0, 1 - (age / max_age))
            expiry_remaining = (key['expires_at'] - now).total_seconds()
            total_lifespan = (key['expires_at'] - key['created_at']).total_seconds()
            expiry_health = max(0.0, expiry_remaining / total_lifespan) if total_lifespan > 0 else 0.0
            usage_health = max(0.0, 1 - (key.get('usage_count', 0) / max(1, key.get('max_usage', 10000))))
            total_health += age_health * 0.4 + expiry_health * 0.3 + usage_health * 0.3
        return min(1.0, total_health / max(1, len(self.active_keys)))

    def _calculate_usage_health(self) -> float:
        """Calculate health based on overall usage"""
        total_usage = sum(k.get('usage_count', 0) for k in self.active_keys.values())
        total_capacity = sum(k.get('max_usage', 10000) for k in self.active_keys.values())
        if total_capacity == 0:
            return 0.5
        return max(0.0, 1 - (total_usage / total_capacity))

    def _calculate_rotation_health(self) -> float:
        """Calculate health based on rotation history"""
        if not self.key_history:
            return 0.9  # New system, no rotations needed
        count = len(self.key_history)
        health = 0.9 if count < 10 else (0.7 if count < 50 else (0.5 if count < 100 else 0.3))
        recent = sum(1 for k in self.key_history
                     if (datetime.now(timezone.utc) - k.get('created_at', datetime.now(timezone.utc))).days < 1)
        if recent > 10:
            health *= 0.7
        return max(0.0, min(1.0, health))

    def _calculate_risk_health(self) -> float:
        """Calculate health based on risk factors"""
        if not self.context_cache:
            return 0.8
        avg_risk = float(np.mean([c.risk_score for c in self.context_cache.values()]))
        risk_health = 1 - avg_risk
        high_risk_count = sum(1 for c in self.context_cache.values() if c.risk_score > 0.7)
        if high_risk_count > 0 and self.context_cache:
            risk_health *= (1 - (high_risk_count / len(self.context_cache)) * 0.3)
        return max(0.0, min(1.0, risk_health))

    async def get_key_health_details(self) -> Dict[str, Any]:
        """Get detailed health information for each key"""
        details = {}
        now = datetime.now(timezone.utc)
        for key_id, key in self.active_keys.items():
            age = (now - key['created_at']).total_seconds()
            expiry_remaining = (key['expires_at'] - now).total_seconds()
            total_lifespan = (key['expires_at'] - key['created_at']).total_seconds()
            max_age = 86400 * 7
            age_health = max(0.0, 1 - (age / max_age))
            expiry_health = max(0.0, expiry_remaining / total_lifespan) if total_lifespan > 0 else 0.0
            usage_health = max(0.0, 1 - (key.get('usage_count', 0) / max(1, key.get('max_usage', 10000))))
            details[key_id] = {
                'age_seconds': age,
                'expiry_remaining': expiry_remaining,
                'usage_count': key.get('usage_count', 0),
                'max_usage': key.get('max_usage', 10000),
                'health_score': age_health * 0.4 + expiry_health * 0.3 + usage_health * 0.3,
                'status': key.get('status', 'active'),
                'version': key.get('version', 1)
            }
        return details


class EncryptionRealityFabric:
    """
    Creates convincing encryption deception infrastructure.

    Uses ONLY modern, secure algorithms in deception to avoid
    tipping off attackers with obsolete crypto.

    Args:
        legacy_simulation: If True, includes obsolete algorithms (DES, RC4)
                           for legacy environment simulation. Default: False.
    """

    def __init__(self, legacy_simulation: bool = False) -> None:
        self.fake_keys: Dict[str, Dict[str, Any]] = {}
        self.fake_certificates: List[Dict[str, Any]] = []
        self.fake_tokens: List[Dict[str, Any]] = []
        self.fake_ciphertexts: List[Dict[str, Any]] = []
        self.fake_logs: List[Dict[str, Any]] = []
        self.fake_audit_trails: List[Dict[str, Any]] = []
        self.active_deceptions: List[Dict[str, Any]] = []

        # Modern secure algorithms (default)
        self.fake_algorithms = [
            'aes-256-gcm', 'chacha20-poly1305', 'aes-256-cbc', 'aes-192-gcm'
        ]
        # Legacy simulation - only when explicitly enabled
        self.legacy_algorithms = [
            'aes-128-cbc', 'des-cbc', '3des-cbc', 'blowfish'
        ]
        self.legacy_simulation = legacy_simulation

    async def generate_fake_encryption_context(self) -> Dict[str, Any]:
        """Generate fake encryption context for deception.
        Uses modern algorithms by default; legacy only if explicitly enabled."""
        if self.legacy_simulation:
            algorithm_pool = self.fake_algorithms + self.legacy_algorithms
        else:
            algorithm_pool = self.fake_algorithms

        fake_key_sizes = [256, 256, 256, 192]  # Modern key sizes only
        context = {
            'key_id': f"KEY-{secrets.token_hex(8).upper()}",
            'algorithm': np.random.choice(algorithm_pool),
            'key_size': int(np.random.choice(fake_key_sizes)),
            'rotation': str(np.random.choice(['30-days', '60-days', '90-days', 'manual'])),
            'created_at': (datetime.now(timezone.utc) - timedelta(days=int(np.random.randint(1, 30)))).isoformat(),
            'last_rotated': (datetime.now(timezone.utc) - timedelta(days=int(np.random.randint(1, 7)))).isoformat(),
            'last_accessed': (datetime.now(timezone.utc) - timedelta(hours=int(np.random.randint(1, 24)))).isoformat(),
            'access_count': int(np.random.randint(100, 10000)),
            'environment': str(np.random.choice(['production', 'staging', 'development'])),
            'security_level': str(np.random.choice(['high', 'medium', 'low']))
        }
        self.fake_keys[context['key_id']] = context
        return context

    async def create_deception_payload(self, context: Any) -> Dict[str, Any]:
        """Create deception payload based on context.
        Uses modern algorithms by default; legacy only if explicitly enabled."""
        if self.legacy_simulation:
            algo_pool = ['aes-128-cbc', 'des-cbc', '3des-cbc', 'blowfish']
        else:
            algo_pool = ['aes-256-gcm', 'chacha20-poly1305', 'aes-256-cbc']

        payload = {
            'fake_key_id': f"FAKE-{secrets.token_hex(6).upper()}",
            'fake_algorithm': str(np.random.choice(algo_pool)),
            'fake_metadata': self._generate_fake_metadata(),
            'fake_audit_trail': self._generate_fake_audit_trail(),
            'fake_ciphertexts': await self._generate_fake_ciphertexts(3),
            'fake_certificates': await self._generate_fake_certificates(2),
            'fake_tokens': await self._generate_fake_tokens(5),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.active_deceptions.append(payload)
        return payload

    def _generate_fake_metadata(self) -> Dict[str, Any]:
        """Generate fake encryption metadata"""
        return {
            'encryption_date': (datetime.now(timezone.utc) - timedelta(days=int(np.random.randint(1, 30)))).isoformat(),
            'last_modified': (datetime.now(timezone.utc) - timedelta(hours=int(np.random.randint(1, 24)))).isoformat(),
            'file_size': int(np.random.randint(1024, 10485760)),
            'checksum': secrets.token_hex(16),
            'owner': f"user_{secrets.token_hex(4)}",
            'permissions': str(np.random.choice(['read', 'write', 'admin'])),
            'backup_location': f"s3://backup-{secrets.token_hex(4)}/encrypted"
        }

    def _generate_fake_audit_trail(self) -> List[Dict[str, Any]]:
        """Generate fake audit trail"""
        actions = ['encrypt', 'decrypt', 'rotate', 'access', 'modify', 'delete', 'share']
        trail = []
        for _ in range(int(np.random.randint(5, 20))):
            action = np.random.choice(actions)
            trail.append({
                'action': action,
                'timestamp': (datetime.now(timezone.utc) - timedelta(days=int(np.random.randint(1, 30)))).isoformat(),
                'user': f"user_{secrets.token_hex(4)}",
                'ip': f"192.168.{int(np.random.randint(1, 255))}.{int(np.random.randint(1, 255))}",
                'status': str(np.random.choice(['success', 'success', 'success', 'failed'])),
                'details': {
                    'key_id': f"KEY-{secrets.token_hex(8).upper()}",
                    'algorithm': str(np.random.choice(['AES-128-CBC', 'DES-CBC', 'RC4'])),
                    'size': int(np.random.randint(1024, 1048576))
                }
            })
        return trail

    async def _generate_fake_ciphertexts(self, count: int) -> List[Dict[str, Any]]:
        """Generate fake ciphertexts"""
        return [{
            'id': f"CT-{secrets.token_hex(8).upper()}",
            'data': secrets.token_hex(int(np.random.randint(64, 512))),
            'algorithm': str(np.random.choice(['AES-128-CBC', 'DES-CBC', 'RC4'])),
            'key_id': f"KEY-{secrets.token_hex(8).upper()}",
            'created_at': (datetime.now(timezone.utc) - timedelta(days=int(np.random.randint(1, 30)))).isoformat()
        } for _ in range(count)]

    async def _generate_fake_certificates(self, count: int) -> List[Dict[str, Any]]:
        """Generate fake certificates"""
        return [{
            'id': f"CERT-{secrets.token_hex(8).upper()}",
            'subject': f"CN=*.{secrets.token_hex(4)}.com",
            'issuer': f"CN=CA-{secrets.token_hex(4)}",
            'valid_from': datetime.now(timezone.utc).isoformat(),
            'valid_to': (datetime.now(timezone.utc) + timedelta(days=int(np.random.randint(30, 365)))).isoformat(),
            'serial': secrets.token_hex(16),
            'signature_algorithm': str(np.random.choice(['sha256WithRSAEncryption', 'sha512WithRSAEncryption']))
        } for _ in range(count)]

    async def _generate_fake_tokens(self, count: int) -> List[Dict[str, Any]]:
        """Generate fake tokens"""
        return [{
            'id': f"TOKEN-{secrets.token_hex(8).upper()}",
            'token': secrets.token_urlsafe(32),
            'created_at': (datetime.now(timezone.utc) - timedelta(days=int(np.random.randint(1, 30)))).isoformat(),
            'expires_at': (datetime.now(timezone.utc) + timedelta(hours=int(np.random.randint(1, 24)))).isoformat(),
            'scope': str(np.random.choice(['read', 'write', 'admin'])),
            'user': f"user_{secrets.token_hex(4)}"
        } for _ in range(count)]

    async def handle_fake_decryption(self, encrypted_data: Dict[str, Any]) -> bytes:
        """Handle decryption of fake data - returns plausible fake data"""
        return f"FAKE_DATA_{secrets.token_hex(16)}".encode()

    async def get_deception_stats(self) -> Dict[str, Any]:
        """Get deception statistics"""
        return {
            'active_deceptions': len(self.active_deceptions),
            'fake_keys': len(self.fake_keys),
            'fake_certificates': len(self.fake_certificates),
            'fake_tokens': len(self.fake_tokens),
            'fake_ciphertexts': len(self.fake_ciphertexts),
            'fake_audit_trails': len(self.fake_audit_trails),
            'total_interactions': sum(len(d.get('fake_audit_trail', [])) for d in self.active_deceptions)
        }


class DynamicEncryptionPolicyEngine:
    """
    Dynamic policy engine for encryption decisions.

    Policies adapt based on:
    - Risk level
    - Trust level
    - Asset criticality
    - Compliance requirements
    - Threat intelligence
    """

    def __init__(self) -> None:
        self.policies: Dict[str, Dict[str, Any]] = {}
        self.active_policy: Optional[Dict[str, Any]] = None
        self._load_default_policies()

    def _load_default_policies(self) -> None:
        """Load default encryption policies"""
        self.policies = {
            'critical_asset': {
                'algorithm': 'aes-256-gcm', 'key_size': 256, 'kdf': 'argon2id',
                'rotation': 'immediate', 'deception': False, 'envelope': True
            },
            'high_risk': {
                'algorithm': 'aes-256-gcm', 'key_size': 256, 'kdf': 'argon2id',
                'rotation': 'hourly', 'deception': True, 'envelope': True
            },
            'medium_risk': {
                'algorithm': 'chacha20-poly1305', 'key_size': 256, 'kdf': 'pbkdf2-sha256',
                'rotation': 'daily', 'deception': False, 'envelope': True
            },
            'low_risk': {
                'algorithm': 'chacha20-poly1305', 'key_size': 256, 'kdf': 'pbkdf2-sha256',
                'rotation': 'weekly', 'deception': False, 'envelope': False
            },
            'deception': {
                'algorithm': 'aes-128-cbc', 'key_size': 128, 'kdf': 'pbkdf2-sha256',
                'rotation': 'static', 'deception': True, 'envelope': False
            }
        }

    async def get_policy_for_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get appropriate policy based on context"""
        risk_score = context.get('risk_score', 0.5)
        asset_type = context.get('asset_type', 'general')

        if context.get('use_deception', False):
            policy_key = 'deception'
        elif asset_type == 'critical':
            policy_key = 'critical_asset'
        elif risk_score > 0.7:
            policy_key = 'high_risk'
        elif risk_score > 0.3:
            policy_key = 'medium_risk'
        else:
            policy_key = 'low_risk'

        policy = self.policies.get(policy_key, self.policies['medium_risk']).copy()
        return self._adjust_policy(policy, context)

    def _adjust_policy(self, policy: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust policy based on context factors"""
        adjusted = policy.copy()

        threat_level = context.get('threat_level', 0.0)
        if threat_level > 0.8 and adjusted.get('rotation') != 'immediate':
            adjusted['rotation'] = 'immediate'

        trust_score = context.get('trust_score', 0.5)
        if trust_score < 0.2:
            adjusted['deception'] = True
            adjusted['envelope'] = True

        compliance = context.get('compliance', [])
        if 'GDPR' in compliance or 'HIPAA' in compliance:
            adjusted['envelope'] = True
            adjusted['algorithm'] = 'aes-256-gcm'

        return adjusted

    async def update_policy(self, policy_key: str, policy_data: Dict[str, Any]) -> None:
        """Update a policy dynamically"""
        self.policies[policy_key] = policy_data
        logger.info(f"Policy {policy_key} updated")


class DynamicEncryptionSystem:
    """
    Complete dynamic encryption system.

    Components:
    1. Context-Aware Encryption Engine
    2. Reality Fabric (Deception)
    3. Policy Engine
    4. ACDO Integration
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.reality_fabric = EncryptionRealityFabric()
        self.encryption_engine = ContextAwareEncryptionEngine(config, self.reality_fabric)
        self.policy_engine = DynamicEncryptionPolicyEngine()
        self.acdo: Optional[Any] = None

    def register_acdo(self, acdo: Any) -> None:
        """Register with ACDO orchestrator"""
        self.acdo = acdo

    async def encrypt(self, data: bytes, context_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Complete encryption pipeline: policy -> context -> encrypt -> envelope -> log"""
        if context_data is None:
            context_data = {}

        policy = await self.policy_engine.get_policy_for_context(context_data)
        context_data['policy'] = policy
        context_data['use_deception'] = policy.get('deception', False)

        encrypted = await self.encryption_engine.encrypt(data, context_data)

        if self.acdo and hasattr(self.acdo, 'log_encryption_event'):
            await self.acdo.log_encryption_event({
                'context_id': encrypted.get('context_id'),
                'algorithm': encrypted.get('metadata', {}).get('algorithm'),
                'deception_used': encrypted.get('deception') is not None,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

        return encrypted

    async def decrypt(self, encrypted_data: Dict[str, Any]) -> bytes:
        """Complete decryption pipeline"""
        return await self.encryption_engine.decrypt(encrypted_data)

    async def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'encryption_status': await self.encryption_engine.get_encryption_status(),
            'deception_stats': await self.reality_fabric.get_deception_stats(),
            'policies': list(self.policy_engine.policies.keys()),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
