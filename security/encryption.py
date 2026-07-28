"""
BLACK VEIL V2 — Encryption Utilities
AES-256 encryption for sensitive data at rest
"""
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


SENSITIVE_FIELDS = {
    "password", "password_hash", "api_key", "secret",
    "token", "private_key", "credential", "passphrase",
}


def _get_fernet() -> Fernet:
    """Get or create a Fernet cipher instance from master encryption key."""
    master_key = os.getenv("BV_ENCRYPTION_KEY")
    if master_key is None:
        master_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        os.environ["BV_ENCRYPTION_KEY"] = master_key

    if isinstance(master_key, str):
        master_key = master_key.encode()

    if len(master_key) != 44:  # Fernet keys are 44 base64 chars
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"blackveil-salt",
            iterations=100_000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(master_key))
        return Fernet(derived_key)

    return Fernet(master_key)


class EncryptionManager:
    """Manages encryption and decryption of sensitive data using Fernet."""

    def __init__(self):
        self._cipher = _get_fernet()

    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64-encoded ciphertext"""
        return self._cipher.encrypt(data.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext back to plaintext"""
        return self._cipher.decrypt(ciphertext.encode()).decode()

    def encrypt_dict(self, data: dict, sensitive_fields: Optional[set[str]] = None) -> dict:
        """Encrypt sensitive fields in a dictionary."""
        fields_to_encrypt = sensitive_fields or SENSITIVE_FIELDS
        encrypted = {}
        for key, value in data.items():
            if key.lower() in fields_to_encrypt and isinstance(value, str):
                encrypted[key] = self.encrypt(value)
            elif isinstance(value, dict):
                encrypted[key] = self.encrypt_dict(value, fields_to_encrypt)
            else:
                encrypted[key] = value
        return encrypted

    def decrypt_dict(self, data: dict, sensitive_fields: Optional[set[str]] = None) -> dict:
        """Decrypt sensitive fields in a dictionary."""
        fields_to_decrypt = sensitive_fields or SENSITIVE_FIELDS
        decrypted = {}
        for key, value in data.items():
            if key.lower() in fields_to_decrypt and isinstance(value, str):
                try:
                    decrypted[key] = self.decrypt(value)
                except Exception:
                    decrypted[key] = value
            elif isinstance(value, dict):
                decrypted[key] = self.decrypt_dict(value, fields_to_decrypt)
            else:
                decrypted[key] = value
        return decrypted


def encrypt_sensitive_data(data: dict) -> dict:
    """Convenience function: encrypt sensitive fields in a dict"""
    return EncryptionManager().encrypt_dict(data)


def decrypt_sensitive_data(data: dict) -> dict:
    """Convenience function: decrypt sensitive fields in a dict"""
    return EncryptionManager().decrypt_dict(data)


encryption_manager = EncryptionManager()
