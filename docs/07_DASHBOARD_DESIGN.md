# BLACK VEIL V2 — Dashboard Design

## React-based Real-time Security Dashboard

---

## 1. Dashboard Overview

### Tech Stack
- **Framework**: React 18 + TypeScript
- **State Management**: Redux Toolkit + RTK Query
- **Real-time**: WebSocket (Socket.io)
- **Charts**: D3.js + Recharts
- **UI**: Material-UI (MUI) + Custom Components
- **Maps**: Leaflet.js for heatmap
- **Build**: Vite
- **Testing**: Jest + React Testing Library

### Layout Structure
```
┌─────────────────────────────────────────────────────────────────────────┐
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  HEADER: Logo | Status Bar | System Health | Notifications | User │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────┬─────────────────────────────────────────────────────────┐  │
│  │         │                                                         │  │
│  │  SIDE   │                   MAIN CONTENT AREA                     │  │
│  │  NAV    │                                                         │  │
│  │         │  ┌──────────────────────────────────────────────────┐   │  │
│  │  • Trust│  │            TRUST OVERVIEW CARDS                  │   │  │
│  │  • Threat│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │   │  │
│  │  • Decep.│  │  │Overall│ │Network│ │  IoT │ │ User │ │CICIDS│  │   │  │
│  │  • Agents│  │  │ Trust │ │ Trust │ │ Trust│ │ Trust│ │Trust │  │   │  │
│  │  • Reports│  │  │  81%  │ │  87%  │ │  82% │ │  74% │ │  80% │  │   │  │
│  │  • Settings│  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘  │   │  │
│  │         │  └──────────────────────────────────────────────────┘   │  │
│  │         │                                                         │  │
│  │         │  ┌──────────────────────────────────────────────────┐   │  │
│  │         │  │         REAL-TIME THREAT FEED                    │   │  │
│  │         │  │  ┌──────────────────────┐ ┌──────────────────┐  │   │  │
│  │         │  │  │  Threat Timeline     │ │  Attack Map      │  │   │  │
│  │         │  │  │  (Scrollable List)   │ │  (Geo Heatmap)   │  │   │  │
│  │         │  │  └──────────────────────┘ └──────────────────┘  │   │  │
│  │         │  └──────────────────────────────────────────────────┘   │  │
│  │         │                                                         │  │
│  │         │  ┌──────────────────────────────────────────────────┐   │  │
│  │         │  │     DECEPTION & RESPONSE STATUS                  │   │  │
│  │         │  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │   │  │
│  │         │  │  │ Active   │ │ Fake     │ │ Response         │ │   │  │
│  │         │  │  │Honeypots │ │Credential │ │ History          │ │   │  │
│  │         │  │  │    5     │ │    12    │ │ Last 24h: 18     │ │   │  │
│  │         │  │  └──────────┘ └──────────┘ └──────────────────┘ │   │  │
│  │         │  └──────────────────────────────────────────────────┘   │  │
│  │         │                                                         │  │
│  │         │  ┌──────────────────────────────────────────────────┐   │  │
│  │         │  │         AGENT HEALTH STATUS                      │   │  │
│  │         │  │  ○ Network Agent 01 - HEALTHY (Trust: 87%)      │   │  │
│  │         │  │  ○ IoT Agent 01 - HEALTHY (Trust: 82%)          │   │  │
│  │         │  │  ⚠ User Agent 01 - WATCHLIST (Trust: 74%)       │   │  │
│  │         │  │  ○ CICIDS Agent 01 - HEALTHY (Trust: 80%)       │   │  │
│  │         │  │  ○ Fusion Agent - HEALTHY                        │   │  │
│  │         │  └──────────────────────────────────────────────────┘   │  │
│  └─────────┴─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Screen Views

### 2.1 Main Dashboard View (`/dashboard`)
```
Components:
├── SystemStatusBar (Top)
│   ├── Overall System Health (Green/Yellow/Red)
│   ├── Active Threats Counter
│   ├── Uptime Display
│   └── Last Updated Timestamp
│
├── TrustOverviewCards
│   ├── OverallCompositeTrust (Gauge Chart)
│   ├── NetworkTrustCard
│   ├── IoTTrustCard
│   ├── UserTrustCard
│   └── CICIDSTrustCard
│
├── RealTimeThreatFeed
│   ├── ThreatTimeline (Virtualized List)
│   │   ├── Threat ID | Time | Type | Severity | Source | Status
│   │   └── Click to expand details
│   └── ThreatHeatmap (Geo Map)
│       └── Color-coded intensity overlay
│
├── DeceptionStatusPanel
│   ├── ActiveHoneypots
│   │   ├── Count + Details
│   │   └── Interaction Rate Chart
│   └── FakeCredentialStatus
│       ├── Mutation Timeline
│       └── Detection Stats
│
├── ResponseHistoryPanel
│   ├── Recent Actions List
│   ├── Success Rate Chart
│   └── Auto vs Manual Response Ratio
│
└── AgentHealthGrid
    ├── Agent Cards (8 total)
    ├── Status Indicator (Active/Compromised/Recovering)
    ├── Current Trust Score
    └── Last Heartbeat Timestamp
```

### 2.2 Trust Analysis View (`/trust`)
```
Components:
├── TrustTimeSeries (Interactive Chart)
│   ├── Select agents to compare
│   ├── Time range selector (1h/6h/24h/7d/30d)
│   ├── Granularity control
│   └── Annotations for events (threats, recoveries)
│
├── TrustDistribution
│   ├── Histogram of trust scores
│   ├── Statistical summary (mean, std, percentiles)
│   └── Outlier detection
│
├── TrustDriftDetection
│   ├── Drift score timeline
│   ├── Change point markers
│   └── Drift type classification
│
├── RecoveryTimeline
│   ├── Recovery events on timeline
│   ├── Recovery success/failure indicators
│   └── Recovery probability chart
│
└── ExplainableTrustPanel
    ├── Feature contribution bar chart (SHAP)
    ├── Top factors affecting trust
    └── Natural language explanation
```

### 2.3 Threat Intelligence View (`/threats`)
```
Components:
├── ThreatOverview
│   ├── Severity distribution (Pie/Donut chart)
│   ├── Threat type breakdown
│   └── Time-series trend
│
├── ThreatCorrelationGraph
│   ├── Interactive network graph
│   ├── Cluster visualization
│   ├── Correlation strength edges
│   └── Click to explore cluster
│
├── AttackTimeline
│   ├── Kill chain visualization
│   ├── Step-by-step reconstruction
│   ├── Evidence markers
│   └── Confidence scores per step
│
├── ThreatHeatmapView
│   ├── Geo-map with intensity overlay
│   ├── Time-lapse animation
│   └── Hotspot identification
│
└── BehaviorPrediction
    ├── Predicted next attack vectors
    ├── Confidence intervals
    └── Recommended countermeasures
```

### 2.4 Deception Status View (`/deception`)
```
Components:
├── ActiveDeceptionsGrid
│   ├── Card per active deception
│   ├── Type (Honeypot/Credential/Service)
│   ├── Status (Active/Triggered/Expired)
│   ├── Interaction count
│   └── Time remaining
│
├── CredentialMutationTimeline
│   ├── Mutation history per credential
│   ├── Credential strength evolution
│   └── Lifetime prediction
│
├── HoneypotInteractionFeed
│   ├── Real-time interaction log
│   ├── Attacker behavior analysis
│   └── Technique classification (MITRE)
│
└── DeceptionEffectiveness
    ├── Detection rate
    ├── Dwell time statistics
    └── Attack diversion metrics
```

### 2.5 Agent Management View (`/agents`)
```
Components:
├── AgentList
│   ├── Search/filter agents
│   ├── Status filters (All/Active/Compromised/Recovering)
│   ├── Quick action buttons
│   └── Agent detail expansion
│
├── AgentDetailPanel
│   ├── Performance metrics
│   ├── Trust history chart
│   ├── Recent predictions
│   └── Configuration editor
│
├── AgentComparison
│   ├── Side-by-side agent comparison
│   ├── Metric selection
│   └── Statistical significance indicators
│
└── AgentRegistration
    ├── Registration form
    ├── API key generation
    └── Configuration template
```

### 2.6 Report Center (`/reports`)
```
Components:
├── ReportGenerator
│   ├── Report type selection
│   ├── Time range picker
│   ├── Format selector (PDF/HTML/CSV)
│   ├── Content toggles
│   └── Generate button
│
├── ReportList
│   ├── Generated reports table
│   ├── Download/Delete actions
│   └── Schedule recurring reports
│
└── ReportViewer
    ├── Embedded PDF viewer
    ├── Print/Export options
    └── Share with team
```

---

## 3. Color Scheme & Theme

### Dark Theme (Default)
```css
/* Background */
--bg-primary: #0a0e1a;        /* Main background */
--bg-secondary: #111827;      /* Card background */
--bg-tertiary: #1f2937;       /* Elevated surfaces */

/* Text */
--text-primary: #f9fafb;      /* Primary text */
--text-secondary: #9ca3af;    /* Secondary text */
--text-muted: #6b7280;        /* Muted text */

/* Accent - Cyber Blue */
--accent-primary: #00d4ff;    /* Primary accent */
--accent-secondary: #0099cc;  /* Secondary accent */
--accent-tertiary: #006699;   /* Dark accent */

/* Status Colors */
--status-healthy: #10b981;    /* Green - Agent healthy */
--status-warning: #f59e0b;    /* Yellow - Watchlist */
--status-danger: #ef4444;     /* Red - Compromised */
--status-critical: #dc2626;   /* Dark red - Critical */
--status-recovering: #8b5cf6; /* Purple - Recovery */

/* Threat Severity */
--severity-low: #6b7280;      /* Gray */
--severity-medium: #f59e0b;   /* Yellow */
--severity-high: #f97316;     /* Orange */
--severity-critical: #ef4444; /* Red */

/* Trust Score Range */
--trust-high: #10b981;        /* 80-100: Green */
--trust-medium: #f59e0b;      /* 60-79: Yellow */
--trust-low: #ef4444;         /* 0-59: Red */
```

### Components Style
```css
/* Cards */
.card {
  background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
  border: 1px solid #374151;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

/* Gauge Chart */
.gauge {
  background: conic-gradient(
    var(--trust-high) 0% 81%,
    var(--bg-tertiary) 81% 100%
  );
}

/* Real-time indicators */
.indicator {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
```

---

## 4. Real-time Update Mechanism

### WebSocket Connection
```typescript
// Socket.io connection
const socket = io('wss://api.blackveil.io/ws/dashboard', {
  auth: { token: 'jwt_token_here' },
  transports: ['websocket'],
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionAttempts: 10
});

// Event subscriptions
socket.on('trust_update', (data: TrustUpdate) => {
  dispatch(updateTrustScore(data));
});

socket.on('threat_detected', (data: ThreatEvent) => {
  dispatch(addThreatEvent(data));
  showNotification(data);
});

socket.on('deployment_status', (data: DeployStatus) => {
  dispatch(updateDeploymentStatus(data));
});

socket.on('response_executed', (data: ResponseEvent) => {
  dispatch(addResponseEvent(data));
});
```

### Update Frequency
| Update Type | Frequency | Transport |
|-------------|-----------|-----------|
| Trust scores | Every 5s | WebSocket |
| Threats | Real-time | WebSocket |
| Agent status | Every 10s | HTTP Polling |
| Deception status | Every 30s | WebSocket |
| Heatmap | Every 60s | WebSocket |
| Reports | On demand | HTTP |

---

## 5. Responsive Design

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Desktop | >1200px | Full 3-column |
| Tablet | 768-1200px | 2-column |
| Mobile | <768px | Single column, collapsible nav |

---

## 6. Accessibility

- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- High contrast mode
- Focus indicators
- ARIA labels on all interactive elements

