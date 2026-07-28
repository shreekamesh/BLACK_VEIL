"""
BLACK VEIL V2 — Security Package
Authentication, authorization, encryption, and security utilities
"""
from security.auth import (
    create_access_token,
    verify_token,
    get_current_user,
    hash_password,
    verify_password,
)
from security.api_key import (
    generate_api_key,
    hash_api_key,
    verify_api_key,
    APIKeyManager,
)
from security.rbac import (
    RBACManager,
    Permission,
    Role,
    require_permission,
    require_role,
)
from security.encryption import (
    encrypt_sensitive_data,
    decrypt_sensitive_data,
    EncryptionManager,
)

__all__ = [
    "create_access_token",
    "verify_token",
    "get_current_user",
    "hash_password",
    "verify_password",
    "generate_api_key",
    "hash_api_key",
    "verify_api_key",
    "APIKeyManager",
    "RBACManager",
    "Permission",
    "Role",
    "require_permission",
    "require_role",
    "encrypt_sensitive_data",
    "decrypt_sensitive_data",
    "EncryptionManager",
]
