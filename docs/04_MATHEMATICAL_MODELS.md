# BLACK VEIL V2 — Mathematical Models

## IEEE Research Mathematical Foundation

---

## 1. Trust Computation Model

### Core Trust Formula
```
T(t) = α·N(t) + β·I(t) + γ·U(t) + δ·C(t)

where:
  T(t) = Composite Trust Score at time t
  N(t) = Network Trust Score (UNSW-NB15)
  I(t) = IoT Trust Score (EDGE-IoT)
  U(t) = User Trust Score (CERT-r4.2)
  C(t) = CICIDS Trust Score (CICIDS2017)
  α + β + γ + δ = 1  (weight normalization)
```

### Weight Adaptation
```
α(t+1) = α(t) × [1 + η × (Acc_N(t) - T̄(t))]

where:
  η = learning rate
  Acc_N(t) = Network model accuracy at time t
  T̄(t) = average trust across all domains at time t
```

---

## 2. Temporal Trust Recovery Model

### Exponential Decay with Recovery
```
T(t) = T₀·e^(-λt) + Σᵢ Rᵢ·e^(-μ(t-tᵢ))

Parameters:
  λ = Trust decay constant (0.01 - 0.1)
  μ = Recovery decay constant (0.05 - 0.5)
  Rᵢ = Recovery magnitude at event i
  tᵢ = Time of recovery event i
```

### Recovery Probability
```
P_recovery(t) = 1 / [1 + e^(-k(t - t₀))]

where:
  k = recovery rate
  t₀ = inflection point
```

---

## 3. Threat Correlation Model

### Correlation Score
```
C(eᵢ, eⱼ) = w₁·time_sim(eᵢ, eⱼ) + w₂·spatial_sim(eᵢ, eⱼ) + w₃·type_sim(eᵢ, eⱼ)

time_sim = e^(-|tᵢ - tⱼ| / τ)
spatial_sim = 1 / (1 + ||pᵢ - pⱼ||²)
type_sim = δ(typeᵢ, typeⱼ)  // Kronecker delta
```

### Cluster Confidence
```
Conf(C) = Σᵢⱼ C(eᵢ, eⱼ) / |C|² × [1 - H(C)]

where:
  H(C) = entropy of cluster C
  |C| = number of events in cluster
```

---

## 4. Deception Effectiveness Model

### Deception Success Probability
```
P_success(D, A) = σ(β₀ + β₁·Realism(D) + β₂·Luring(D) - β₃·DetectionRisk(D))

where:
  σ(x) = 1 / (1 + e^(-x))  // sigmoid
  Realism(D) = how realistic deception D appears
  Luring(D) = how attractive deception D is to attacker A
  DetectionRisk(D) = risk of deception being detected
```

### Optimal Deployment Timing
```
t* = argmax_t [P_success(D, A, t) × Impact(D, t) - Cost(D, t)]
```

---

## 5. Risk Assessment Model

### Composite Risk Index
```
RI(t) = Σᵢ wᵢ × fᵢ(t)

where:
  f₁(t) = 1 - T(t)/100  (trust inverse)
  f₂(t) = Σ Threat_Severity × e^(-κΔt)  (threat accumulation)
  f₃(t) = Vulnerability_Score(t)  (system vulnerabilities)
  f₄(t) = Anomaly_Score(t)  (behavioral anomalies)
```

### Risk Classification
```
Risk Level = {
    LOW:        RI ∈ [0, 25)
    MEDIUM:     RI ∈ [25, 50)
    HIGH:       RI ∈ [50, 75)
    CRITICAL:   RI ∈ [75, 100]
}
```

---

## 6. Adaptive Credential Mutation Model

### Mutation Timing
```
T_mutate = T_base × [1 + α × (1 - Threat_Level) - β × Usage_Frequency]

where:
  T_base = base mutation interval
  α = threat level sensitivity
  β = usage frequency sensitivity
```

### Credential Strength Evolution
```
S(t+1) = S(t) + ΔS × (1 - S(t)/S_max)

where:
  S(t) = credential strength at time t
  ΔS = strength increment per mutation
  S_max = maximum credential strength
```

---

## 7. Multi-Agent Consensus Model

### Byzantine Fault Tolerance
```
Consensus = median(weighted_votes) if |agreement| ≥ 2f + 1

where:
  f = maximum number of faulty/malicious agents
  N = total agents = 3f + 1 (minimum for BFT)
```

### Weighted Voting
```
Vote_Weight(i) = Tᵢ(t) × Accᵢ(t) × Relᵢ(t)
Final_Decision = argmaxₖ Σᵢ Vote_Weight(i) × δ(voteᵢ, k)
```

---

## 8. Explainable Trust Model (SHAP-based)

### Feature Contribution
```
φⱼ(f) = Σₛ⊆F\{j} [|s|!(|F|-|s|-1)!/|F|!] × [fₓ(S∪{j}) - fₓ(S)]

where:
  φⱼ(f) = Shapley value for feature j in model f
  F = set of all features
  S = subset of features
  fₓ(S) = model prediction using subset S
```

### Trust Decomposition
```
Trust_Explanation = Σⱼ φⱼ × featureⱼ + φ₀

where:
  φ₀ = baseline (expected) trust score
  φⱼ = contribution of feature j
  featureⱼ = normalized feature value
```

---

## 9. Temporal Drift Detection Model

### CUSUM Drift Detection
```
Sₜ = max(0, Sₜ₋₁ + Tₜ - Tₜ₋₁ - k)
Alarm if Sₜ > h

where:
  S₀ = 0
  k = allowance (slack parameter)
  h = decision threshold
  Tₜ = trust score at time t
```

### Bayesian Change Point
```
P(CP at t | Data) = P(Data | CP at t) × P(CP) / P(Data)

P(Data | CP at t) = Πᵢ<ᵗ P(xᵢ | θ₁) × Πᵢ≥ᵗ P(xᵢ | θ₂)

where:
  CP = change point
  θ₁ = distribution parameters before change
  θ₂ = distribution parameters after change
```

---

## 10. Response Optimization Model

### Response Selection
```
R* = argmin_R [Cost(R) + Expected_Damage(R) + Recovery_Time(R)]

Expected_Damage(R) = P(Threat | Evidence) × Damage(Threat) × (1 - Effectiveness(R))
```

### Response Effectiveness
```
Eff(R, T) = α × Block_Rate(R, T) + β × Containment_Time(R, T) + γ × Recovery_Quality(R, T)

where:
  α + β + γ = 1
  Block_Rate = fraction of threat actions blocked
  Containment_Time = time to contain threat
  Recovery_Quality = quality of system recovery after response
```

---

## 11. Fusion Ensemble Model

### Weighted Soft Voting
```
P(Class = k | Models) = Σᵢ wᵢ × Pᵢ(Class = k)

where:
  Pᵢ(Class = k) = probability from model i for class k
  wᵢ = weight of model i (Σ wᵢ = 1)
```

### Entropy-based Confidence
```
Confidence = 1 - H(P) / log(K)

H(P) = -Σₖ Pₖ × log(Pₖ)

where:
  H(P) = entropy of prediction distribution
  K = number of classes
  Pₖ = probability of class k
```

---

## 12. Resource Optimization Model

### Cost Function
```
Cost(actions, t) = Σᵢ [C_compute(i,t) + C_storage(i,t) + C_network(i,t)]

where:
  C_compute = computational cost of action i
  C_storage = storage cost of action i
  C_network = network bandwidth cost of action i
```

### Budget Constraint
```
Σᵢ Cost(i, t) ≤ Budget(t) subject to:
  Σᵢ Security_Benefit(i, t) ≥ Min_Security(t)
```

---

## Summary of Mathematical Constants

| Parameter | Value | Description |
|-----------|-------|-------------|
| λ | 0.02 | Trust decay constant |
| μ | 0.1 | Recovery decay constant |
| η | 0.01 | Weight adaptation learning rate |
| κ | 0.05 | Threat severity decay |
| τ | 3600s | Temporal correlation window |
| k | 0.5 | CUSUM allowance |
| h | 3.0 | CUSUM decision threshold |
| f | 1 | Byzantine fault tolerance (N=4) |
| β₀ | -2.0 | Deception model bias |
| S_max | 100 | Maximum credential strength |
| Min_Security | 0.8 | Minimum security requirement |

