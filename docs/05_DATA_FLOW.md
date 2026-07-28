# BLACK VEIL V2 — Complete Data Flow

---

## 1. High-Level Data Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION LAYER                                         │
│                                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Network  │  │   IoT    │  │   User   │  │   CICIDS     │  │   Real-time      │  │
│  │ Dataset  │  │ Dataset  │  │ Dataset  │  │   Dataset    │  │   Streams        │  │
│  │(UNSW-NB15)│  │(EDGE-IoT)│  │(CERT-r4.2)│  │ (CICIDS2017) │  │   (Live Data)   │  │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └──────┬───────┘  └────────┬─────────┘  │
└────────┼──────────────┼────────────┼──────────────┼───────────────────┼────────────┘
         │              │            │              │                   │
         ▼              ▼            ▼              ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         DATA PREPROCESSING LAYER                                     │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  DataValidator → Cleaner → Encoder → Normalizer → FeatureExtractor          │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│  Output: ProcessedFeatureVectors (normalized, encoded, validated)                    │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         AI INFERENCE LAYER                                           │
│                                                                                     │
│  ┌──────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌────────────┐  │
│  │ Network      │  │   IoT    │  │   User   │  │   CICIDS     │  │  Fusion    │  │
│  │ Inference    │  │Inference  │  │Inference  │  │  Inference   │  │  Engine    │  │
│  │ (UNSW_RF)    │  │(EDGE_RF)  │  │(CERT_RF)  │  │(CICIDS_RF)   │  │            │  │
│  └──────┬───────┘  └─────┬────┘  └─────┬────┘  └──────┬───────┘  └──────┬─────┘  │
│         │                │            │              │                   │         │
│         └────────────────┴────────────┴──────────────┴───────────────────┘         │
│                                      │                                             │
│                              Predictions + Probabilities                           │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         TRUST COMPUTATION LAYER                                     │
│                                                                                     │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Network      │  │   IoT Trust      │  │   User Trust     │  │   CICIDS     │  │
│  │ Trust Score  │  │   Score          │  │   Score          │  │   Trust      │  │
│  └──────┬───────┘  └──────┬───────────┘  └──────┬───────────┘  └──────┬───────┘  │
│         │                │                    │                    │             │
│         └────────────────┴────────────────────┴────────────────────┘             │
│                                      │                                             │
│                            ┌─────────▼──────────┐                                 │
│                            │  Composite Trust   │                                 │
│                            │  Score (Weighted)  │                                 │
│                            └─────────┬──────────┘                                 │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         TEMPORAL RECOVERY LAYER                                     │
│                                                                                     │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Trust        │  │   Drift          │  │   Recovery       │  │   Memory     │  │
│  │ Decay        │  │   Detection      │  │   Computation    │  │   Buffer     │  │
│  └──────┬───────┘  └──────┬───────────┘  └──────┬───────────┘  └──────┬───────┘  │
│         │                │                    │                    │             │
│         └────────────────┴────────────────────┴────────────────────┘             │
│                                      │                                             │
│                          Recovered Trust Score                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         THREAT CORRELATION LAYER                                    │
│                                                                                     │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Event        │  │   Correlation    │  │   Cluster        │  │   Attack     │  │
│  │ Collection   │  │   Analysis       │  │   Detection      │  │   Timeline   │  │
│  └──────┬───────┘  └──────┬───────────┘  └──────┬───────────┘  └──────┬───────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
            ┌─────────────────────────┼─────────────────────────┐
            │                         │                         │
            ▼                         ▼                         ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│   DECEPTION ENGINE    │ │   RESPONSE ENGINE     │ │   FORENSIC ENGINE    │
│                       │ │                       │ │                       │
│   ┌───────────────┐   │ │   ┌───────────────┐   │ │   ┌───────────────┐   │
│   │ Deception     │   │ │   │ Response      │   │ │   │ Evidence      │   │
│   │ Selection     │   │ │   │ Selection     │   │ │   │ Collection    │   │
│   └───────┬───────┘   │ │   └───────┬───────┘   │ │   └───────┬───────┘   │
│   ┌───────▼───────┐   │ │   ┌───────▼───────┐   │ │   ┌───────▼───────┐   │
│   │ Fake          │   │ │   │ Action        │   │ │   │ Timeline     │   │
│   │ Credential    │   │ │   │ Execution     │   │ │   │ Reconstruction│   │
│   └───────┬───────┘   │ │   └───────┬───────┘   │ │   └───────┬───────┘   │
│   ┌───────▼───────┐   │ │   ┌───────▼───────┐   │ │   ┌───────▼───────┐   │
│   │ Honeypot      │   │ │   │ Action        │   │ │   │ Intelligence │   │
│   │ Deployment    │   │ │   │ Monitoring    │   │ │   │ Extraction   │   │
│   └───────────────┘   │ │   └───────────────┘   │ │   └───────────────┘   │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
            │                         │                         │
            └─────────────────────────┼─────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         OUTPUT LAYER                                                 │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │  │
│  │  │Dashboard │  │  Reports │  │  Logs    │  │  Alerts  │  │  Database    │  │  │
│  │  │ (React)  │  │  (PDF)   │  │ (MongoDB)│  │ (Socket) │  │ (PostgreSQL) │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow Sequence (Detailed)

### 2.1 Batch Processing Flow
```
1. Load Dataset
   ├── Read CSV from /datasets/*.csv
   ├── Validate schema and data types
   └── Handle missing values

2. Preprocess
   ├── Encode categorical features
   ├── Normalize numerical features
   └── Extract relevant feature subset

3. Model Inference
   ├── Load trained model from /models/*.pkl
   ├── Run prediction on preprocessed data
   └── Output prediction + probability + confidence

4. Trust Computation
   ├── Calculate domain-specific trust score
   ├── Apply weight adaptation
   └── Compute composite trust score

5. Temporal Recovery
   ├── Load historical trust data
   ├── Apply time decay function
   ├── Detect trust drift
   └── Recover trust if needed

6. Threat Correlation
   ├── Collect threat events from all domains
   ├── Compute pairwise correlations
   ├── Detect threat clusters
   └── Build attack timeline

7. Decision & Response
   ├── Assess threat severity
   ├── Select deception technique
   ├── Deploy response action
   └── Log forensic evidence

8. Store & Report
   ├── Store in PostgreSQL (structured)
   ├── Store in MongoDB (logs/events)
   ├── Update Redis cache
   ├── Push to dashboard via WebSocket
   └── Generate report files
```

### 2.2 Real-time Streaming Flow
```
1. Data Ingestion (WebSocket/API)
   ├── Receive packet/event stream
   ├── Parse and validate input
   └── Queue for processing

2. Real-time Inference
   ├── Load model into memory (warm start)
   ├── Run lightweight prediction
   └── Publish result to event bus

3. Immediate Trust Update
   ├── Update trust score in Redis
   ├── Check drift conditions
   └── Trigger recovery if needed

4. Real-time Deception
   ├── Check if attack detected
   ├── Select and deploy deception
   └── Monitor attacker response

5. Response Execution
   ├── Execute automated response
   ├── Update system state
   └── Notify security team

6. Dashboard Push
   ├── Update real-time charts
   ├── Push alert notifications
   └── Update heatmap
```

---

## 3. Inter-Module Communication

### 3.1 Event Bus Topics
```
Topic: blackveil.inference.{domain}
Payload: {
  agent_id, prediction, probability, confidence,
  features_hash, timestamp, model_version
}

Topic: blackveil.trust.{domain}
Payload: {
  agent_id, trust_score, risk_score, threat_level,
  components[], timestamp
}

Topic: blackveil.threat.{type}
Payload: {
  threat_id, severity, confidence, source,
  target, attack_type, timestamp
}

Topic: blackveil.deception.{action}
Payload: {
  deception_id, type, target, status,
  attacker_ip, payload, timestamp
}

Topic: blackveil.response.{action}
Payload: {
  response_id, action_type, target,
  status, result, timestamp
}

Topic: blackveil.dashboard.update
Payload: {
  event_type, data, timestamp
}
```

### 3.2 API Endpoints Data Flow
```
POST /api/v1/predict
  → Validate API key (Auth)
  → Parse request body
  → Route to appropriate engine
  → Run inference
  → Compute trust score
  → Return prediction + trust

GET /api/v1/trust/{agent_id}
  → Validate API key (Auth)
  → Query PostgreSQL for trust history
  → Query Redis for current trust
  → Apply temporal recovery if needed
  → Return trust data

POST /api/v1/deception/deploy
  → Validate API key (Auth)
  → Analyze threat context
  → Select deception technique
  → Deploy deception resource
  → Return deception details

POST /api/v1/response/execute
  → Validate API key (Auth)
  → Assess threat severity
  → Select response action
  → Execute response
  → Monitor effectiveness
  → Return response result
```

---

## 4. Data Transformation Pipeline

### 4.1 Network Data (UNSW-NB15)
```
Raw → Clean → Encode → Normalize → Predict → Trust
42 features → 42 features → label_encoded → minmax_scaled → RF model → Trust(0-100)
```

### 4.2 IoT Data (EDGE-IoT)
```
Raw → Clean → Encode → Normalize → Merge → Predict → Trust
21 features → 21 features → label_encoded → minmax_scaled → time+features → RF model → Trust(0-100)
```

### 4.3 User Data (CERT-r4.2)
```
Raw → Encode → Normalize → Feature_Extract → Risk → Trust
10 features → encoded → normalized → user behavior → risk score → Trust(0-100)
```

### 4.4 CICIDS2017 Data
```
Raw → Clean → Encode → Normalize → Merge → [Predict] → [Trust]
79 features → cleaned → encoded → normalized → merged → need model → need trust
```

---

## 5. Data Retention Policy

| Data Type | Retention | Storage | Purpose |
|-----------|-----------|---------|---------|
| Raw datasets | Indefinite | File System | Research & retraining |
| Predictions | 90 days | PostgreSQL | Performance analysis |
| Trust scores | 1 year | PostgreSQL | Temporal analysis |
| Threat events | 180 days | PostgreSQL/Redis | Correlation |
| Deception logs | 90 days | PostgreSQL | Audit |
| Forensic evidence | 1 year | MongoDB | Investigation |
| System logs | 30 days | MongoDB | Debugging |
| Audit trail | 7 years | MongoDB | Compliance |
| Cache data | TTL-based | Redis | Performance |
| Reports | Indefinite | File System | Documentation |

