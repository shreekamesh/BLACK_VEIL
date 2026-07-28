export interface TrustScore {
  entityId: string
  entityType: 'user' | 'system' | 'application' | 'device'
  score: number
  confidence: number
  level: 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW' | 'CRITICAL'
  previousTrust?: number
  trustDelta?: number
  riskScore: number
  trustDna?: Record<string, number>
  recoveryState?: string
  contributingFactors: Record<string, number>
  explanation?: string
  timestamp: string
}

export interface TrustFactor {
  name: string
  score: number
  weight: number
  description?: string
  trend?: 'increasing' | 'decreasing' | 'stable'
}

export interface TrustHistoryPoint {
  timestamp: string
  score: number
  change?: number
  eventType?: string
  reason?: string
}

export interface TrustHistory {
  entityId: string
  scores: TrustHistoryPoint[]
  count: number
  trend?: 'improving' | 'declining' | 'stable'
  volatility?: number
}

export interface TrustRelationship {
  id: string
  source: string
  target: string
  trustScore: number
  relationshipType: string
  interactionCount: number
  lastInteraction?: string
}

export interface TrustGraphNode {
  id: string
  label: string
  type: 'user' | 'system' | 'device' | 'application'
  trustScore: number
  riskLevel: string
  size?: number
}

export interface TrustGraphEdge {
  id: string
  source: string
  target: string
  trustScore: number
  type: string
  directed: boolean
}

export interface TrustGraph {
  nodes: TrustGraphNode[]
  edges: TrustGraphEdge[]
  count: number
}

export interface TrustSummary {
  avgTrust: number
  totalRelationships: number
  byLevel: Record<string, number>
  generatedAt: string
}

export interface TrustEvent {
  id: string
  eventType: string
  source: string
  target: string
  severity: number
  confidence: number
  context: Record<string, any>
  evidence: Record<string, any>
  timestamp: string
}

export interface TrustCalculationRequest {
  entityId: string
  scores?: Record<string, number>
  context?: Record<string, any>
}
