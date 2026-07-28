# BLACK VEIL V2 — Security Design

## Comprehensive Security Architecture for Research Framework

---

## 1. Security Layers Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: NETWORK SECURITY                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  TLS 1.3     │  │  WAF         │  │  Rate        │  │  DDoS      │ │
│  │  (End-to-End)│  │  (ModSecurity)│  │  Limiting    │  │  Protection│ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                    LAYER 2: AUTHENTICATION                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  JWT Tokens  │  │  API Keys    │  │  RBAC        │  │  MFA       │ │
│  │  (RS256)     │  │  (HMAC)      │  │  (Role-Based)│  │  (TOTP)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                    LAYER 3: APPLICATION SECURITY                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Input       │  │  SQL         │  │  XSS         │  │  CSRF      │ │
│  │  Validation  │  │  Injection   │  │  Protection  │  │  Tokens    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                    LAYER 4: DATA SECURITY                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Encryption  │  │  Data        │  │  Audit       │  │  Backup    │ │
│  │  (AES-256)   │  │  Masking     │  │  Trail       │  │  & DR      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                    LAYER 5: MODEL SECURITY                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Model       │  │  Adversarial │  │  Model       │  │  Secure    │ │
│  │  Watermarking│  │  Robustness  │  │  Versioning  │  │  Serving   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                    LAYER 6: OPERATIONAL SECURITY                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Secrets     │  │  Container   │  │  Vulnerability│  │  Incident  │ │
│  │  Management  │  │  Security    │  │  Scanning    │  │  Response  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication & Authorization

### 2.1 API Authentication
```python
# JWT Token Generation
def create_access_token(user_id: str, role: str, permissions: list):
    payload = {
        "sub": user_id,
        "role": role,
        "permissions": permissions,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
        "jti": str(uuid.uuid4())  # JWT ID for revocation
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="RS256")

# API Key Hashing
def hash_api_key(api_key: str):
    salt = os.urandom(32)
    key_hash = hashlib.blake2b(api_key.encode(), salt=salt).hexdigest()
    return f"{salt.hex()}${key_hash}"
```

### 2.2 RBAC Matrix

| Role | Resources | Actions | Rate Limit |
|------|-----------|---------|------------|
| **admin** | All | CRUD | 1000/min |
| **operator** | Trust, Deception, Response, Agents | Read, Execute | 200/min |
| **analyst** | Trust, Threat, Reports | Read, Export | 100/min |
| **agent** | Own data | Write only | 500/min |
| **viewer** | Dashboard, Reports | Read only | 50/min |

### 2.3 Permission Enforcement
```python
from functools import wraps

def require_permission(*required_permissions):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_permissions = get_current_user_permissions()
            for perm in required_permissions:
                if perm not in user_permissions:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Missing permission: {perm}"
                    )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@router.post("/api/v1/deception/deploy")
@require_permission("write:deception")
async def deploy_deception(request: DeceptionRequest):
    ...
```

---

## 3. Data Encryption

### 3.1 Encryption at Rest
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashing, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate master encryption key
master_key = Fernet.generate_key()
cipher = Fernet(master_key)

# Encrypt sensitive data before storing
def encrypt_sensitive_data(data: dict) -> dict:
    encrypted = {}
    for key, value in data.items():
        if key in SENSITIVE_FIELDS:
            encrypted[key] = cipher.encrypt(json.dumps(value).encode())
        else:
            encrypted[key] = value
    return encrypted

# Decrypt on read
def decrypt_sensitive_data(data: dict) -> dict:
    decrypted = {}
    for key, value in data.items():
        if key in SENSITIVE_FIELDS:
            decrypted[key] = json.loads(cipher.decrypt(value))
        else:
            decrypted[key] = value
    return decrypted
```

### 3.2 Encryption in Transit
```nginx
# Nginx TLS Configuration
server {
    listen 443 ssl http2;
    ssl_protocols TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_certificate /etc/ssl/certs/blackveil.crt;
    ssl_certificate_key /etc/ssl/private/blackveil.key;
}
```

### 3.3 Database Encryption
```sql
-- PostgreSQL TDE (Transparent Data Encryption)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive columns
CREATE TABLE fake_credentials (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password_encrypted BYTEA NOT NULL, -- pgp_sym_encrypt()
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Encrypt at application layer for maximum security
-- Use column-level encryption for PII
```

---

## 4. Input Validation & Sanitization

### 4.1 Request Validation
```python
from pydantic import BaseModel, Field, validator
import ipaddress

class PredictRequest(BaseModel):
    features: Dict[str, float]
    context: Dict[str, Any]
    
    @validator('features')
    def validate_features(cls, v):
        if len(v) == 0:
            raise ValueError('Features cannot be empty')
        if any(not isinstance(val, (int, float)) for val in v.values()):
            raise ValueError('Feature values must be numeric')
        if any(val < -1e10 or val > 1e10 for val in v.values()):
            raise ValueError('Feature values out of range')
        return v
    
    @validator('context')
    def validate_context(cls, v):
        if 'source_ip' in v:
            try:
                ipaddress.ip_address(v['source_ip'])
            except ValueError:
                raise ValueError('Invalid IP address')
        return v
```

### 4.2 SQL Injection Prevention
```python
# Always use parameterized queries
async def get_agent_trust(agent_id: str):
    query = """
        SELECT trust_score, risk_score, threat_level
        FROM trust_scores
        WHERE agent_id = $1
        ORDER BY timestamp DESC
        LIMIT 1
    """
    return await db.fetchrow(query, agent_id)

# Never use f-strings for SQL
# Never concatenate user input into queries
```

### 4.3 XSS Prevention
```typescript
// React automatically escapes JSX
// Additional sanitization for dangerous content
import DOMPurify from 'dompurify';

function ThreatDescription({ html }: { html: string }) {
  const sanitized = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

---

## 5. Model Security

### 5.1 Model Protection
```python
# Model watermarking for intellectual property protection
def watermark_model(model, watermark_data: bytes):
    """Embed watermark in model weights using spread-spectrum"""
    weights = model.get_weights()
    watermarked_weights = []
    
    for layer_idx, layer_weights in enumerate(weights):
        flat_weights = layer_weights.flatten()
        
        # Spread watermark across weights
        for i, bit in enumerate(watermark_data):
            idx = (layer_idx * 1000 + i * 10) % len(flat_weights)
            flat_weights[idx] += (bit - 0.5) * 0.001
        
        watermarked_weights.append(flat_weights.reshape(layer_weights.shape))
    
    model.set_weights(watermarked_weights)

# Verify watermark
def verify_watermark(model, original_watermark: bytes):
    extracted = []
    weights = model.get_weights()
    
    for layer_idx, layer_weights in enumerate(weights):
        flat_weights = layer_weights.flatten()
        
        for i in range(len(original_watermark)):
            idx = (layer_idx * 1000 + i * 10) % len(flat_weights)
            bit = 1 if flat_weights[idx] > 0 else 0
            extracted.append(bit)
    
    return extracted == list(original_watermark)
```

### 5.2 Adversarial Robustness
```python
# Input sanitization against adversarial examples
def sanitize_input(features: np.ndarray, epsilon: float = 0.01):
    """Apply feature squeezing to defend against adversarial attacks"""
    # Median smoothing
    smoothed = scipy.ndimage.median_filter(features, size=3)
    
    # Clipping to valid range
    clipped = np.clip(smoothed, 0, 1)
    
    # Rounding to reduce precision (defeat gradient-based attacks)
    rounded = np.round(clipped / epsilon) * epsilon
    
    return rounded
```

### 5.3 Secure Model Serving
```python
# Model loading sandbox
import pickle
import tempfile
import subprocess

def load_model_secure(model_path: str):
    """Load pickle model in isolated process"""
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
        f.write(b"""
import pickle
import sys
import json

with open(sys.argv[1], 'rb') as mf:
    model = pickle.load(mf)

# Extract safe metadata only
safe_info = {
    'classes': model.classes_.tolist(),
    'n_features': model.n_features_in_,
    'feature_importances': model.feature_importances_.tolist()
}
print(json.dumps(safe_info))
""")
    
    result = subprocess.run(
        ['python3', f.name, model_path],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    return json.loads(result.stdout)
```

---

## 6. Secrets Management

### 6.1 Environment Configuration
```bash
# .env.production (never committed to git)
BLACKVEIL_SECRET_KEY=rsa_private_key_here
BLACKVEIL_JWT_SECRET=hmac_secret_here
BLACKVEIL_DB_PASSWORD=strong_password_here
BLACKVEIL_REDIS_PASSWORD=redis_password_here
BLACKVEIL_ENCRYPTION_KEY=fernet_key_here
BLACKVEIL_SENTRY_DSN=https://xxx@sentry.io/xxx
BLACKVEIL_SLACK_WEBHOOK=https://hooks.slack.com/xxx
```

### 6.2 Vault Integration
```python
import hvac

class VaultClient:
    def __init__(self, vault_addr: str, vault_token: str):
        self.client = hvac.Client(url=vault_addr, token=vault_token)
    
    def get_secret(self, path: str, key: str) -> str:
        secret = self.client.secrets.kv.v2.read_secret(path)
        return secret['data']['data'][key]
    
    def rotate_secret(self, path: str, key: str, new_value: str):
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret={key: new_value}
        )

# Usage
vault = VaultClient(os.getenv('VAULT_ADDR'), os.getenv('VAULT_TOKEN'))
db_password = vault.get_secret('blackveil/database', 'password')
```

---

## 7. Audit Logging

### 7.1 Audit Trail Structure
```json
{
  "audit_id": "aud_001",
  "timestamp": "2024-01-01T00:00:00Z",
  "actor": {
    "type": "user | agent | system",
    "id": "user_001",
    "ip": "192.168.1.100",
    "role": "operator"
  },
  "action": "deploy_deception",
  "resource": {
    "type": "honeypot",
    "id": "dec_001",
    "endpoint": "192.168.1.200:2222"
  },
  "changes": {
    "before": null,
    "after": { "status": "active", "service": "ssh" }
  },
  "result": "success",
  "signature": "hmac_sha256_signature_for_integrity"
}
```

### 7.2 Log Integrity
```python
import hmac
import hashlib

def sign_audit_log(entry: dict, secret_key: str) -> str:
    """Create HMAC signature for audit log integrity"""
    message = json.dumps(entry, sort_keys=True).encode()
    signature = hmac.new(
        secret_key.encode(),
        message,
        hashlib.sha256
    ).hexdigest()
    return signature

def verify_audit_log(entry: dict, signature: str, secret_key: str) -> bool:
    """Verify audit log hasn't been tampered with"""
    expected = sign_audit_log(entry, secret_key)
    return hmac.compare_digest(signature, expected)
```

### 7.3 Chain of Custody
```python
CHAIN_FILE = "logs/audit_chain.json"

def append_to_chain(entry: dict):
    """Maintain blockchain-like chain of custody"""
    chain = []
    if os.path.exists(CHAIN_FILE):
        with open(CHAIN_FILE, 'r') as f:
            chain = json.load(f)
    
    # Previous hash
    prev_hash = chain[-1]['hash'] if chain else "0" * 64
    
    # Current entry with hash
    entry['prev_hash'] = prev_hash
    entry['timestamp'] = datetime.utcnow().isoformat()
    entry['hash'] = hashlib.sha256(
        json.dumps(entry, sort_keys=True).encode()
    ).hexdigest()
    
    chain.append(entry)
    
    with open(CHAIN_FILE, 'w') as f:
        json.dump(chain, f, indent=2)
```

---

## 8. Rate Limiting & DDoS Protection

### 8.1 Rate Limiting Configuration
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("100/minute")
async def predict_endpoint(request: Request):
    ...

# Global rate limits
GLOBAL_LIMITS = {
    "/api/v1/predict": "100/minute",
    "/api/v1/trust": "200/minute", 
    "/api/v1/deception": "50/minute",
    "/api/v1/response": "30/minute",
    "/api/v1/dashboard": "60/minute",
}
```

### 8.2 IP Blacklisting
```python
from collections import defaultdict
import time

class IPThreatIntelligence:
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.blacklist = set()
        self.BLACKLIST_THRESHOLD = 10
        self.WINDOW_SECONDS = 300
    
    def record_attempt(self, ip: str, success: bool):
        if not success:
            self.failed_attempts[ip].append(time.time())
            self._check_blacklist(ip)
    
    def _check_blacklist(self, ip: str):
        window_start = time.time() - self.WINDOW_SECONDS
        recent_failures = [
            t for t in self.failed_attempts[ip]
            if t > window_start
        ]
        if len(recent_failures) >= self.BLACKLIST_THRESHOLD:
            self.blacklist.add(ip)
    
    def is_blocked(self, ip: str) -> bool:
        return ip in self.blacklist
```

---

## 9. Container Security

### 9.1 Dockerfile Security
```dockerfile
FROM python:3.11-slim AS base

# Security updates
RUN apt-get update && apt-get install -y --no-install-recommends \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd -m -u 1000 blackveil
USER blackveil

# Read-only filesystem
RUN chmod -R 555 /app

# No shell access
RUN echo "blackveil:x:1000:1000::/home/blackveil:/sbin/nologin" >> /etc/passwd

# Security headers
ENV PYTHONWARNINGS=error
ENV PYTHONDONTWRITEBYTECODE=1
```

### 9.2 Docker Compose Security
```yaml
version: '3.8'

services:
  api:
    security_opt:
      - no-new-privileges:true
    read_only: true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    environment:
      - BLACKVEIL_ENV=production
    secrets:
      - db_password
      - jwt_secret

secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

---

## 10. Security Monitoring

### 10.1 Security Events Monitoring
```python
# Monitor for security events
SECURITY_EVENTS = {
    "BRUTE_FORCE": "Multiple failed auth attempts from {ip}",
    "SQL_INJECTION": "SQL injection pattern detected in request",
    "XSS_ATTEMPT": "XSS payload detected in {field}",
    "UNAUTHORIZED_ACCESS": "Access denied for {user} to {resource}",
    "MODEL_TAMPERING": "Model hash mismatch detected for {model_id}",
    "DATA_EXFILTRATION": "Unusual data transfer detected: {bytes} bytes",
}
```

### 10.2 Alert Thresholds
```yaml
alerts:
  auth_failures:
    threshold: 5
    window: 5_minutes
    action: rate_limit
    
  trust_drop:
    threshold: 20_percent
    window: 1_hour
    action: investigate_agent
    
  model_drift:
    threshold: 3_standard_deviations
    window: 24_hours
    action: retrain_model
    
  anomaly_score:
    threshold: 0.95
    action: isolate_system
```

---

## 11. Compliance & Standards

| Standard | Requirement | Implementation |
|----------|-------------|----------------|
| OWASP Top 10 | Input validation, XSS, CSRF | Pydantic, DOMPurify, CSRF tokens |
| NIST 800-53 | Access control, audit | RBAC, HMAC audit logs |
| ISO 27001 | Information security | Encryption, access control |
| GDPR | Data protection, privacy | Data masking, encryption |
| HIPAA | Healthcare data (if used) | PHI encryption, audit trails |
| SOC2 | Security, availability | Monitoring, DR plan |

---

## 12. Incident Response Plan

### 12.1 Response Levels
| Level | Severity | Response Time | Example |
|-------|----------|---------------|---------|
| L1 | LOW | < 1 hour | Minor anomaly, single alert |
| L2 | MEDIUM | < 30 min | Multiple alerts, potential intrusion |
| L3 | HIGH | < 15 min | Confirmed breach, data exposure |
| L4 | CRITICAL | < 5 min | Active attack, system compromise |

### 12.2 Incident Response Playbook
```python
class IncidentResponder:
    def __init__(self):
        self.response_playbook = {
            "DATA_BREACH": [
                "isolate_affected_systems",
                "rotate_all_credentials",
                "notify_security_team",
                "collect_forensic_evidence",
                "notify_affected_parties",
                "begin_recovery_process"
            ],
            "RANSOMWARE": [
                "isolate_infected_systems",
                "block_ransomware_c2_ips",
                "restore_from_backup",
                "analyze_entry_vector",
                "update_detection_rules"
            ],
            "INSIDER_THREAT": [
                "suspend_user_account",
                "revoke_access_tokens",
                "preserve_evidence",
                "investigate_user_activity",
                "legal_notification"
            ]
        }
    
    async def execute_playbook(self, incident_type: str):
        steps = self.response_playbook.get(incident_type, [])
        for step in steps:
            await self.execute_step(step)
            self.log_step_completion(step)
```

