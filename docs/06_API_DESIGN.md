# BLACK VEIL V2 — API Design

## FastAPI-based RESTful API Architecture

---

## 1. API Overview

| Base URL | Version | Protocol | Auth |
|----------|---------|----------|------|
| `/api/v1` | v1 | HTTPS | JWT + API Key |

---

## 2. Authentication & Authorization

### 2.1 API Key Authentication
```
POST /api/v1/auth/api-key

Request:
{
  "api_key": "bv_sk_xxxxxxxxxxxxxxxx"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "permissions": ["read:trust", "write:deception", "admin:agents"]
}
```

### 2.2 JWT Token Structure
```
Header:  { "alg": "HS256", "typ": "JWT" }
Payload: {
  "sub": "agent_001",
  "role": "admin",
  "permissions": ["read:*", "write:*"],
  "iat": 1700000000,
  "exp": 1700003600
}
```

### 2.3 RBAC Roles
| Role | Permissions |
|------|-------------|
| `admin` | Full access to all endpoints |
| `operator` | Read trust, execute responses |
| `analyst` | Read all, write reports |
| `agent` | Write own metrics, read own config |

---

## 3. API Endpoints

### 3.1 AI Inference Endpoints

#### Predict from all domains
```
POST /api/v1/predict
Content-Type: application/json
Authorization: Bearer <token>

Request:
{
  "data": {
    "network": { ... features ... },
    "iot": { ... features ... },
    "user": { ... features ... },
    "cicids": { ... features ... }
  },
  "context": {
    "timestamp": "2024-01-01T00:00:00Z",
    "source_ip": "192.168.1.100",
    "target": "web_server_01"
  }
}

Response:
{
  "status": "success",
  "predictions": {
    "network": { "label": 0, "probability": 0.98, "confidence": 0.95 },
    "iot": { "label": 0, "probability": 0.99, "confidence": 0.97 },
    "user": { "label": 0, "probability": 0.87, "confidence": 0.82 },
    "cicids": { "label": 0, "probability": 0.92, "confidence": 0.90 }
  },
  "fusion": {
    "fused_label": 0,
    "fused_probability": 0.94,
    "ensemble_confidence": 0.91,
    "agreement_level": 0.85
  },
  "request_id": "req_abc123",
  "processing_time_ms": 145
}
```

#### Predict single domain
```
POST /api/v1/predict/{domain}
Domain: network | iot | user | cicids

Request:
{
  "features": { ... domain-specific features ... },
  "context": { ... }
}

Response: (same structure, single domain)
```

#### Batch prediction
```
POST /api/v1/predict/batch

Request:
{
  "requests": [
    { "domain": "network", "features": {...}, "context": {...} },
    { "domain": "iot", "features": {...}, "context": {...} },
    ...
  ]
}

Response:
{
  "status": "success",
  "results": [ ... ],
  "request_id": "req_def456",
  "total_processing_time_ms": 890
}
```

### 3.2 Trust Engine Endpoints

#### Get current trust
```
GET /api/v1/trust/{agent_id}
Authorization: Bearer <token>

Response:
{
  "agent_id": "agent_001",
  "domain": "network",
  "current_trust": 87.34,
  "current_risk": 12.66,
  "threat_level": "LOW",
  "trust_trend": "stable",
  "last_updated": "2024-01-01T00:00:00Z",
  "components": {
    "prediction_accuracy": 0.95,
    "historical_consistency": 0.88,
    "anomaly_score": 0.03,
    "context_factor": 1.02
  }
}
```

#### Get trust history
```
GET /api/v1/trust/{agent_id}/history
Query: ?window=24h&granularity=1h

Response:
{
  "agent_id": "agent_001",
  "window": "24h",
  "granularity": "1h",
  "data_points": [
    { "timestamp": "2024-01-01T00:00:00Z", "trust_score": 85.2, "risk_score": 14.8 },
    { "timestamp": "2024-01-01T01:00:00Z", "trust_score": 86.1, "risk_score": 13.9 },
    ...
  ],
  "statistics": {
    "mean": 85.7,
    "std": 2.1,
    "min": 82.3,
    "max": 88.9,
    "trend": "slight_increase"
  }
}
```

#### Get composite trust
```
GET /api/v1/trust/composite
Authorization: Bearer <token>

Response:
{
  "composite_trust": 81.45,
  "composite_risk": 18.55,
  "domains": {
    "network": { "trust": 87.34, "weight": 0.35, "status": "HEALTHY" },
    "iot": { "trust": 82.15, "weight": 0.25, "status": "HEALTHY" },
    "user": { "trust": 74.20, "weight": 0.25, "status": "WATCHLIST" },
    "cicids": { "trust": 79.80, "weight": 0.15, "status": "HEALTHY" }
  },
  "overall_status": "HEALTHY",
  "last_updated": "2024-01-01T00:00:00Z"
}
```

#### Update trust weight
```
PATCH /api/v1/trust/weights

Request:
{
  "weights": {
    "network": 0.30,
    "iot": 0.30,
    "user": 0.25,
    "cicids": 0.15
  },
  "reason": "Manual adjustment for CICIDS model update"
}

Response:
{
  "status": "success",
  "previous_weights": { "network": 0.35, "iot": 0.25, "user": 0.25, "cicids": 0.15 },
  "new_weights": { "network": 0.30, "iot": 0.30, "user": 0.25, "cicids": 0.15 },
  "effective_from": "2024-01-01T00:00:00Z"
}
```

### 3.3 Temporal Recovery Endpoints

#### Trigger recovery
```
POST /api/v1/recovery/trigger

Request:
{
  "agent_id": "agent_001",
  "recovery_type": "auto",
  "force": false
}

Response:
{
  "status": "recovery_initiated",
  "agent_id": "agent_001",
  "previous_trust": 62.34,
  "recovery_target": 75.00,
  "estimated_recovery_time": "2024-01-01T02:30:00Z",
  "recovery_actions": [
    { "action": "positive_interaction_required", "priority": "high" },
    { "action": "reduce_anomalous_activity", "priority": "medium" }
  ],
  "recovery_probability": 0.78
}
```

#### Get recovery status
```
GET /api/v1/recovery/status/{agent_id}

Response:
{
  "agent_id": "agent_001",
  "recovery_active": true,
  "started_at": "2024-01-01T00:00:00Z",
  "progress": 0.65,
  "current_trust": 70.12,
  "target_trust": 75.00,
  "estimated_completion": "2024-01-01T01:45:00Z",
  "drift_detected": false,
  "actions_remaining": ["complete_interaction_evaluation"]
}
```

#### Get recovery history
```
GET /api/v1/recovery/history/{agent_id}
Query: ?limit=10&offset=0

Response:
{
  "agent_id": "agent_001",
  "total_recoveries": 24,
  "success_rate": 0.83,
  "recoveries": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "type": "auto",
      "from_trust": 55.0,
      "to_trust": 78.5,
      "duration_sec": 5400,
      "success": true
    },
    ...
  ]
}
```

### 3.4 Deception Engine Endpoints

#### Deploy deception
```
POST /api/v1/deception/deploy

Request:
{
  "threat_id": "threat_001",
  "deception_type": "honeypot",
  "target": "attacker_ip_here",
  "config": {
    "service_type": "ssh",
    "port": 2222,
    "credibility": "high",
    "lifetime_sec": 3600
  }
}

Response:
{
  "status": "deployed",
  "deception_id": "dec_001",
  "type": "honeypot",
  "endpoint": "192.168.1.200:2222",
  "credential_honeypot": "admin:hV8k#mP2$sL9",
  "expires_at": "2024-01-01T01:00:00Z",
  "monitoring_key": "mon_abc123"
}
```

#### List active deceptions
```
GET /api/v1/deception/active

Response:
{
  "active_deceptions": [
    {
      "deception_id": "dec_001",
      "type": "honeypot",
      "service": "ssh",
      "target_attacker": "10.0.0.5",
      "status": "active",
      "interactions": 3,
      "deployed_at": "2024-01-01T00:00:00Z",
      "expires_at": "2024-01-01T01:00:00Z"
    },
    {
      "deception_id": "dec_002",
      "type": "fake_credential",
      "service": "web_login",
      "target_attacker": "10.0.0.5",
      "status": "triggered",
      "interactions": 7,
      "deployed_at": "2024-01-01T00:30:00Z"
    }
  ],
  "total_active": 2
}
```

#### Mutate credential
```
POST /api/v1/deception/mutate/{deception_id}

Response:
{
  "deception_id": "dec_002",
  "old_credential": "admin:OldPass123",
  "new_credential": "root:Xk9#mP4$vR2",
  "mutation_type": "automatic",
  "mutated_at": "2024-01-01T00:45:00Z",
  "next_mutation_at": "2024-01-01T01:15:00Z"
}
```

### 3.5 Response Engine Endpoints

#### Execute response
```
POST /api/v1/response/execute

Request:
{
  "threat_id": "threat_001",
  "response_type": "isolate_agent",
  "target": "agent_001",
  "config": {
    "block_duration_sec": 3600,
    "notify_admin": true,
    "rotation_credentials": true
  }
}

Response:
{
  "status": "executed",
  "response_id": "resp_001",
  "actions": [
    { "action": "isolate_agent", "target": "agent_001", "status": "completed" },
    { "action": "rotate_credentials", "target": "agent_001", "status": "in_progress" },
    { "action": "deploy_deception", "target": "attacker", "status": "initiated" },
    { "action": "notify_admin", "target": "security_team", "status": "completed" }
  ],
  "executed_at": "2024-01-01T00:00:00Z",
  "estimated_completion": "2024-01-01T00:05:00Z"
}
```

#### Get response history
```
GET /api/v1/response/history
Query: ?agent_id=agent_001&limit=20

Response:
{
  "responses": [
    {
      "response_id": "resp_001",
      "threat_id": "threat_001",
      "type": "isolate_agent",
      "status": "completed",
      "initiated_by": "auto",
      "executed_at": "2024-01-01T00:00:00Z",
      "completed_at": "2024-01-01T00:04:32Z",
      "result": "success"
    },
    ...
  ],
  "total_count": 42
}
```

### 3.6 Threat Endpoints

#### Report threat
```
POST /api/v1/threat/report

Request:
{
  "source": "network_engine",
  "threat_type": "malicious_packet",
  "severity": "HIGH",
  "confidence": 0.92,
  "source_ip": "10.0.0.5",
  "destination_ip": "192.168.1.100",
  "destination_port": 443,
  "description": "SQL injection attempt detected",
  "raw_data": { "payload": "..." }
}

Response:
{
  "status": "received",
  "threat_id": "threat_001",
  "correlation_results": {
    "related_events": 3,
    "correlation_score": 0.78,
    "attack_timeline_id": "timeline_001"
  }
}
```

#### Get threat heatmap
```
GET /api/v1/threat/heatmap
Query: ?window=24h&resolution=1h

Response:
{
  "window": "24h",
  "resolution": "1h",
  "hotspots": [
    {
      "source_ip": "10.0.0.5",
      "threat_count": 145,
      "avg_severity": 0.72,
      "time_distribution": [5, 12, 8, ..., 3]
    },
    ...
  ],
  "heatmap_grid": [
    { "x": 0, "y": 0, "intensity": 0.85 },
    ...
  ],
  "trend": "increasing"
}
```

### 3.7 Agent Management Endpoints

#### Register agent
```
POST /api/v1/agents/register

Request:
{
  "name": "Network Agent 01",
  "agent_type": "network",
  "version": "2.0.0",
  "config": {
    "model": "UNSW_RF_v2",
    "update_interval_sec": 60
  }
}

Response:
{
  "agent_id": "agent_001",
  "api_key": "bv_sk_xxxxxxxxxxxxxxxx",
  "secret": "bv_sec_yyyyyyyyyyyyyyyy",
  "status": "active",
  "registered_at": "2024-01-01T00:00:00Z"
}
```

#### List agents
```
GET /api/v1/agents
Query: ?type=network&status=active

Response:
{
  "agents": [
    {
      "agent_id": "agent_001",
      "name": "Network Agent 01",
      "type": "network",
      "status": "active",
      "trust_score": 87.34,
      "last_heartbeat": "2024-01-01T00:00:00Z",
      "version": "2.0.0"
    },
    ...
  ],
  "total": 8
}
```

### 3.8 Dashboard Endpoints

#### Get dashboard summary
```
GET /api/v1/dashboard/summary

Response:
{
  "system_status": "OPERATIONAL",
  "agents": {
    "total": 8,
    "active": 7,
    "compromised": 0,
    "recovering": 1
  },
  "trust_summary": {
    "composite_trust": 81.45,
    "network_trust": 87.34,
    "iot_trust": 82.15,
    "user_trust": 74.20,
    "cicids_trust": 79.80
  },
  "threat_summary": {
    "total_24h": 145,
    "critical": 2,
    "high": 15,
    "medium": 48,
    "low": 80,
    "top_attack": "SQL_Injection"
  },
  "deception_summary": {
    "active_honeypots": 5,
    "fake_credentials": 12,
    "attacks_captured": 34
  },
  "response_summary": {
    "total_responses_24h": 18,
    "success_rate": 0.94,
    "auto_responses": 15,
    "manual_responses": 3
  }
}
```

#### WebSocket real-time updates
```
WS /api/v1/ws/dashboard?token=<jwt>

Server pushes:
{
  "event": "trust_update",
  "data": { "agent_id": "agent_001", "new_trust": 87.5, "old_trust": 87.34 }
}
{
  "event": "threat_detected",
  "data": { "threat_id": "threat_002", "severity": "CRITICAL", "type": "ransomware" }
}
{
  "event": "deception_triggered",
  "data": { "deception_id": "dec_003", "attacker_ip": "10.0.0.5" }
}
{
  "event": "response_executed",
  "data": { "response_id": "resp_002", "action": "block_ip", "target": "10.0.0.5" }
}
{
  "event": "recovery_completed",
  "data": { "agent_id": "agent_002", "new_trust": 78.5, "recovery_time_sec": 4200 }
}
```

### 3.9 Report Endpoints

#### Generate report
```
POST /api/v1/reports/generate

Request:
{
  "report_type": "trust_analysis",
  "time_window": "7d",
  "format": "pdf",
  "include": ["charts", "recommendations", "forensics"]
}

Response:
{
  "report_id": "rpt_001",
  "status": "generating",
  "estimated_completion": "2024-01-01T00:05:00Z",
  "download_url": "/api/v1/reports/download/rpt_001"
}
```

#### List reports
```
GET /api/v1/reports
Query: ?type=trust_analysis&limit=10

Response:
{
  "reports": [
    {
      "report_id": "rpt_001",
      "type": "trust_analysis",
      "created_at": "2024-01-01T00:00:00Z",
      "status": "completed",
      "size_bytes": 2456789,
      "format": "pdf"
    },
    ...
  ]
}
```

---

## 4. API Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "TRUST_ENGINE_ERROR",
    "message": "Failed to compute trust score for agent agent_001",
    "details": {
      "agent_id": "agent_001",
      "reason": "Model not loaded",
      "retry_after_sec": 30
    },
    "request_id": "req_err_001",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_FAILED` | 401 | Invalid or expired token |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `RATE_LIMITED` | 429 | Too many requests |
| `MODEL_NOT_LOADED` | 503 | AI model unavailable |
| `TRUST_ENGINE_ERROR` | 500 | Trust computation failed |
| `DECEPTION_ERROR` | 500 | Deception deployment failed |

---

## 5. Rate Limiting

```
Headers:
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1700003600

Limits by endpoint:
- /predict: 100/minute
- /trust: 200/minute
- /deception: 50/minute
- /response: 30/minute
- /dashboard: 60/minute
- /agents: 100/minute
```

---

## 6. API Versioning

- Current: `/api/v1/`
- Deprecation: 6 months notice
- Migration guide provided with new version
- Backward compatible within major version

