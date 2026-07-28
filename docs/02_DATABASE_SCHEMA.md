# BLACK VEIL V2 — Database Schema

## 1. Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE OVERVIEW                          │
│  PostgreSQL (Primary) + Redis (Cache) + MongoDB (Logs/Events)      │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. PostgreSQL Schema

### 2.1 Trust Scores Table
```sql
CREATE TABLE trust_scores (
    id              BIGSERIAL PRIMARY KEY,
    agent_id        VARCHAR(64) NOT NULL,
    domain          VARCHAR(32) NOT NULL, -- 'network', 'iot', 'user', 'cicids'
    trust_score     DOUBLE PRECISION NOT NULL, -- 0.0 to 100.0
    risk_score      DOUBLE PRECISION NOT NULL, -- 0.0 to 100.0
    threat_level    VARCHAR(16) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    confidence      DOUBLE PRECISION NOT NULL, -- 0.0 to 1.0
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Metadata
    model_version   VARCHAR(32),
    data_source     VARCHAR(128),
    features_hash   VARCHAR(64),
    
    CONSTRAINT fk_agent FOREIGN KEY (agent_id) REFERENCES agents(id)
);

CREATE INDEX idx_trust_agent_time ON trust_scores(agent_id, timestamp DESC);
CREATE INDEX idx_trust_domain_time ON trust_scores(domain, timestamp DESC);
CREATE INDEX idx_trust_threat_level ON trust_scores(threat_level, timestamp DESC);

-- Partition by month for performance
CREATE TABLE trust_scores_y2024m01 PARTITION OF trust_scores
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### 2.2 Agents Table
```sql
CREATE TABLE agents (
    id              VARCHAR(64) PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    agent_type      VARCHAR(32) NOT NULL, -- 'network', 'iot', 'user', 'cicids', 'fusion'
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE', -- 'ACTIVE', 'SUSPENDED', 'COMPROMISED', 'RECOVERING'
    ip_address      INET,
    port            INTEGER,
    version         VARCHAR(16),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_heartbeat  TIMESTAMPTZ,
    config_json     JSONB,
    metadata_json   JSONB
);

CREATE INDEX idx_agents_type ON agents(agent_type);
CREATE INDEX idx_agents_status ON agents(status);
```

### 2.3 Temporal Recovery Log
```sql
CREATE TABLE temporal_recovery_log (
    id              BIGSERIAL PRIMARY KEY,
    agent_id        VARCHAR(64) NOT NULL,
    recovery_type   VARCHAR(32) NOT NULL, -- 'AUTO', 'MANUAL', 'TRIGGERED'
    previous_trust  DOUBLE PRECISION NOT NULL,
    current_trust   DOUBLE PRECISION NOT NULL,
    recovery_action VARCHAR(128),
    drift_detected  BOOLEAN DEFAULT FALSE,
    drift_score     DOUBLE PRECISION,
    recovery_prob   DOUBLE PRECISION,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_sec    INTEGER,
    success         BOOLEAN,
    details_json    JSONB,
    
    CONSTRAINT fk_recovery_agent FOREIGN KEY (agent_id) REFERENCES agents(id)
);

CREATE INDEX idx_recovery_agent ON temporal_recovery_log(agent_id, timestamp DESC);
CREATE INDEX idx_recovery_success ON temporal_recovery_log(success, timestamp DESC);
```

### 2.4 Deception Events
```sql
CREATE TABLE deception_events (
    id              BIGSERIAL PRIMARY KEY,
    threat_id       BIGINT REFERENCES threat_events(id),
    deception_type  VARCHAR(32) NOT NULL, -- 'HONEYPOT', 'FAKE_CREDENTIAL', 'DECOY_SERVICE', 'NETWORK_DECEPTION'
    deception_id    VARCHAR(64) NOT NULL, -- unique identifier for the deception resource
    target_agent    VARCHAR(64) REFERENCES agents(id),
    attacker_ip     INET,
    confidence      DOUBLE PRECISION,
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE', -- 'ACTIVE', 'TRIGGERED', 'EXPIRED'
    deployed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    triggered_at    TIMESTAMPTZ,
    expired_at      TIMESTAMPTZ,
    payload_json    JSONB,
    response_json   JSONB
);

CREATE INDEX idx_deception_threat ON deception_events(threat_id);
CREATE INDEX idx_deception_type ON deception_events(deception_type);
CREATE INDEX idx_deception_status ON deception_events(status);
```

### 2.5 Threat Events
```sql
CREATE TABLE threat_events (
    id              BIGSERIAL PRIMARY KEY,
    agent_id        VARCHAR(64) NOT NULL REFERENCES agents(id),
    threat_type     VARCHAR(64) NOT NULL,
    severity        VARCHAR(16) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    confidence      DOUBLE PRECISION NOT NULL,
    source_ip       INET,
    destination_ip  INET,
    protocol        VARCHAR(16),
    port            INTEGER,
    payload_hash    VARCHAR(64),
    description     TEXT,
    raw_data        JSONB,
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ,
    resolution      VARCHAR(128),
    
    CONSTRAINT fk_threat_agent FOREIGN KEY (agent_id) REFERENCES agents(id)
);

CREATE INDEX idx_threat_severity ON threat_events(severity, detected_at DESC);
CREATE INDEX idx_threat_agent ON threat_events(agent_id, detected_at DESC);
CREATE INDEX idx_threat_source ON threat_events(source_ip);
```

### 2.6 Response Actions
```sql
CREATE TABLE response_actions (
    id              BIGSERIAL PRIMARY KEY,
    threat_id       BIGINT REFERENCES threat_events(id),
    response_type   VARCHAR(32) NOT NULL, -- 'ISOLATE', 'BLOCK', 'ROTATE', 'ALERT', 'DECEPTION'
    target          VARCHAR(128),
    action          VARCHAR(256) NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'EXECUTED', 'FAILED', 'ROLLED_BACK'
    initiated_by    VARCHAR(64) REFERENCES agents(id),
    executed_at     TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    result_json     JSONB,
    error_message   TEXT
);

CREATE INDEX idx_response_threat ON response_actions(threat_id);
CREATE INDEX idx_response_status ON response_actions(status);
```

### 2.7 Fake Credentials
```sql
CREATE TABLE fake_credentials (
    id              BIGSERIAL PRIMARY KEY,
    service_name    VARCHAR(128) NOT NULL,
    username        VARCHAR(128) NOT NULL,
    password_hash   VARCHAR(256) NOT NULL,
    domain          VARCHAR(128),
    credential_type VARCHAR(32) NOT NULL, -- 'SSH', 'HTTP', 'FTP', 'DB', 'API'
    status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    lifetime_sec    INTEGER NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at    TIMESTAMPTZ,
    mutated_count   INTEGER DEFAULT 0,
    mutation_history JSONB,
    parent_id       BIGINT REFERENCES fake_credentials(id)
);

CREATE INDEX idx_fake_cred_status ON fake_credentials(status);
CREATE INDEX idx_fake_cred_type ON fake_credentials(credential_type);
```

### 2.8 Forensic Events (Detailed Logging)
```sql
CREATE TABLE forensic_events (
    id              BIGSERIAL PRIMARY KEY,
    event_id        VARCHAR(64) UNIQUE NOT NULL,
    event_type      VARCHAR(32) NOT NULL,
    source          VARCHAR(64) NOT NULL, -- which engine generated this
    severity        VARCHAR(16) NOT NULL,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    chain_of_events JSONB,
    evidence_json   JSONB,
    timeline_data   JSONB,
    reconstruction  TEXT,
    hash_chain      VARCHAR(64)
);

CREATE INDEX idx_forensic_type ON forensic_events(event_type);
CREATE INDEX idx_forensic_source ON forensic_events(source);
CREATE INDEX idx_forensic_time ON forensic_events(timestamp DESC);
```

### 2.9 User Activity Log
```sql
CREATE TABLE user_activity_log (
    id              BIGSERIAL PRIMARY KEY,
    user_id         VARCHAR(64) NOT NULL,
    activity_type   VARCHAR(32) NOT NULL,
    resource        VARCHAR(256),
    action          VARCHAR(128),
    ip_address      INET,
    user_agent      TEXT,
    risk_level      VARCHAR(16),
    trust_impact    DOUBLE PRECISION,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata_json   JSONB
);

CREATE INDEX idx_user_activity ON user_activity_log(user_id, timestamp DESC);
CREATE INDEX idx_activity_type ON user_activity_log(activity_type, timestamp DESC);
```

### 2.10 Heatmap Data
```sql
CREATE TABLE threat_heatmap (
    id              BIGSERIAL PRIMARY KEY,
    time_slot       TIMESTAMPTZ NOT NULL,
    source_ip       INET,
    destination_ip  INET,
    threat_count    INTEGER NOT NULL DEFAULT 0,
    avg_severity    DOUBLE PRECISION,
    threat_types    JSONB,
    risk_score      DOUBLE PRECISION,
    trust_impact    DOUBLE PRECISION,
    
    UNIQUE(time_slot, source_ip, destination_ip)
);

CREATE INDEX idx_heatmap_time ON threat_heatmap(time_slot DESC);
CREATE INDEX idx_heatmap_source ON threat_heatmap(source_ip);
```

### 2.11 Model Registry
```sql
CREATE TABLE model_registry (
    id              BIGSERIAL PRIMARY KEY,
    model_name      VARCHAR(128) NOT NULL,
    model_version   VARCHAR(32) NOT NULL,
    model_type      VARCHAR(32) NOT NULL, -- 'RF', 'XGBOOST', 'NN', 'ENSEMBLE'
    domain          VARCHAR(32) NOT NULL, -- 'network', 'iot', 'user', 'cicids'
    file_path       VARCHAR(512) NOT NULL,
    accuracy        DOUBLE PRECISION,
    f1_score        DOUBLE PRECISION,
    precision       DOUBLE PRECISION,
    recall          DOUBLE PRECISION,
    training_date   TIMESTAMPTZ,
    training_config JSONB,
    is_active       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(model_name, model_version)
);

CREATE INDEX idx_model_domain ON model_registry(domain);
CREATE INDEX idx_model_active ON model_registry(is_active);
```

## 3. Redis Cache Schema

```python
# Key Patterns
trust:agent:{agent_id}:current           → TrustScore (JSON)
trust:agent:{agent_id}:history:{window}  → List[TrustScore]
threat:recent:{limit}                    → List[ThreatEvent]
deception:active:{type}                  → Set[DeceptionID]
heatmap:realtime:{timeslot}              → Hash[IP → Count]
session:{session_id}                     → SessionData
rate_limit:{endpoint}:{ip}               → Counter
```

## 4. MongoDB Collections (Logs)

```javascript
// System Logs Collection
{
  _id: ObjectId,
  level: "INFO" | "WARN" | "ERROR" | "DEBUG",
  module: String,
  message: String,
  timestamp: Date,
  trace_id: String,
  metadata: Object
}

// Audit Trail Collection
{
  _id: ObjectId,
  action: String,
  actor: String,
  resource: String,
  old_value: Mixed,
  new_value: Mixed,
  timestamp: Date,
  ip: String
}

// Agent Communication Log
{
  _id: ObjectId,
  from_agent: String,
  to_agent: String,
  message_type: String,
  payload: Mixed,
  timestamp: Date,
  signature: String
}
```

## 5. Database Initialization Script

```sql
-- init_db.sql
CREATE DATABASE blackveil;
CREATE DATABASE blackveil_cache;
CREATE DATABASE blackveil_logs;

-- Connect to blackveil
\c blackveil;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS trust;
CREATE SCHEMA IF NOT EXISTS threat;
CREATE SCHEMA IF NOT EXISTS deception;
CREATE SCHEMA IF NOT EXISTS forensic;
CREATE SCHEMA IF NOT EXISTS audit;

-- Apply all table definitions above within respective schemas
-- Set up partitioning and indexes
-- Create materialized views for reports
```

