"""
BLACK VEIL V5 - Cryptographic Utilities
Encryption, hashing, and secure random generation
"""
import base64
import hashlib
import hmac
import os
import secrets
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoUtils:
    """Cryptographic utility functions"""

    @staticmethod
    def generate_key(length: int = 32) -> str:
        """Generate a cryptographically secure random key"""
        return base64.urlsafe_b64encode(os.urandom(length)).decode()

    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
        """Hash a password using PBKDF2-SHA256"""
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode())).decode()
        return key, salt

    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: bytes) -> bool:
        """Verify a password against its hash"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        try:
            derived = base64.urlsafe_b64encode(kdf.derive(password.encode())).decode()
            return hmac.compare_digest(derived, stored_hash)
        except Exception:
            return False

    @staticmethod
    def get_fernet(key: Optional[str] = None) -> Fernet:
        """Get a Fernet cipher instance"""
        if key is None:
            key = os.getenv("BV_ENCRYPTION_KEY")
            if key is None:
                key = CryptoUtils.generate_key(32)
                os.environ["BV_ENCRYPTION_KEY"] = key
        if isinstance(key, str):
            key = key.encode()
        if len(key) != 44:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"blackveil-v5-salt",
                iterations=100_000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(key))
        return Fernet(key)

    @staticmethod
    def encrypt(plaintext: str, key: Optional[str] = None) -> str:
        """Encrypt a string"""
        f = CryptoUtils.get_fernet(key)
        return f.encrypt(plaintext.encode()).decode()

    @staticmethod
    def decrypt(ciphertext: str, key: Optional[str] = None) -> str:
        """Decrypt a string"""
        f = CryptoUtils.get_fernet(key)
        return f.decrypt(ciphertext.encode()).decode()

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_hex(length)

    @staticmethod
    def hash_hmac(data: str, secret: Optional[str] = None) -> str:
        """Create HMAC-SHA256 hash of data"""
        if secret is None:
            secret = os.getenv("BV_HMAC_SECRET", "blackveil-default-secret")
        return hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def generate_api_key(prefix: str = "bv") -> str:
        """Generate a formatted API key"""
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_sk_{random_part}"

    @staticmethod
    def secure_compare(a: str, b: str) -> bool:
        """Constant-time string comparison"""
        return hmac.compare_digest(a, b)

    @staticmethod
    def mask_sensitive(value: str, visible_chars: int = 4) -> str:
        """Mask a sensitive string, showing only last N chars"""
        if len(value) <= visible_chars:
            return "*" * len(value)
        return "*" * (len(value) - visible_chars) + value[-visible_chars:]
