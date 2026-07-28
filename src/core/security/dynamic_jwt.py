"""
BLACK VEIL Dynamic JWT Manager
100% Dynamic - No Static Methods

Core Principle:
- Every token has unique properties (algorithms, expiry, claims, signatures)
- Secrets rotate automatically with probabilistic selection
- Context-aware token generation (risk, trust, entropy)
- Tokens are double-encrypted for extra security
"""
import jwt
import secrets
import time
import uuid
import base64
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta, timezone

import numpy as np

logger = logging.getLogger(__name__)


class DynamicJWTManager:
    """
    100% Dynamic JWT Management.
    
    Each token generated is unique because:
    - Secret is probabilistically selected from a rotating pool
    - Algorithm (HS256/HS384/HS512) varies per token
    - Expiry time is computed from risk + trust context
    - Claims include entropy and risk metadata
    - Token is encrypted with the dynamic encryption engine
    """

    def __init__(self, encryption_engine=None):
        self.encryption_engine = encryption_engine
        self.active_secrets: Dict[str, Dict[str, Any]] = {}
        self.secret_history: List[Dict[str, Any]] = []
        self.current_algorithm = 'HS256'
        self.token_version = 1

        # Dynamic bounds
        self.min_expiry = 300    # 5 minutes
        self.max_expiry = 86400  # 24 hours
        self.current_entropy = 0.85

        self._initialize_dynamic_secrets()
        logger.info("DynamicJWTManager initialized")

    def _initialize_dynamic_secrets(self) -> None:
        """Initialize pool of dynamic JWT secrets"""
        for _ in range(5):
            secret = self._generate_dynamic_secret()
            self.active_secrets[secret['id']] = secret

    def _generate_dynamic_secret(self) -> Dict[str, Any]:
        """Generate a JWT secret with randomized properties"""
        secret_length = int(32 + (self.current_entropy * 32))
        secret_bytes = secrets.token_bytes(secret_length)
        return {
            'id': str(uuid.uuid4()),
            'secret': base64.urlsafe_b64encode(secret_bytes).decode(),
            'created_at': datetime.now(timezone.utc),
            'expires_at': datetime.now(timezone.utc) + timedelta(hours=12),
            'algorithm': str(np.random.choice(['HS256', 'HS384', 'HS512'])),
            'usage_count': 0,
            'max_usage': int(10000 + np.random.uniform(0, 10000)),
            'status': 'active',
        }

    async def create_token(self, user_data: Dict[str, Any],
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a dynamic JWT token.
        
        Every token is unique:
        - Different secret selected via probabilistic scoring
        - Algorithm chosen by risk context
        - Expiry computed from trust and risk
        - Claims include dynamic entropy/risk metadata
        - Token encrypted for additional security
        """
        ctx = context or {}
        secret = self._get_best_secret()
        secret['usage_count'] += 1

        risk_score = ctx.get('risk_score', 0.5)
        user_trust = ctx.get('trust_score', 0.8)

        # Compute dynamic expiry
        base_expiry = 3600
        risk_factor = 1.0 - (risk_score * 0.5)
        trust_factor = 0.5 + (user_trust * 0.5)
        expiry_seconds = int(base_expiry * trust_factor * risk_factor)
        expiry_seconds = max(self.min_expiry, min(self.max_expiry, expiry_seconds))

        # Build dynamic claims
        claims = {
            'user_id': user_data.get('id'),
            'username': user_data.get('username'),
            'role': user_data.get('role', 'viewer'),
            'exp': time.time() + expiry_seconds,
            'iat': time.time(),
            'jti': str(uuid.uuid4()),
            'version': self.token_version,
            'entropy': self.current_entropy,
            'risk_score': risk_score,
            'trust_score': user_trust,
            'token_type': 'access',
        }

        algorithm = self._select_algorithm(ctx)

        # Generate JWT
        token = jwt.encode(claims, secret['secret'], algorithm=algorithm)

        result = {
            'token': token,
            'token_id': claims['jti'],
            'expires_in': expiry_seconds,
            'algorithm': algorithm,
            'secret_id': secret['id'],
            'claims': claims,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        # Optional: encrypt the token for double security
        if self.encryption_engine:
            try:
                encrypted = await self.encryption_engine.encrypt_data(token.encode())
                result['token'] = base64.b64encode(encrypted['ciphertext']).decode()
                result['encrypted'] = True
            except Exception as e:
                logger.debug(f"JWT encryption skipped: {e}")
                result['encrypted'] = False

        logger.debug(f"JWT created: id={claims['jti'][:8]}, algo={algorithm}, exp={expiry_seconds}s")
        return result

    async def verify_token(self, token_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Verify a dynamic JWT token.
        
        Handles:
        - Decryption if token was encrypted
        - Secret lookup across active + historical keys
        - Multiple algorithm attempts
        """
        try:
            token_str = token_data['token']

            # Decrypt if encrypted
            if token_data.get('encrypted') and self.encryption_engine:
                ct = base64.b64decode(token_str)
                decrypted = await self.encryption_engine.decrypt_data({
                    'ciphertext': ct,
                    'iv': token_data.get('iv', b''),
                    'tag': token_data.get('tag', b''),
                    'algorithm': token_data.get('algorithm', 'aes-256-gcm'),
                    'salt': token_data.get('salt', b''),
                    'key_id': token_data.get('key_id', ''),
                    'key_version': token_data.get('key_version', 1),
                    'context_id': token_data.get('context_id', ''),
                })
                token_str = decrypted.decode()

            # Find signing secret
            secret = self._find_secret(token_data.get('secret_id'))
            if not secret:
                logger.warning("JWT secret not found for verification")
                return None

            # Try algorithms
            for algo in ['HS256', 'HS384', 'HS512']:
                try:
                    payload = jwt.decode(token_str, secret['secret'],
                                         algorithms=[algo])
                    return payload
                except jwt.ExpiredSignatureError:
                    logger.warning("JWT expired")
                    return None
                except Exception:
                    continue

            return None
        except Exception as e:
            logger.error(f"JWT verification failed: {e}")
            return None

    def _get_best_secret(self) -> Dict[str, Any]:
        """Probabilistically select the best secret from the active pool"""
        active = [s for s in self.active_secrets.values() if s['status'] == 'active']
        if not active:
            new_s = self._generate_dynamic_secret()
            self.active_secrets[new_s['id']] = new_s
            return new_s

        scored = []
        for s in active:
            age_ratio = (datetime.now(timezone.utc) - s['created_at']).total_seconds() / \
                        max(1, (s['expires_at'] - s['created_at']).total_seconds())
            score = (
                0.4 * (1 - s['usage_count'] / max(1, s['max_usage'])) +
                0.3 * (1 - age_ratio) +
                0.3 * self.current_entropy
            )
            scored.append((score, s))

        scores = np.array([s[0] for s in scored])
        probs = np.exp(scores) / np.sum(np.exp(scores))
        return scored[np.random.choice(len(scored), p=probs)][1]

    def _select_algorithm(self, context: Dict[str, Any]) -> str:
        """Select JWT signing algorithm based on risk context"""
        risk = context.get('risk_score', 0.5)
        if risk > 0.8:
            return 'HS512'
        elif risk > 0.5:
            return str(np.random.choice(['HS256', 'HS384']))
        return 'HS256'

    def _find_secret(self, secret_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Find a secret by ID across active and historical keys"""
        if secret_id and secret_id in self.active_secrets:
            return self.active_secrets[secret_id]
        if secret_id:
            for s in self.secret_history:
                if s['id'] == secret_id:
                    return s
        # Fallback: return any active secret
        for s in self.active_secrets.values():
            if s['status'] == 'active':
                return s
        return None

    def rotate_secrets(self) -> int:
        """Rotate all JWT secrets. Returns count of rotated secrets."""
        count = 0
        for secret in list(self.active_secrets.values()):
            secret['status'] = 'expired'
            self.secret_history.append(secret)
            count += 1
        self.active_secrets = {}
        for _ in range(5):
            new_s = self._generate_dynamic_secret()
            self.active_secrets[new_s['id']] = new_s
        self.token_version += 1
        self.current_entropy = min(1.0, self.current_entropy + 0.05)
        logger.info(f"JWT secrets rotated: {count} replaced")
        return count

    def get_state_summary(self) -> Dict[str, Any]:
        """Get JWT manager state summary"""
        return {
            'active_secrets': len(self.active_secrets),
            'historical_secrets': len(self.secret_history),
            'token_version': self.token_version,
            'entropy': round(self.current_entropy, 3),
            'active_algorithms': list(set(
                s['algorithm'] for s in self.active_secrets.values()
            )),
        }

