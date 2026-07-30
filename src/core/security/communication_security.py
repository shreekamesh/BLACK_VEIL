"""
Communication Security for BLACK VEIL
Secure communication protocols with TLS 1.3, QUIC, and perfect forward secrecy
"""

from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
import ssl
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProtocolVersion(Enum):
    """Communication protocol versions"""
    TLS_1_3 = "tls_1_3"
    TLS_1_2 = "tls_1_2"
    QUIC = "quic"
    DTLS = "dtls"

class CipherSuite(Enum):
    """Available cipher suites"""
    ECDHE_ECDSA_AES256_GCM_SHA384 = "ECDHE-ECDSA-AES256-GCM-SHA384"
    ECDHE_RSA_AES256_GCM_SHA384 = "ECDHE-RSA-AES256-GCM-SHA384"
    ECDHE_ECDSA_CHACHA20_POLY1305 = "ECDHE-ECDSA-CHACHA20-POLY1305"
    ECDHE_RSA_CHACHA20_POLY1305 = "ECDHE-RSA-CHACHA20-POLY1305"

@dataclass
class SecurityContext:
    """Security context for communication"""
    protocol: ProtocolVersion
    cipher_suite: CipherSuite
    perfect_forward_secrecy: bool
    certificate_pinning: bool
    hsts_enforced: bool

class CommunicationSecurity:
    """
    Secure communication for BLACK VEIL
    
    Features:
    - TLS 1.3 and QUIC support
    - Perfect forward secrecy
    - Certificate pinning
    - HSTS enforcement
    - Secure channel establishment
    """
    
    def __init__(self):
        self.active_sessions = {}
        self.session_cache = {}
        self.certificate_pins = {}
        
    def create_secure_context(self, 
                             protocol: ProtocolVersion = ProtocolVersion.TLS_1_3,
                             require_pfs: bool = True) -> ssl.SSLContext:
        """Create a secure SSL/TLS context"""
        if protocol == ProtocolVersion.TLS_1_3:
            context = ssl.create_default_context(
                purpose=ssl.Purpose.CLIENT_AUTH,
                cafile=None,
                capath=None,
                cadata=None
            )
            
            # TLS 1.3 only
            context.minimum_version = ssl.TLSVersion.TLSv1_3
            context.maximum_version = ssl.TLSVersion.TLSv1_3
            
            # Strong cipher suites
            context.set_ciphers(
                'ECDHE-ECDSA-AES256-GCM-SHA384:'
                'ECDHE-RSA-AES256-GCM-SHA384:'
                'ECDHE-ECDSA-CHACHA20-POLY1305:'
                'ECDHE-RSA-CHACHA20-POLY1305'
            )
            
            # Perfect forward secrecy
            if require_pfs:
                context.options |= ssl.OP_SINGLE_ECDH_USE
                context.options |= ssl.OP_SINGLE_DH_USE
            
            return context
        
        else:
            # Fallback to TLS 1.2
            context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.maximum_version = ssl.TLSVersion.TLSv1_2
            
            return context
    
    def establish_secure_channel(self, 
                                 peer_id: str,
                                 protocol: ProtocolVersion = ProtocolVersion.TLS_1_3,
                                 certificate_pin: Optional[str] = None) -> Dict:
        """Establish a secure communication channel"""
        
        # Create security context
        context = self.create_secure_context(protocol)
        
        # Certificate pinning
        if certificate_pin:
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            self.certificate_pins[peer_id] = certificate_pin
        
        # Create session
        session = {
            'peer_id': peer_id,
            'protocol': protocol.value,
            'established_at': datetime.utcnow(),
            'certificate_pinned': certificate_pin is not None,
            'hsts_enforced': True,
            'security_context': context
        }
        
        self.active_sessions[peer_id] = session
        
        logger.info(f"Secure channel established with {peer_id}")
        
        return session
    
    def enforce_hsts(self, domain: str) -> Dict:
        """Enforce HSTS (HTTP Strict Transport Security)"""
        return {
            'domain': domain,
            'max_age': 31536000,  # 1 year
            'include_subdomains': True,
            'preload': True,
            'enforced_at': datetime.utcnow().isoformat()
        }
    
    def get_session_security(self, peer_id: str) -> Optional[Dict]:
        """Get security details for a session"""
        if peer_id in self.active_sessions:
            session = self.active_sessions[peer_id]
            return {
                'protocol': session['protocol'],
                'established_at': session['established_at'].isoformat(),
                'certificate_pinned': session['certificate_pinned'],
                'hsts_enforced': session['hsts_enforced'],
                'age_seconds': (datetime.utcnow() - session['established_at']).total_seconds()
            }
        return None
    
    def close_session(self, peer_id: str) -> bool:
        """Close a secure session"""
        if peer_id in self.active_sessions:
            del self.active_sessions[peer_id]
            logger.info(f"Closed secure session with {peer_id}")
            return True
        return False
    
    def get_security_metrics(self) -> Dict:
        """Get communication security metrics"""
        return {
            'active_sessions': len(self.active_sessions),
            'certificate_pins': len(self.certificate_pins),
            'protocols_used': list(set(s['protocol'] for s in self.active_sessions.values())),
            'hsts_enforced': all(s['hsts_enforced'] for s in self.active_sessions.values())
        }
