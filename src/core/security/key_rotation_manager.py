"""
Intelligent Key Rotation Manager for BLACK VEIL
Time-based, usage-based, and risk-based key rotation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import secrets
import hashlib
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class KeyInfo:
    """Information about a key"""
    id: str
    created_at: datetime
    expires_at: datetime
    usage_count: int
    max_usage: int
    status: str  # active, expiring, rotated, revoked
    algorithm: str
    key_hash: str

class KeyRotationManager:
    """
    Manages key rotation based on multiple factors
    
    Rotation Triggers:
    - Time-based: Keys expire after defined period
    - Usage-based: Keys rotate after max usage
    - Risk-based: Keys rotate on high risk
    - Event-based: Security events trigger rotation
    """
    
    def __init__(self):
        self.active_keys: Dict[str, KeyInfo] = {}
        self.rotation_history: List[Dict] = []
        self.key_log = []
        
        # Default policies
        self.policies = {
            'short_lived': {'max_age_hours': 0.25, 'max_usage': 1000},      # 15 minutes
            'medium_lived': {'max_age_hours': 8, 'max_usage': 10000},       # 8 hours
            'long_lived': {'max_age_hours': 72, 'max_usage': 100000},       # 3 days
            'critical': {'max_age_hours': 0.5, 'max_usage': 500},           # 30 minutes
        }
    
    def generate_key(self, policy: str = 'medium_lived', 
                     algorithm: str = 'aes-256-gcm',
                     context: Dict = None) -> KeyInfo:
        """Generate a new key with rotation policy"""
        if context is None:
            context = {}
        
        policy_config = self.policies.get(policy, self.policies['medium_lived'])
        
        # Adjust policy based on risk
        risk_score = context.get('risk_score', 0.5)
        if risk_score > 0.8:
            policy_config = self.policies['critical']
        elif risk_score > 0.6:
            policy_config = self.policies['short_lived']
        
        # Generate key
        key_data = secrets.token_bytes(32)
        key_id = f"KEY-{secrets.token_hex(8).upper()}"
        
        # Calculate expiry
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(hours=policy_config['max_age_hours'])
        
        key_info = KeyInfo(
            id=key_id,
            created_at=created_at,
            expires_at=expires_at,
            usage_count=0,
            max_usage=policy_config['max_usage'],
            status='active',
            algorithm=algorithm,
            key_hash=hashlib.sha256(key_data).hexdigest()[:8]
        )
        
        self.active_keys[key_id] = key_info
        
        logger.info(f"Generated key {key_id} with policy {policy}")
        
        return key_info
    
    def rotate_key(self, key_id: str, reason: str) -> Optional[KeyInfo]:
        """Rotate a specific key"""
        if key_id not in self.active_keys:
            logger.error(f"Key {key_id} not found")
            return None
        
        old_key = self.active_keys[key_id]
        old_key.status = 'rotated'
        
        self.rotation_history.append({
            'old_key': key_id,
            'timestamp': datetime.utcnow(),
            'reason': reason,
            'new_key': None
        })
        
        # Generate new key
        new_key = self.generate_key(
            policy='medium_lived',
            algorithm=old_key.algorithm
        )
        
        self.rotation_history[-1]['new_key'] = new_key.id
        
        logger.info(f"Rotated key {key_id} to {new_key.id} due to {reason}")
        
        return new_key
    
    def check_rotation_needed(self) -> List[str]:
        """Check which keys need rotation"""
        keys_to_rotate = []
        now = datetime.utcnow()
        
        for key_id, key in self.active_keys.items():
            if key.status != 'active':
                continue
            
            # Time-based rotation
            if now >= key.expires_at:
                keys_to_rotate.append(key_id)
                continue
            
            # Usage-based rotation
            if key.usage_count >= key.max_usage:
                keys_to_rotate.append(key_id)
                continue
        
        return keys_to_rotate
    
    def emergency_rotation(self, reason: str) -> List[str]:
        """Emergency rotation of all keys"""
        rotated_keys = []
        
        for key_id in list(self.active_keys.keys()):
            new_key = self.rotate_key(key_id, f"EMERGENCY: {reason}")
            if new_key:
                rotated_keys.append(new_key.id)
        
        logger.warning(f"Emergency rotation completed for {len(rotated_keys)} keys")
        return rotated_keys
    
    def get_key_info(self, key_id: str) -> Optional[Dict]:
        """Get information about a key"""
        if key_id in self.active_keys:
            key = self.active_keys[key_id]
            return {
                'id': key.id,
                'status': key.status,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat(),
                'usage_count': key.usage_count,
                'max_usage': key.max_usage,
                'algorithm': key.algorithm
            }
        return None
    
    def get_rotation_metrics(self) -> Dict:
        """Get rotation metrics"""
        return {
            'active_keys': len(self.active_keys),
            'total_rotations': len(self.rotation_history),
            'keys_need_rotation': len(self.check_rotation_needed()),
            'last_rotation': self.rotation_history[-1]['timestamp'].isoformat() if self.rotation_history else None
        }
