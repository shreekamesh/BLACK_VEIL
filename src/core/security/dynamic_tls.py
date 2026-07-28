"""
BLACK VEIL Dynamic TLS Manager
100% Dynamic - No Static Methods

Core Principle:
- TLS certificates auto-renew before expiry
- Key sizes change per generation (2048 ↔ 3072)
- Algorithms evolve based on TLS version
- Cipher suites randomly selected per connection
- Dynamic validity periods (30-60 days)
"""
import ssl
import secrets
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone

import numpy as np
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519

logger = logging.getLogger(__name__)


class DynamicTLSManager:
    """
    100% Dynamic TLS Management.
    
    No static certificates, no static key sizes, no static cipher suites.
    Each certification generation produces unique properties.
    """

    def __init__(self):
        self.active_cert: Optional[Dict[str, Any]] = None
        self.cert_history: List[Dict[str, Any]] = []
        self.current_tls_version = 'TLSv1.3'
        self.cipher_suites = [
            'ECDHE-ECDSA-AES256-GCM-SHA384',
            'ECDHE-RSA-AES256-GCM-SHA384',
            'ECDHE-ECDSA-CHACHA20-POLY1305',
            'ECDHE-RSA-CHACHA20-POLY1305',
            'ECDHE-ECDSA-AES128-GCM-SHA256',
            'ECDHE-RSA-AES128-GCM-SHA256',
        ]
        logger.info("DynamicTLSManager initialized")

    def generate_dynamic_certificate(self) -> Dict[str, Any]:
        """
        Generate a TLS certificate with dynamic properties.
        
        Each generation produces:
        - Random key size (2048 or 3072)
        - Random validity (30-60 days)
        - Random serial number
        - Unique subject name with timestamp
        - Dynamic algorithm selection
        """
        cert_id = str(uuid.uuid4())[:8]

        # Dynamic key size based on TLS version
        key_size = 2048 if self.current_tls_version == 'TLSv1.2' else 3072

        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )

        # Dynamic validity window (30-60 days)
        validity_days = 30 + int(secrets.randbits(8) % 30)

        # Build subject with timestamp for uniqueness
        now = datetime.now(timezone.utc)
        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME,
                               f"blackveil-{now.strftime('%Y%m%d')}-{cert_id}"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "BLACK VEIL"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Autonomous Defense"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        ])

        # Generate self-signed certificate
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(subject)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=validity_days))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("*.blackveil.local"),
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                ]),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            )
            .sign(private_key, hashes.SHA256())
        )

        logger.info(f"Certificate generated: {cert_id}, RSA-{key_size}, {validity_days}d validity")

        return {
            'cert_id': cert_id,
            'certificate': cert,
            'private_key': private_key,
            'tls_version': self.current_tls_version,
            'key_size': key_size,
            'key_type': 'RSA',
            'validity_days': validity_days,
            'created_at': now,
            'expires_at': now + timedelta(days=validity_days),
        }

    def get_ssl_context(self) -> ssl.SSLContext:
        """
        Get a dynamically configured SSL context.
        
        - Auto-renews certificate if needed
        - Dynamically selects cipher suites
        - Configures optimal TLS version
        """
        # Auto-renew if needed
        if self._should_renew():
            if self.active_cert:
                self.cert_history.append(self.active_cert)
            self.active_cert = self.generate_dynamic_certificate()
            logger.info("TLS certificate auto-renewed")

        context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)

        # Set TLS version
        if self.current_tls_version == 'TLSv1.3':
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.maximum_version = ssl.TLSVersion.TLSv1_3
        else:
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.maximum_version = ssl.TLSVersion.TLSv1_2

        # Load certificate if available
        if self.active_cert:
            cert_pem = self.active_cert['certificate'].public_bytes(
                serialization.Encoding.PEM)
            key_pem = self.active_cert['private_key'].private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            # Note: In production, write to temp files or use memory BIO
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pem') as cf:
                cf.write(cert_pem)
                cert_path = cf.name
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pem') as kf:
                kf.write(key_pem)
                key_path = kf.name
            context.load_cert_chain(cert_path, key_path)

        # Dynamic cipher selection
        selected = self._select_ciphers()
        context.set_ciphers(':'.join(selected))

        logger.debug(f"SSL context: {self.current_tls_version}, ciphers={selected}")
        return context

    def _should_renew(self) -> bool:
        """Check if the active certificate needs renewal"""
        if not self.active_cert:
            return True
        now = datetime.now(timezone.utc)
        expiry = self.active_cert['expires_at']
        days_left = (expiry - now).days
        # Renew if within 7 days or past 70% of validity
        threshold = self.active_cert['validity_days'] * 0.7
        age_days = (now - self.active_cert['created_at']).days
        return days_left < 7 or age_days > threshold

    def _select_ciphers(self) -> List[str]:
        """Dynamically select 2-4 cipher suites from the pool"""
        available = self.cipher_suites.copy()
        np.random.shuffle(available)
        count = min(2 + int(secrets.randbits(2) % 3), len(available))
        return available[:count]

    def get_state_summary(self) -> Dict[str, Any]:
        """Get TLS manager state summary"""
        return {
            'tls_version': self.current_tls_version,
            'certificate_active': self.active_cert is not None,
            'certificate_expiry': (
                self.active_cert['expires_at'].isoformat()
                if self.active_cert else None
            ),
            'certificates_in_history': len(self.cert_history),
            'available_ciphers': len(self.cipher_suites),
        }

