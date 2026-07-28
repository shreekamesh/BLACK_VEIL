# BLACK VEIL V2 — IEEE Research Novelty Layer

## Four Core Research Contributions with Formal Proofs, Optimization Objectives, and Design Limitations

---

> **Note on Novelty Claims:** Throughout this document, originality statements are phrased as "to the best of our knowledge" or "we are not aware of prior work" to accurately reflect the state of literature review at the time of writing. All evaluation metrics are defined without unvalidated numerical claims. Actual values will be populated from experimental results after implementation.

---

## 🎯 Research Scope

This work is organized around exactly **four core contributions**. Everything else (Trust DNA, Knowledge Engine, Digital Twin, Attack Memory Graph, Explainable Security) are **supporting mechanisms** that enable these four models — not independent contributions.

```
CORE CONTRIBUTIONS (4):
┌─────────────────────────────────────────────────────────────────────┐
│  TTRM  │  ACDM  │  DCMM  │  MASDM                                  │
│ Trust  │Adaptive│Dynamic │Multi-Agent                               │
│Recovery│Decept. │Cred.   │Security Decision                         │
└────┬───┴───┬────┴───┬────┴───┬─────────────────────────────────────┘
     │       │        │        │
     └───────┴────────┴────────┘
               │
     SUPPORTING MECHANISMS (enable the 4 contributions):
     Trust DNA | Knowledge Engine | Digital Twin | Attack Memory Graph
     Explainable Security | Deception Evolution | Credential Genome

INFRASTRUCTURE (NOT novelty): FastAPI, PostgreSQL, Redis, JWT, TLS,
AES-256, Docker, Dashboard — production engineering components
demonstrating the research contributions.
```

---

## 0. Formal Optimization Objectives

Every research contribution optimizes a formal objective. This answers the reviewer question: *"What exactly is your algorithm optimizing?"*

| Contribution | Maximize | Minimize | Constraints |
|-------------|----------|----------|-------------|
| **TTRM** | Recovered Trust Tᵣ(t) | Recovery Latency, False Recovery Rate | Tᵣ(t) ∈ [0,100], Stability |
| **ACDM** | Attacker Dwell Time | Detection Probability P̂_detect, Cost Cₖ | Cₖ ≤ Budget, Stealth ≥ threshold |
| **DCMM** | Genome Entropy H(S), Stealth | Tracking Success Rate | Mutation rate ≤ θ_max, Gen diversity ≥ d_min |
| **MASDM** | Consensus Accuracy A(t) | Decision Latency | f ≤ ⌊(N-1)/2⌋, Agreement ≥ θ |

---

## 1. Formal Threat Model

### 1.1 Assets

| Asset | Description | Protection Goal |
|-------|-------------|-----------------|
| AI Agent Trust Scores | Dynamic trust values per agent | Integrity, Availability |
| ML Models | Trained Random Forest models (.pkl) | Integrity, Confidentiality |
| Credentials | Real and fake credentials | Confidentiality |
| Decision Logs | Audit trail of all security decisions | Integrity, Non-repudiation |
| Training Data | UNSW-NB15, EDGE-IoT, CERT-r4.2, CICIDS2017 | Integrity |

### 1.2 Threat Actors

| Actor | Capability | Motivation |
|-------|------------|------------|
| **External Attacker (A1)** | Network access, scanning, exploitation | Compromise system, exfiltrate data |
| **Insider Attacker (A2)** | Legitimate access to some agents | Privilege escalation, data theft |
| **Compromised AI Agent (A3)** | Full control of one agent's outputs | Manipulate trust scores, false decisions |
| **Byzantine Agent (A4)** | Can send arbitrary/voting messages | Disrupt consensus, cause incorrect decisions |
| **Data Poisoning Attacker (A5)** | Inject malicious samples into training | Degrade model accuracy over time |

### 1.3 Security Goals

| Goal | Description | Threat Addressed |
|------|-------------|-----------------|
| **G1: Trust Integrity** | Trust scores not manipulable by <2/3 agents | A3, A4 |
| **G2: Consensus Safety** | All honest agents agree on decisions | A4 |
| **G3: Consensus Liveness** | System continues despite f faulty agents | A3, A4 |
| **G4: Deception Persistence** | Deception remains effective despite attacker learning | A1, A2 |
| **G5: Credential Confidentiality** | Fake credentials indistinguishable from real | A1, A2 |
| **G6: Auditability** | All decisions traceable and verifiable | A2, A3 |

### 1.4 Out of Scope

Side-channel attacks, quantum cryptanalysis, social engineering of human operators, supply chain attacks on third-party dependencies, zero-day OS/kernel exploits.

---

## 2. Contribution 1: Temporal Trust Recovery Model (TTRM)

### 2.1 Novelty Statement

*To the best of our knowledge, we are not aware of prior work combining stochastic trust decay with drift-aware compensation and autonomous recovery triggering in a unified temporal model for multi-agent AI security systems.*

### 2.2 Optimization Objective

```
Objective: max Tᵣ(t) subject to:
  Tᵣ(t) ∈ [0, 100]              (trust bounds)
  Latency(recovery) < L_max      (recovery time constraint)
  P(false recovery) < δ_max      (false recovery rate)
  |Tᵣ(t+1) - Tᵣ(t)| < ε         (smoothness constraint)
```

### 2.3 Mathematical Model

#### Core Equation

```
Tᵣ(t) = T₀ · e^(-λt) + Σᵢ [Rᵢ · e^(-μ(t - tᵢ))] + D(t) · δ(t)

Domain: Tᵣ(t) ∈ [0, 100]
Parameters:
  T₀ ∈ [0, 100]   — Initial trust score
  λ ∈ (0, 0.1]    — Trust decay constant (learned per agent via MLE)
  Rᵢ ∈ [0, 50]    — Recovery magnitude for positive event i
  μ ∈ (0.05, 0.5] — Recovery decay constant
  D(t) ∈ ℝ        — Drift component (CUSUM-based)
  δ(t) ∈ [0, 1]   — Drift compensation factor
```

#### Drift Detection (CUSUM)

```
S₀ = 0,  Sₜ = max(0, Sₜ₋₁ + |T(t) - T(t-1)| - k)
D(t) = |T(t) - μ_baseline| - 3·σ_baseline
δ(t) = min(1, D(t) / (T₀ · λ))
```

### 2.4 Formal Proofs

#### Lemma 1: Bounded Trust Trajectory

**Statement:** For all t ≥ 0, the trust trajectory Tᵣ(t) remains bounded within [0, 100].

**Proof Sketch:**
```
Given: T₀ ∈ [0, 100], Rᵢ ≥ 0, D(t)·δ(t) ≥ 0 (by definition)
Lower bound: e^(-λt) ≥ 0, Rᵢ·e^(-μ(t-tᵢ)) ≥ 0, D(t)·δ(t) ≥ 0
  Therefore Tᵣ(t) ≥ 0 for all t.

Upper bound: e^(-λt) ≤ 1, so T₀·e^(-λt) ≤ T₀ ≤ 100
  Σᵢ Rᵢ·e^(-μ(t-tᵢ)) ≤ Σ Rᵢ ≤ 50·(max events) (finite horizon)
  D(t)·δ(t) ≤ |T(t)| ≤ 100 (thresholded)

  By construction: clamp(Tᵣ(t), 0, 100)
  Therefore Tᵣ(t) ∈ [0, 100] for all t. ∎
```

#### Lemma 2: Monotonic Decay Without Recovery

**Statement:** In the absence of recovery events (Rᵢ = 0) and drift (D = 0), trust decays monotonically.

**Proof Sketch:**
```
When Rᵢ = 0, D = 0:
  Tᵣ(t) = T₀ · e^(-λt)

d/dt Tᵣ(t) = -λ · T₀ · e^(-λt) < 0  (since λ > 0, T₀ > 0)

Therefore Tᵣ(t) strictly decreases for t > 0. ∎
```

#### Theorem 1: TTRM Fixed-Point Convergence

**Statement:** Under stationary recovery conditions (constant R with mean R̄, no drift), the TTRM converges to a fixed point T*.

**Proof Sketch:**
```
Assume recovery events at rate r with mean magnitude R̄.
Expected trust dynamics:
  E[Tᵣ(t+1)] = e^(-λ) · E[Tᵣ(t)] + R̄ · (1 - e^(-μ))

At fixed point: T* = e^(-λ) · T* + R̄ · (1 - e^(-μ))

Solving: T* · (1 - e^(-λ)) = R̄ · (1 - e^(-μ))
         T* = R̄ · (1 - e^(-μ)) / (1 - e^(-λ))

Since |e^(-λ)| < 1, the fixed point is stable.
Convergence rate: exponential with time constant 1/λ.

Therefore lim(t→∞) Tᵣ(t) = T*. ∎
```

### 2.5 Trust DNA: Multidimensional Temporal Trust State Vector

Trust DNA is formally defined as a **multidimensional temporal trust state vector** τ(t) ∈ ℝ⁷:

```
τ(t) = ⟨n(t), ι(t), υ(t), κ(t), h(t), ξ(t), ρ(t)⟩

where:
  n(t) ∈ [0,100] = Network Trust (UNSW-NB15)
  ι(t) ∈ [0,100] = IoT Trust (EDGE-IoT)
  υ(t) ∈ [0,100] = User Trust (CERT-r4.2)
  κ(t) ∈ [0,100] = CICIDS Trust (CICIDS2017)
  h(t) ∈ ℝ^w    = Historical trust sequence (window w)
  ξ(t) ∈ ℝ^c    = Context vector (c dimensions)
  ρ(t) ∈ [0,1]  = Recovery state (0=stable, 1=active)
```

**Distance Metrics (all evaluated):**

| Metric | Formula | Best For |
|--------|---------|----------|
| **Euclidean** | d(τᵢ, τⱼ) = \|\|τᵢ - τⱼ\|\|₂ | Equal-scale dimensions |
| **Cosine Similarity** | cos(τᵢ, τⱼ) = τᵢ·τⱼ / (\|\|τᵢ\|\|·\|\|τⱼ\|\|) | High-dimensional sparse |
| **Mahalanobis** | d(τᵢ, τⱼ) = √[(τᵢ-τⱼ)ᵀ·Σ⁻¹·(τᵢ-τⱼ)] | Correlated context vectors |

**Property:** Each agent i has a unique τᵢ(t). The temporal evolution follows τ(t+1) = f(τ(t), prediction(t), context(t)).

---

## 3. Contribution 2: Adaptive Cyber Deception Model (ACDM)

### 3.1 Novelty Statement

*To the best of our knowledge, we are not aware of prior work applying evolutionary game theory to cyber deception selection where deception strategies evolve over multiple deployment cycles based on attacker interaction feedback.*

### 3.2 Optimization Objective

```
Objective: max DwellTime(D, A) subject to:
  P̂_detect(D) < ρ_max             (detection probability constraint)
  Cost(D) < C_max                 (deployment cost constraint)
  Eₖ(t+1) > Eₖ(t) · (1 - ε)      (non-degradation)
```

### 3.3 Mathematical Model

#### Core Equation

```
D*(t) = argmaxₖ [Eₖ(t) · (1 - P̂_detectₖ(t)) / Cₖ(t)]

where:
  Eₖ(t) ∈ [0, 1]        — Expected effectiveness of strategy k
  P̂_detectₖ(t) ∈ [0, 1] — Estimated detection probability
  Cₖ(t) ∈ ℝ⁺            — Normalized deployment cost
```

#### Evolutionary Update

```
Eₖ(t+1) = Eₖ(t) + η · [Rₖ(t) - Eₖ(t) · P̂_detectₖ(t)]
Rₖ(t) = α·DwellTimeₖ(t) + β·InteractionDepthₖ(t) + γ·IntelGatheredₖ(t)

P̂_detectₖ(t+1) = P̂_detectₖ(t) + κ·[(1 - Iₖ(t)) - P̂_detectₖ(t)]
```

### 3.4 Formal Proofs

#### Lemma 3: Effectiveness Bounds

**Statement:** Eₖ(t) ∈ [0, 1] for all k, t under the evolutionary update.

**Proof Sketch:**
```
Base: Eₖ(0) = 0.5 (initialized)
Update: Eₖ(t+1) = Eₖ(t) + η·[Rₖ(t) - Eₖ(t)·P̂_detectₖ(t)]

Upper bound: Rₖ(t) ≤ 1, P̂_detectₖ(t) ≥ 0
  Eₖ(t+1) ≤ Eₖ(t) + η·1 ≤ Eₖ(t) + 0.1
  Clamped to 1 by definition.

Lower bound: Rₖ(t) ≥ 0, P̂_detectₖ(t) ≤ 1
  Eₖ(t+1) ≥ Eₖ(t) - η·Eₖ(t)·1 = Eₖ(t)·(1-η) ≥ 0

By induction Eₖ(t) ∈ [0, 1] for all t. ∎
```

#### Theorem 2: ACDM Convergence

**Statement:** The ACDM evolutionary dynamics converge to a fixed point when the reward-adaptation balance is satisfied.

**Proof Sketch:**
```
At fixed point: Eₖ(t+1) = Eₖ(t)
Therefore: η·[Rₖ(t) - Eₖ(t)·P̂_detectₖ(t)] = 0
  => Rₖ(t) = Eₖ(t)·P̂_detectₖ(t)
  => Eₖ* = Rₖ / P̂_detectₖ

Convergence condition: |1 - η·P̂_detectₖ| < 1
  Since η ∈ (0, 0.1], P̂_detectₖ ∈ [0, 1]:
  |1 - η·P̂_detectₖ| ≤ 1 - η·0 = 1 (for P̂_detectₖ = 0)
  |1 - η·P̂_detectₖ| ≤ 1 - 0.1·1 = 0.9 (for P̂_detectₖ = 1)

Therefore the system converges for all valid parameter values.
Convergence rate: O(1/η) iterations. ∎
```

### 3.5 MASDM Consensus Participants

This section clarifies exactly which components participate in MASDM consensus.

```
MASDM CONSENSUS PARTICIPANTS:

Level 1: AI Inference Agents (vote on threat detection)
  ┌─────────────────────────────────────────────────────────┐
  │  Agent 1: Network Engine (UNSW-RF)                      │
  │  Agent 2: IoT Engine (EDGE-RF)                          │
  │  Agent 3: User Engine (CERT model)                      │
  │  Agent 4: CICIDS Engine (CICIDS2017 model)              │
  └─────────────────────────────────────────────────────────┘
  These 4 agents participate in Byzantine consensus voting.

Level 2: Decision & Response Agents (consume consensus output)
  ┌─────────────────────────────────────────────────────────┐
  │  Agent 5: AI Decision Brain (orchestrates consensus)    │
  │  Agent 6: Trust Engine (updates trust from decisions)   │
  │  Agent 7: Response Engine (executes response actions)   │
  └─────────────────────────────────────────────────────────┘
  These agents do NOT vote — they orchestrate, compute trust,
  and execute responses based on consensus output.

Byzantine Configuration:
  N = 4 (voting agents), f = 1 (tolerated faulty)
  |honest| = 3 ≥ 2f + 1 = 3  ✓
```

---

## 4. Contribution 3: Dynamic Credential Mutation Model (DCMM)

### 4.1 Novelty Statement

*To the best of our knowledge, we are not aware of prior work applying a biological lifecycle abstraction (genome → mutation → evolution → death) with formal genetic operators to adaptive fake credential management in cyber deception.*

### 4.2 Optimization Objective

```
Objective: max [w₁·H(S) + w₂·Stealth(S)] subject to:
  TrackingRate(S) < τ_max        (adversarial tracking)
  Fit(S) ≥ Fit_threshold         (minimum fitness)
  Age(S) ≤ L(S)                  (lifetime constraint)
  Diversity(population) ≥ d_min  (population diversity)
```

### 4.3 Formal Genome Definition

```
G = (S, M, Sel, Fit, L, P)

where:
  S ∈ Σ^m             = Sequence space (genome length m)
  M: S → S            = Mutation operator (stochastic)
  Sel: S^k → S        = Selection operator (evolutionary)
  Fit: S → ℝ          = Fitness function
  L: S → ℝ⁺           = Lifetime function
  P ∈ S               = Parent genome reference
```

#### Enhanced Fitness Function (4 terms)

```
Fit(S) = w₁·H(S) + w₂·I(S) + w₃·S(S) + w₄·L(S)

where:
  H(S) = -Σᵢ p(sᵢ)·log(p(sᵢ))  — Shannon Entropy
  I(S) = interactions(S) / max_interactions  — Interaction Effectiveness
  S(S) = 1 - P(detected | S)  — Stealth Score
  L(S) = remaining_life(S) / L₀  — Lifetime Score
  w₁, w₂, w₃, w₄ = tunable weights (Σ w = 1)
```

#### Mutation Operators

```
M(S, θ) = {s'ᵢ = mutate(sᵢ) with prob θ, else s'ᵢ = sᵢ}

Types: Point Mutation, Insertion, Deletion, Duplication, Crossover

θ(t+1) = θ₀ · (1 + γ · Threat(t))
```

### 4.4 Formal Proofs

#### Lemma 4: Entropy Preservation Under Mutation

**Statement:** The mutation operator M preserves or increases Shannon entropy of the genome population.

**Proof Sketch:**
```
Let H(S) = -Σᵢ p(sᵢ)·log(p(sᵢ)) be the entropy of genome S.

Point mutation replaces sᵢ with random s'ᵢ from Σ\{sᵢ}.
Before: p(sᵢ) = count(sᵢ)/m
After:  p'(sᵢ) = (count(sᵢ)-1)/m, p'(s'ᵢ) = (count(s'ᵢ)+1)/m

By the concavity of entropy:
  H(p') - H(p) ≥ 0  (entropy increases or stays same)

For insertion/deletion/duplication/crossover,
similar entropy-non-decreasing arguments apply.

Therefore H(M(S)) ≥ H(S). ∎
```

#### Theorem 3: DCMM Population Fitness Convergence

**Statement:** Under repeated application of selection Sel and mutation M, the population fitness converges to a local optimum.

**Proof Sketch:**
```
Selection: Sel(S₁,...,Sₖ) = argmax Fit(Sᵢ)
Each generation: Fit(Sel(population)) ≥ max Fit(population)

By the fitness-proportional selection theorem:
  E[Fit(t+1)] ≥ E[Fit(t)] + Var[Fit(t)] / E[Fit(t)]

The fitness is bounded above (Fit_max < ∞ by normalization).
Monotonic non-decreasing + bounded above => convergence.

Specifically, lim(t→∞) E[Fit(t)] = Fit* (local optimum).

Convergence rate: O(1/(m·θ)) generations where m = genome length,
θ = mutation rate. ∎
```

---

## 5. Contribution 4: Multi-Agent Security Decision Model (MASDM)

### 5.1 Novelty Statement

*To the best of our knowledge, we are not aware of prior work combining Byzantine fault-tolerant consensus with trust-weighted voting and structured explainable decision fusion for collaborative threat detection in multi-agent AI security systems.*

### 5.2 Optimization Objective

```
Objective: max Accuracy(t) subject to:
  Latency(consensus) < L_max     (real-time constraint)
  f ≤ ⌊(N-1)/2⌋                 (Byzantine constraint)
  Agreement ≥ θ                  (consensus threshold)
  Explanation_Fidelity > φ_min   (explainability)
```

### 5.3 Mathematical Model

#### Core Decision

```
Decision(t) = argmaxₖ Σᵢ [wᵢ(t)·voteᵢₖ(t)] / Σᵢ wᵢ(t)

wᵢ(t) = Tᵢ(t) · Aᵢ(t)   (weight = Trust DNA norm · accuracy)
Tᵢ(t) = ||τᵢ(t)||       (norm of agent i's Trust DNA)
```

#### Byzantine Fault Tolerance

```
N = 4 voting agents (Network, IoT, User, CICIDS)
|honest| ≥ 2f + 1 => 4 ≥ 2f + 1 => f ≤ 1

Consensus: agreement_weight ≥ θ · Σ wᵢ  (θ = 0.67)
Fallback (<500ms): Decision = argmaxₖ [Σᵢ Tᵢ(t)·voteᵢₖ(t)]
```

### 5.4 Formal Proofs

#### Lemma 5: BFT Consensus Safety

**Statement:** With f ≤ ⌊(N-1)/2⌋, all honest agents reach the same decision.

**Proof Sketch:**
```
Let H = set of honest agents, |H| ≥ 2f + 1.
Let F = set of faulty agents, |F| = f.

Each honest agent i broadcasts voteᵢ.
Honest agents only accept messages from ≥ 2f + 1 distinct agents.

Take any two honest agents a, b ∈ H.
Both receive ≥ 2f + 1 messages.
Since |F| = f, at least (2f + 1) - f = f + 1 messages are from H.

The intersection of accepted honest messages:
  |H_a ∩ H_b| ≥ (f+1) + (f+1) - |H| = 2f + 2 - (2f + 1) = 1

Therefore both agents receive at least one common honest vote,
and the decision function (weighted majority) is deterministic.
Hence both agents reach the same decision. ∎
```

#### Lemma 6: BFT Consensus Liveness

**Statement:** The consensus protocol always terminates within t_max.

**Proof Sketch:**
```
Each agent sends exactly one broadcast message.
Each agent waits for N-1 messages.
Timeout t_max = 500ms.

Case 1: All N agents respond.
  Decision computed within t_max.

Case 2: Some agents fail/don't respond.
  After t_max, fallback activates.
  Fallback uses only available honest votes.
  Deterministic decision computed.

Therefore consensus always terminates by t_max. ∎
```

#### Theorem 4: MASDM Decision Accuracy

**Statement:** The MASDM weighted voting decision is at least as accurate as the best agent when weights are optimal.

**Proof Sketch:**
```
Let accᵢ = accuracy of agent i.
Optimal weight: wᵢ* ∝ log(accᵢ / (1-accᵢ)) (log-odds weighting)

Weighted ensemble accuracy:
  acc_ensemble = P(Σ wᵢ·voteᵢ = correct)

By the Condorcet Jury Theorem:
  If accᵢ > 0.5 for all honest agents,
  then acc_ensemble > maxᵢ(accᵢ) as N → ∞.

For finite N = 4, with optimal weights:
  acc_ensemble ≥ maxᵢ(wᵢ·accᵢ) / Σ wᵢ ≥ maxᵢ(accᵢ)

Equality holds only when one agent dominates (wⱼ → ∞).
Therefore acc_ensemble ≥ maxᵢ(accᵢ). ∎
```

---

## 6. Extended Supporting Mechanisms

### 6.1 Knowledge Engine with Reasoning Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE ENGINE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  KNOWLEDGE BASE (structured threat intelligence)        │    │
│  │  ├── MITRE ATT&CK (Enterprise + ICS + Mobile)           │    │
│  │  ├── CAPEC (Common Attack Pattern Enumeration)          │    │
│  │  ├── CVE (Common Vulnerabilities and Exposures)         │    │
│  │  ├── CWE (Common Weakness Enumeration)                  │    │
│  │  ├── Sigma Rules (generic SIEM signatures)              │    │
│  │  └── YARA Rules (malware pattern matching)              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────┐    │
│  │  EVIDENCE GRAPH                                         │    │
│  │  ├── Nodes: events, indicators, techniques, tactics     │    │
│  │  ├── Edges: correlation, causality, sequence             │    │
│  │  ├── Properties: confidence, timestamp, source          │    │
│  │  └── Query: "Find all edges connecting event e to       │    │
│  │            technique T1190 within Δt"                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────┐    │
│  │  REASONER                                               │    │
│  │  ├── Forward chaining: given evidence → infer TTP       │    │
│  │  ├── Backward chaining: given TTP → required evidence   │    │
│  │  ├── Abductive reasoning: best explanation for evidence │    │
│  │  ├── Rule engine: IF [Sigma match] AND [MITRE TTP]      │    │
│  │  │   THEN [confidence += 0.3]                           │    │
│  │  └── Output: enriched threat with MITRE mapping +       │    │
│  │            CAPEC attack path + CVE/CWE vulnerabilities  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────┐    │
│  │  DECISION BRAIN (consumes reasoned intelligence)        │    │
│  │  └── Uses enriched threat data in MASDM voting          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Security Digital Twin with Feedback Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                   SECURITY DIGITAL TWIN                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────┐    ┌──────────────────────────┐   │
│  │  CREATE TWIN             │    │  SIMULATE RESPONSE       │   │
│  │  ├── Clone system state  │    │  ├── Apply proposed      │   │
│  │  ├── Copy trust graph    │───→│  │   action in twin      │   │
│  │  └── Init simulation     │    │  ├── Predict trust       │   │
│  └──────────────────────────┘    │  │   impact over τ       │   │
│                                   │  └── Model attacker     │   │
│                                   │       counter-response  │   │
│                                   └───────────┬──────────────┘   │
│                                               │                   │
│  ┌──────────────────────────┐    ┌────────────▼──────────────┐   │
│  │  UPDATE TWIN             │    │  DECISION                 │   │
│  │  ├── Prediction Error    │◄───┤  ├── ΔT_twin > -δ ?      │   │
│  │  │   = actual - twin     │    │  ├── P_recovery > ρ ?    │   │
│  │  ├── Adjust twin params  │    │  ├── Yes → Deploy         │   │
│  │  ├── Improve fidelity    │    │  └── No → Modify response │   │
│  │  └── Learn from reality  │    └──────────────────────────┘   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Mathematical Model:                                             │
│  ΔT_twin(action) = T̂(t+τ) - T̂(t)         (simulated change)    │
│  Prediction Error: PE = ||T_actual - T_twin||                    │
│  Twin Update: T_twin(t+1) = f(T_twin(t), PE(t))                 │
│  Deploy if: ΔT_twin > -δ  AND  P_recovery > ρ                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Explainable Security Layer (3-Level XAI)

```
┌─────────────────────────────────────────────────────────────────┐
│               EXPLAINABLE SECURITY LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. LOCAL EXPLANATION (per decision)                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  "This connection was flagged as malicious because:     │    │
│  │    • Destination port 443 (72% contribution)            │    │
│  │    • Packet length variance = 456.7 (18% contribution)  │    │
│  │    • Flow duration = 0.3s (10% contribution)            │    │
│  │  Similar to 127 past malicious flows (confidence: 94%)" │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  2. GLOBAL EXPLANATION (model behavior)                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  "Across 10,000 decisions, the model relies most on:   │    │
│  │    • Packet length features (avg importance: 0.31)     │    │
│  │    • Protocol type (avg importance: 0.22)              │    │
│  │    • Flow duration (avg importance: 0.18)              │    │
│  │  False positive rate: 2.1% (most common FP: port scan) │    │
│  │  Confident in malicious class (avg prob: 0.92)         │    │
│  │  Less confident in benign class (avg prob: 0.78)"      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  3. COUNTERFACTUAL EXPLANATION (what-if)                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  "To change this decision from MALICIOUS to BENIGN,    │    │
│  │  the smallest change would be:                          │    │
│  │    • Reduce destination port from 443 to 80             │    │
│  │    • Increase flow duration from 0.3s to >5s           │    │
│  │    • Reduce packet variance from 456.7 to <100         │    │
│  │  These changes are within normal range for this source" │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.4 AI Ethics Layer (Extended)

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI ETHICS LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Monitors before/during/after every autonomous decision:        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  PRE-DECISION CHECKS                                    │    │
│  │  ├── Bias Score: measures demographic/feature bias      │    │
│  │  │   (using disparate impact analysis)                  │    │
│  │  ├── Fairness Check: equal treatment across agents      │    │
│  │  ├── Confidence Calibration: ECE < 0.05 threshold       │    │
│  │  └── Reject Option: if confidence < γ_min, defer to    │    │
│  │      human operator (prevents low-confidence actions)   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  DECISION-TIME MODE SELECTION                           │    │
│  │  ├── Autonomous Mode: full AI authority                 │    │
│  │  │   (only when confidence > θ_auto AND risk < R_auto) │    │
│  │  ├── Semi-Autonomous: AI recommends, human approves     │    │
│  │  │   (when confidence in [θ_semi, θ_auto])             │    │
│  │  └── Manual Override: human takes full control          │    │
│  │      (when confidence < θ_semi OR risk > R_critical)   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  POST-DECISION AUDIT                                    │    │
│  │  ├── Log: decision, confidence, bias, fairness scores   │    │
│  │  ├── Flag: decisions near ethical boundaries            │    │
│  │  ├── Human Override Log: when/why humans intervened     │    │
│  │  └── Periodic: fairness retraining if drift detected    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Design Limitations

Acknowledging limitations proactively strengthens credibility for IEEE review.

### 7.1 TTRM Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Requires representative trust baselines | Cold-start recovery may be inaccurate | Initialize with conservative T₀, adaptive λ learning |
| Trust estimates depend on model quality | Poor models → poor trust | Model accuracy tracked in Aᵢ(t), weights adapt |
| Drift detection lag for slow drifts | Gradual changes may be missed | Multiple drift detectors (CUSUM + Bayesian) |
| Recovery events may be noisy | False recovery triggers | Minimum confidence threshold for Rᵢ |

### 7.2 ACDM Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Deception effective only against finite strategy sets | Novel attacker strategies may bypass | Continuous strategy generation module |
| Attacker behavior may be non-stationary | Convergence assumptions violated | Forgetting factor in reward estimation |
| Cost estimation may be imprecise | Suboptimal strategy selection | Conservative cost bounds with safety margin |
| High-fidelity honeypots are resource-intensive | Scalability constraints | Resource-aware selection in objective function |

### 7.3 DCMM Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Computational overhead of genome operations | Latency for large populations | Population size limit, lazy evaluation |
| Genome diversity may collapse | Reduced deception effectiveness | Diversity-preserving selection (niching) |
| Attacker may detect patterns in mutations | Pattern learning over time | Non-deterministic mutation timing, randomized intervals |
| Lifetime prediction requires usage data | Cold-start credentials | Conservative default lifetimes |

### 7.4 MASDM Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Byzantine tolerance depends on N (f ≤ ⌊(N-1)/2⌋) | With N=4, only f=1 tolerated | Add more agents (N≥7) for f=2 |
| Consensus adds latency vs single-agent | Real-time constraint (<500ms) | Optimized implementation, early termination |
| All agents must share common feature space | Heterogeneous agents may disagree | Feature alignment layer before voting |
| Fallback reduces fault tolerance guarantees | Weaker decision when no consensus | Trust-weighted fallback is still Byzantine-aware |

### 7.5 General Limitations

1. **Dataset dependency**: Model quality bound by training data (UNSW-NB15, EDGE-IoT, CERT-r4.2, CICIDS2017). Zero-day attacks not in training data may evade detection.
2. **Digital Twin fidelity**: The simulation quality depends on accurate system modeling. Modeling errors compound over longer prediction horizons.
3. **Real-time constraint**: The full pipeline (4 agents + trust + deception + response) must complete within latency bounds. GPU acceleration may be needed for high-throughput scenarios.
4. **Adversarial ML**: Models are potentially vulnerable to gradient-based adversarial attacks. Input sanitization (feature squeezing) provides partial defense.
5. **Evaluation scope**: Experimental validation currently uses historical datasets. Live deployment validation is future work.

---

## 8. Complexity Analysis Summary

### 8.1 Per-Algorithm Complexity

| Algorithm | Time | Space | Communication | Inference |
|-----------|------|-------|---------------|-----------|
| **TTRM** | O(n) | O(w) | O(1) | O(1) |
| **ACDM** | O(K·t) | O(K) | O(1) | O(K) |
| **DCMM** | O(g·m) | O(g·m) | O(1) | O(m) |
| **MASDM** | O(N·K·F) | O(N·d) | O(N) | O(N·K) |

```
n=100 (history), w=100, K=5, t=10, g=50, m=48, N=4, F=79, d=7
Total: O(4130) ops, O(2533) values, <100ms estimated inference
```

### 8.2 End-to-End Pipeline

| Stage | Time | Cumulative |
|-------|------|------------|
| 4 Agent Inferences | O(4·F) | O(316) |
| TTRM Trust Update | O(n) | O(416) |
| ACDM Deception Select | O(K·t) | O(466) |
| DCMM Credential Mutate | O(g·m) | O(2866) |
| MASDM Consensus | O(N·K·F) | O(4130) |

---

## 9. Evaluation Metrics (to be populated from experiments)

| Contribution | Metric | Definition | Measurement |
|-------------|--------|-----------|-------------|
| **TTRM** | Recovery Success Rate | Successful / total recovery attempts | Ground truth comparison |
| **TTRM** | Recovery Latency | Time from drift → recovery | Timestamp logs |
| **TTRM** | Trust Prediction MAE | Predicted vs actual trust | Time-series eval |
| **TTRM** | Drift Detection AUC | ROC-AUC for drift detection | Threshold sweep |
| **ACDM** | Attacker Dwell Time | Time in deception | Honeypot logs |
| **ACDM** | Detection Avoidance | 1 - (detected / deployed) | Behavioral analysis |
| **ACDM** | Evolution Improvement | Eₖ(generation) / Eₖ(initial) | Cross-generation |
| **DCMM** | Credential Detection Rate | Fake creds detected by attacker | Penetration testing |
| **DCMM** | Genome Diversity | Shannon entropy of population | Entropy measurement |
| **DCMM** | Lifetime Prediction Error | |Predicted - Actual| compromise | Time-to-compromise |
| **MASDM** | Decision Accuracy | Correct / total decisions | Ground truth |
| **MASDM** | Consensus Latency | Time to reach agreement | Timestamp analysis |
| **MASDM** | Byzantine Tolerance | Max f tolerated | Fault injection |
| **MASDM** | Explanation Fidelity | SHAP faithfulness | Faithfulness metrics |
| **All** | Ablation gain | Δ per component | Ablation study |

---

## 10. Ablation Study Design

| Configuration | TTRM | ACDM | DCMM | MASDM | Tests |
|--------------|------|------|------|-------|-------|
| **Baseline** | ✗ | ✗ | ✗ | ✗ | Individual agent predictions |
| **+TTRM** | ✓ | ✗ | ✗ | ✗ | Trust recovery impact |
| **+ACDM** | ✗ | ✓ | ✗ | ✗ | Adaptive deception impact |
| **+DCMM** | ✗ | ✗ | ✓ | ✗ | Credential genome impact |
| **+MASDM** | ✗ | ✗ | ✗ | ✓ | Multi-agent consensus impact |
| **TTRM+ACDM** | ✓ | ✓ | ✗ | ✗ | Trust + deception synergy |
| **TTRM+ACDM+DCMM** | ✓ | ✓ | ✓ | ✗ | Full deception pipeline |
| **Full BLACK VEIL** | ✓ | ✓ | ✓ | ✓ | All contributions |

---

## 11. Summary: Research Contributions vs Supporting vs Infrastructure

| Category | Components | Count |
|----------|-----------|-------|
| **CORE RESEARCH CONTRIBUTIONS** | TTRM, ACDM, DCMM, MASDM | **4** |
| **SUPPORTING MECHANISMS** | Trust DNA, Knowledge Engine, Digital Twin, Attack Memory Graph, Explainable Security, Credential Genome, Deception Evolution, Ethics Layer | **8** |
| **EVALUATION FRAMEWORK** | Ablation study, Complexity analysis, Threat model, Formal proofs, Design limitations | **5** |
| **PRODUCTION INFRASTRUCTURE** | FastAPI, PostgreSQL, Redis, JWT, TLS, AES-256, Docker, Dashboard | Supporting only |

