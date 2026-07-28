"""
BLACK VEIL V5 - Input Validation Utilities
Sanitization and validation functions for security
"""
import ipaddress
import re
from typing import Any, Dict, List, Optional, Union


class Validators:
    """Input validation and sanitization utilities"""

    # Common patterns
    IP_PATTERN = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    UUID_PATTERN = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$", re.IGNORECASE)
    DOMAIN_PATTERN = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    )

    # Sensitive field names to watch for
    SENSITIVE_FIELDS = {
        "password", "password_hash", "secret", "token", "api_key",
        "api_secret", "access_key", "private_key", "auth_token",
        "session_id", "credit_card", "ssn", "passphrase",
    }

    # Dangerous patterns to detect in input
    DANGEROUS_PATTERNS = [
        re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"onclick|onload|onerror|onmouseover", re.IGNORECASE),
        re.compile(r"[\"';\-\-]"),
    ]

    @staticmethod
    def validate_ip(address: str) -> bool:
        """Validate IPv4 or IPv6 address"""
        try:
            ipaddress.ip_address(address)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        return bool(Validators.EMAIL_PATTERN.match(email))

    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """Validate UUID format"""
        return bool(Validators.UUID_PATTERN.match(uuid_str))

    @staticmethod
    def validate_domain(domain: str) -> bool:
        """Validate domain name"""
        return bool(Validators.DOMAIN_PATTERN.match(domain))

    @staticmethod
    def validate_port(port: int) -> bool:
        """Validate port number"""
        return 0 <= port <= 65535

    @staticmethod
    def validate_trust_score(score: float) -> bool:
        """Validate trust score range (0-100)"""
        return 0.0 <= score <= 100.0

    @staticmethod
    def validate_confidence(confidence: float) -> bool:
        """Validate confidence value (0-1)"""
        return 0.0 <= confidence <= 1.0

    @staticmethod
    def validate_probability(prob: float) -> bool:
        """Validate probability value (0-1)"""
        return 0.0 <= prob <= 1.0

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize a string by removing dangerous patterns and truncating"""
        if not isinstance(value, str):
            value = str(value)
        # Truncate
        value = value[:max_length]
        # Remove control characters
        value = "".join(char for char in value if ord(char) >= 32 or char in "\n\r\t")
        return value.strip()

    @staticmethod
    def sanitize_dict(data: Dict[str, Any], max_depth: int = 5) -> Dict[str, Any]:
        """Recursively sanitize dictionary values"""
        if max_depth <= 0:
            return {}

        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            safe_key = Validators.sanitize_string(str(key), max_length=128)

            if isinstance(value, str):
                sanitized[safe_key] = Validators.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[safe_key] = Validators.sanitize_dict(value, max_depth - 1)
            elif isinstance(value, list):
                sanitized[safe_key] = [
                    Validators.sanitize_string(str(item)) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[safe_key] = value

        return sanitized

    @staticmethod
    def detect_sensitive_data(data: Dict[str, Any]) -> List[str]:
        """Detect if data contains sensitive fields"""
        detected = []
        for key in data:
            key_lower = key.lower()
            for sensitive in Validators.SENSITIVE_FIELDS:
                if sensitive in key_lower:
                    detected.append(key)
                    break
        return detected

    @staticmethod
    def contains_malicious_content(text: str) -> bool:
        """Check if text contains XSS or injection patterns"""
        for pattern in Validators.DANGEROUS_PATTERNS:
            if pattern.search(text):
                return True
        return False

    @staticmethod
    def validate_json_safe(data: Any) -> bool:
        """Validate that data is JSON-safe (no circular refs, safe types)"""
        try:
            import json
            json.dumps(data)
            return True
        except (TypeError, ValueError, OverflowError):
            return False
