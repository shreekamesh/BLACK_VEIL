# BLACK VEIL V2 — Complete System Architecture

## IEEE Research Paper Title
**Temporal Trust Recovery and Adaptive Cyber Deception Framework for Multi-Agent AI Systems**

---

## 1. System Overview

BLACK VEIL is a production-ready IEEE cybersecurity research framework that implements a multi-agent architecture for:
- **Temporal Trust Recovery** — Dynamic trust scoring with time-series recovery mechanisms
- **Adaptive Cyber Deception** — Intelligent deception deployment based on threat intelligence
- **Multi-Agent AI Fusion** — Collaborative decision making across distributed AI agents

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                    │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │  Dashboard  │  │  REST API    │  │  WebSocket  │  │  CLI/Term    │ │
│  │  (React)    │  │  Consumers   │  │  Real-time  │  │  Interface   │ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘  └──────┬───────┘ │
└─────────┼─────────────────┼─────────────────┼─────────────────┼────────┘
          │                 │                 │                 │
┌─────────┼─────────────────┼─────────────────┼─────────────────┼────────┐
│         │        API GATEWAY (FastAPI)       │                 │        │
│  ┌──────┴──────────────────┴─────────────────┴─────────────────┴──────┐ │
│  │                     AUTHENTICATION / AUTHORIZATION                  │ │
│  │                  JWT + RBAC + API Key Management                   │ │
│  └──────────────────────────────┬─────────────────────────────────────┘ │
│                                 │                                      │
│  ┌──────────────────────────────┼─────────────────────────────────────┐ │
│  │                   ORCHESTRATION LAYER                              │ │
│  │  ┌─────────────┐ ┌─────────┴────────┐ ┌──────────────────────┐   │ │
│  │  │  AI CORE    │ │   TRUST ENGINE   │ │  TEMPORAL RECOVERY   │   │ │
│  │  │  Orchestr.  │ │   Orchestrator   │ │   Orchestrator       │   │ │
│  │  └──────┬──────┘ └────────┬─────────┘ └──────────┬───────────┘   │ │
│  │  ┌──────┴──────┐ ┌───────┴────────┐ ┌────────────┴─────────────┐ │ │
│  │  │ DECEPTION   │ │   RESPONSE     │ │   FORENSIC INTELLIGENCE  │ │ │
│  │  │ Engine      │ │   Engine       │ │   Engine                │ │ │
│  │  └─────────────┘ └────────────────┘ └──────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                 │                                      │
│  ┌──────────────────────────────┼─────────────────────────────────────┐ │
│  │                    SERVICE LAYER                                   │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────┐ ┌────────┐ ┌──────────────┐ │ │
│  │  │ Network  │ │   IoT    │ │ User │ │CICIDS  │ │   Fusion     │ │ │
│  │  │ Engine   │ │  Engine  │ │Engine│ │ Engine │ │   Engine     │ │ │
│  │  └────┬─────┘ └────┬─────┘ └──┬───┘ └───┬────┘ └──────┬───────┘ │ │
│  │       └────────────┴──────────┴──────────┴─────────────┘          │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                 │                                      │
│  ┌──────────────────────────────┼─────────────────────────────────────┐ │
│  │                    DATA LAYER                                     │ │
│  │  ┌────────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────────┐ │ │
│  │  │ PostgreSQL │ │  Redis    │ │  MongoDB  │ │  File System    │ │ │
│  │  │ (Persist)  │ │ (Cache)   │ │ (Logs)    │ │  (Datasets)     │ │ │
│  │  └────────────┘ └───────────┘ └───────────┘ └─────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3. Module Architecture

### 3.1 AI Core Modules

```
ai_core/
├── network_engine/     — UNSW-NB15 model inference & network threat detection
├── iot_engine/         — EDGE-IoT model inference & IoT anomaly detection
├── user_engine/        — CERT-r4.2 model inference & insider threat detection
├── cicids_engine/      — CICIDS2017 model inference & traffic analysis
└── fusion_engine/      — Multi-model fusion & ensemble decision making
```

### 3.2 Trust Engine Architecture

```
┌──────────── INGESTION LAYER ────────────┐
│  Network Scores → IoT Scores → User     │
│  Scores → CICIDS Scores → Temporal Data │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         TRUST COMPUTATION LAYER          │
│  ┌────────────┐ ┌──────────┐ ┌────────┐ │
│  │ Weight     │ │ Context  │ │ Time   │ │
│  │ Adapter    │ │ Analyzer │ │ Decay  │ │
│  └────────────┘ └──────────┘ └────────┘ │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          TRUST OUTPUT LAYER              │
│  ┌────────────┐ ┌──────────┐ ┌────────┐ │
│  │ Final      │ │ Trust    │ │ Threat │ │
│  │ Trust Score│ │ Category │ │ Level  │ │
│  └────────────┘ └──────────┘ └────────┘ │
└─────────────────────────────────────────┘
```

### 3.3 Temporal Recovery Engine

```
┌────────── TIME-SERIES ANALYSIS ──────────┐
│  Historical Trust Scores → Pattern       │
│  Detection → Anomaly Identification      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        RECOVERY MECHANISM LAYER          │
│  ┌────────────┐ ┌──────────┐ ┌────────┐ │
│  │ Recovery   │ │ Drift    │ │ Memory │ │
│  │ Probability│ │ Detection│ │ Buffer │ │
│  └────────────┘ └──────────┘ └────────┘ │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          RECOVERY OUTPUT LAYER           │
│  ┌────────────┐ ┌──────────┐ ┌────────┐ │
│  │ Recovery   │ │ Trust    │ │ Re-     │ │
│  │ Action     │ │ Restore  │ │ evaluation│
│  └────────────┘ └──────────┘ └────────┘ │
└─────────────────────────────────────────┘
```

### 3.4 Deception Engine

```
┌────────── THREAT INTELLIGENCE ───────────┐
│  Threat Level → Attack Type → Confidence │
│  → Attacker Profile                      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        DECEPTION SELECTION LAYER         │
│  ┌────────────┐ ┌──────────┐ ┌────────┐ │
│  │ Honeypot   │ │ Fake     │ │ Decoy  │ │
│  │ Selection  │ │Credential│ │ Service │ │
│  └────────────┘ └──────────┘ └────────┘ │
│  ┌────────────┐ ┌──────────────────────┐ │
│  │ Network    │ │  Dynamic Mutation    │ │
│  │ Deception  │ │  Engine              │ │
│  └────────────┘ └──────────────────────┘ │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        DEPLOYMENT LAYER                  │
│  → Deploy Honeypot                       │
│  → Mutate Credentials                    │
│  → Generate Fake Traffic                 │
│  → Spoof Services                        │
└─────────────────────────────────────────┘
```

### 3.5 Response Engine

```
┌────────── THREAT ASSESSMENT ────────────┐
│  Threat Level → Risk Index → Confidence │
│  → Urgency Score                        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        RESPONSE SELECTION LAYER          │
│  ┌────────────┐ ┌──────────┐ ┌────────┐ │
│  │ Passive    │ │ Active   │ │ Hybrid │ │
│  │ Response   │ │ Response │ │Response│ │
│  └────────────┘ └──────────┘ └────────┘ │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        AUTOMATED ACTIONS                │
│  → Isolate compromised agent            │
│  → Rotate credentials                   │
│  → Block malicious IP                   │
│  → Alert security team                  │
│  → Log forensic evidence                │
└─────────────────────────────────────────┘
```

## 4. Data Flow Architecture

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Raw Data   │──→│  Preprocess │──→│  AI Models  │
│  (Datasets) │   │  Pipeline   │   │  Inference  │
└─────────────┘   └─────────────┘   └──────┬──────┘
                                           │
                                    ┌──────▼──────┐
                                    │   Trust     │
                                    │   Engine    │
                                    └──────┬──────┘
                                           │
┌──────────────────────────────────────────┼──────────┐
│                    ┌─────────────────────▼────┐      │
│                    │  Temporal Recovery       │      │
│                    │  Engine                  │      │
│                    └────────────┬────────────┘      │
│                                 │                   │
│                    ┌────────────▼────────────┐      │
│                    │  Threat Correlation     │      │
│                    └────────────┬────────────┘      │
│                                 │                   │
│              ┌──────────────────┼──────────────┐    │
│              ▼                  ▼              ▼    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │  Deception   │  │  Response    │  │ Forensic │ │
│  │  Engine      │  │  Engine      │  │ Engine   │ │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘ │
│         │                 │                │       │
│         └─────────────────┼────────────────┘       │
│                           ▼                        │
│                    ┌──────────────┐                │
│                    │  Dashboard   │                │
│                    │  & Reports   │                │
│                    └──────────────┘                │
└────────────────────────────────────────────────────┘
```

## 5. Component Interaction Matrix

| Component | Trust Engine | Recovery | Deception | Response | Forensic | Dashboard |
|-----------|-------------|----------|-----------|----------|----------|-----------|
| AI Core | ⬆ Scores | ⬆ History | ⬆ Threats | ⬆ Alerts | ⬆ Events | ⬆ Metrics |
| Trust Engine | — | ⬆ Trust | ⬆ Risk | ⬆ Risk | ⬆ Logs | ⬆ Scores |
| Recovery | ⬅ Pull | — | ⬆ Recovery | ⬆ Recovery | ⬆ Timeline | ⬆ Status |
| Deception | ⬅ Pull | ⬅ Pull | — | ⬆ Deception | ⬆ Actions | ⬆ Status |
| Response | ⬅ Pull | ⬅ Pull | ⬅ Trigger | — | ⬆ Actions | ⬆ Actions |
| Database | ⬆ Store | ⬆ Store | ⬆ Store | ⬆ Store | ⬆ Store | ⬅ Query |

## 6. Scalability Design

- **Horizontal Scaling**: Each engine can be deployed as independent microservice
- **Caching Layer**: Redis for real-time trust scores and threat data
- **Message Queue**: RabbitMQ/Kafka for async inter-engine communication
- **Database Sharding**: By time window for temporal data
- **Model Serving**: GPU-accelerated inference with ONNX runtime

## 7. Fault Tolerance

- **Circuit Breaker**: Per-engine failure isolation
- **Retry Mechanism**: Configurable retry with exponential backoff
- **Fallback Models**: If primary model fails, use ensemble fallback
- **Graceful Degradation**: If trust engine fails, use last known scores
- **Health Checks**: Every module exposes `/health` endpoint

