"""
BLACK VEIL V2 — API Key Management
API key generation, hashing, storage, and verification
"""
import hashlib
import hmac
import os
import secrets
import string
import time
from collections import defaultdict
from typing import Optional

from fastapi import HTTPException, status


def generate_api_key(prefix: str = "bv") -> tuple[str, str]:
    """
    Generate a new API key and its hash.

    Returns:
        tuple: (raw_api_key, hashed_key)
        The raw key should be shown once to the user, then discarded.
    """
    alphabet = string.ascii_letters + string.digits
    raw_key = "".join(secrets.choice(alphabet) for _ in range(48))
    api_key = f"{prefix}_sk_{raw_key}"
    hashed = hash_api_key(api_key)
    return api_key, hashed


def hash_api_key(api_key: str) -> str:
    """Hash an API key using HMAC-SHA256 with a server-side secret."""
    server_secret = os.getenv("BV_API_KEY_SECRET", "change-me-in-production").encode()
    key_hash = hmac.new(
        server_secret,
        api_key.encode(),
        hashlib.sha256,
    ).hexdigest()
    return key_hash


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    """Verify a raw API key against its stored hash"""
    computed_hash = hash_api_key(raw_key)
    return hmac.compare_digest(computed_hash, stored_hash)


class APIKeyManager:
    """Manages API key lifecycle including rate limiting and revocation."""

    def __init__(self):
        self._rate_limits: dict[str, list[float]] = defaultdict(list)
        self._rate_limit_config: dict[str, tuple[int, int]] = defaultdict(
            lambda: (100, 60)
        )

    def set_rate_limit(self, key_hash: str, max_requests: int, window_seconds: int):
        """Configure rate limit for a specific key"""
        self._rate_limit_config[key_hash] = (max_requests, window_seconds)

    def check_rate_limit(self, key_hash: str) -> bool:
        """Check if the API key has exceeded its rate limit."""
        max_reqs, window = self._rate_limit_config[key_hash]
        now = time.time()
        self._rate_limits[key_hash] = [
            t for t in self._rate_limits[key_hash] if now - t < window
        ]
        if len(self._rate_limits[key_hash]) >= max_reqs:
            return False
        self._rate_limits[key_hash].append(now)
        return True

    def validate_and_check(self, raw_key: str, stored_hash: str) -> dict:
        """Validate API key and check rate limit."""
        if not verify_api_key(raw_key, stored_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        if not self.check_rate_limit(stored_hash):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
            )
        return {"valid": True, "key_hash": stored_hash}


api_key_manager = APIKeyManager()
