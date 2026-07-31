# 🛡️ BLACK VEIL

<p align="center">
  <img src="docs/logo.png" width="220" alt="BLACK VEIL Logo">
</p>

<p align="center">
  <strong>Autonomous Cognitive Cyber Defense Framework</strong><br>
  <em>AI • Zero Trust • Adaptive Security • Cognitive Defense • Self-Evolving</em>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Version-2.0.0-brightgreen?style=flat-square" alt="Version"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/PyTorch-2.0.1-red?style=flat-square&logo=pytorch" alt="PyTorch"></a>
  <a href="#"><img src="https://img.shields.io/badge/FastAPI-0.139-green?style=flat-square&logo=fastapi" alt="FastAPI"></a>
  <a href="#"><img src="https://img.shields.io/badge/IEEE-2026-orange?style=flat-square" alt="IEEE"></a>
  <a href="#"><img src="https://img.shields.io/badge/License-Apache%202.0-yellow?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Stars-⭐-brightgreen?style=flat-square" alt="Stars"></a>
</p>

---

## 📖 Overview

**BLACK VEIL** is a next-generation **autonomous cognitive cyber defense framework** designed to provide intelligent, adaptive, and self-evolving cybersecurity. Unlike conventional Intrusion Detection Systems that focus primarily on attack detection, BLACK VEIL combines:

| Component | Description |
|-----------|-------------|
| 🧠 **Cognitive AI** | Intelligent reasoning and decision-making |
| 🔐 **Dynamic Trust Intelligence** | Continuous, context-aware trust evaluation |
| 🧬 **Credential Mutation** | Self-evolving credential management |
| 🎭 **Adaptive Deception** | Integrated deception infrastructure |
| 📊 **Knowledge Graph Learning** | Persistent attack memory and learning |
| ⚡ **Autonomous Orchestration** | Self-driven defense coordination |
| 🎯 **Context-aware Security Actions** | Intelligent, adaptive response selection |

The objective is to move cybersecurity from **passive detection** to **autonomous reasoning**, **decision making**, and **adaptive defense**.

---

## 🎯 Research Vision

BLACK VEIL investigates autonomous cyber defense architectures capable of:

- ✅ Understanding attack behavior and intent
- ✅ Computing dynamic trust in real-time
- ✅ Mutating credentials based on risk
- ✅ Learning continuously from attacks
- ✅ Deploying adaptive deception environments
- ✅ Executing intelligent security actions
- ✅ Preserving operational continuity under attack

---

## 🧠 Core Components

### 1. ACDO — Autonomous Cognitive Defense Orchestrator
Central reasoning engine that coordinates all defense components and makes autonomous decisions in real-time.

### 2. TTRM — Dynamic Trust Computation
Continuously evaluates trust using behavioral, contextual, and historical information. Trust isn't binary—it's a sliding scale that adapts.

### 3. DCMM — Dynamic Credential Mutation Model
Self-evolving credential management using genetic algorithms. Credentials mutate and strengthen based on risk assessment.

### 4. Reality Fabric — Adaptive Deception Infrastructure
Creates fake credentials, APIs, databases, and environments to trap and redirect attackers.

### 5. LAMG — Living Attack Memory Graph
Long-term attack memory that learns from every incident and evolves defense strategies.

### 6. Adaptive Security Actions Layer
Context-aware response selection including:
- 🔐 Dynamic Encryption
- 🔑 MFA Enforcement
- 🔄 Token Rotation
- 🔒 Credential Rotation
- 🌐 Network Isolation
- 🚫 Session Revocation
- 🎭 Deception Deployment
- 📡 Autonomous Recovery

---

## 🏗️ Architecture

BLACK VEIL consists of multiple intelligence layers working in harmony:



---

## 📊 Experimental Evaluation

### Benchmark Datasets
| Dataset | Samples | Features | Classes |
|---------|---------|----------|---------|
| **UNSW-NB15** | 82,332 | 43 | 2 |
| **CICIDS2017** | 2.5M | 78 | 4 |
| **EDGE-IIoT** | 2.8M | 21 | 2 |

### Model Performance Results
| Model | Dataset | Accuracy | F1-Score | AUC |
|-------|---------|----------|----------|-----|
| **XGBoost** | UNSW-NB15 | **100.00%** | **1.000** | **1.000** |
| **LightGBM** | EDGE-IIoT | **100.00%** | **1.000** | **1.000** |
| RandomForest | EDGE-IIoT | 95.18% | 0.9516 | 0.998 |
| RandomForest | CICIDS2017 | 86.94% | 0.8755 | 0.934 |

### Inference Latency
| Model | Inference Time |
|-------|----------------|
| LogisticRegression | **0.6ms** |
| LightGBM | 4.7ms |
| XGBoost | 41.6ms |
| RandomForest | 47.4ms |

### Evaluation Metrics
- ✅ Accuracy
- ✅ Precision
- ✅ Recall
- ✅ F1 Score
- ✅ ROC-AUC
- ✅ Confusion Matrix
- ✅ Inference Latency
- ✅ Throughput

> **Note:** Refer to the [IEEE Paper](BlackVeil_IEEE_2026_Journal_Final.pdf) for detailed experimental configuration and limitations.

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.13+
NVIDIA GPU (optional, recommended)
16GB+ RAM



# Clone repository
git clone https://github.com/shreekamesh/BLACK_VEIL.git
cd BLACK_VEIL

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt


# Start all services (API + Dashboard + Metrics)
./run.sh

# Check status
./status.sh

# Stop services
./stop.sh

# Restart services
./restart.sh


curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"model_name":"unsw_rf","features":[0.0]*43}'


Make a Prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"model_name":"unsw_rf","features":[0.0]*43}'



BLACK_VEIL/
├── src/
│   ├── core/
│   │   ├── cognitive/           # AI reasoning engine
│   │   ├── trust/               # TTRM implementation
│   │   ├── credential/          # DCMM implementation
│   │   ├── deception/           # Reality Fabric
│   │   ├── knowledge/           # LAMG implementation
│   │   ├── orchestrator/        # ACDO core
│   │   └── security/            # Encryption, hashing, key management
│   ├── backend/
│   │   ├── api/                 # FastAPI endpoints
│   │   ├── models/              # Database models
│   │   └── config/              # Configuration
│   └── frontend/                # Dashboard UI
├── models/                      # Trained models
├── datasets/                    # Raw datasets
├── master_dataset/              # Processed datasets
├── ieee_figures/                # Research paper figures
├── dashboard/                   # Monitoring dashboard
├── docs/                        # Documentation
├── deployment/                  # Docker/K8s deployment
├── papers/                      # Research papers
├── train_all_models.py          # Training script
├── inference_api.py             # API server
├── api_metrics.py               # Real-time metrics API
├── blackveil_client.py          # Python client
├── run.sh                       # Start all services
├── stop.sh                      # Stop all services
├── status.sh                    # Check service status
├── restart.sh                   # Restart services
├── requirements.txt             # Python dependencies
├── LICENSE                      # Apache 2.0 License
└── README.md                    # This file


🎯 Future Work
🔜 Federated Learning — Privacy-preserving collaborative learning

🔜 Multi-Agent AI — Decentralized autonomous defense

🔜 Quantum-Safe Security — Post-quantum cryptography

🔜 Edge AI — Lightweight models for edge deployment

🔜 Large Language Models — Enhanced threat intelligence

🔜 BLACK VEIL-X — Adaptive Reality Transformation Architecture (ARTA)

🔜 Real-time Data Flow Visualization — Traditional relay switching views


 Author
Shree Kamesh Kumar C D
Department of Artificial Intelligence and Data Science
Jai Shriram Engineering College
Avinashipalayam, Tirupur, Tamil Nadu, India
📧 Email: kameshkk43631@gmail.com
🔗 GitHub: @shreekamesh

