export interface CognitiveState {
  stateId: string
  stateType: 'perception' | 'reasoning' | 'memory' | 'meta_cognitive'
  stateData: Record<string, any>
  schemaVersion: string
  isCurrent: boolean
  createdAt: string
}

export interface PerceptionState {
  status: 'active' | 'degraded' | 'inactive'
  sensors: string[]
  lastUpdate: string
  activeFeatures: number
  dataRate: number
}

export interface ReasoningState {
  status: 'active' | 'degraded' | 'inactive'
  engines: string[]
  lastUpdate: string
  activeContexts: number
  reasoningCycles: number
}

export interface MemoryState {
  status: 'active' | 'degraded' | 'inactive'
  memoryTypes: string[]
  totalMemories: number
  lastUpdate: string
  recallAccuracy: number
}

export interface MetaCognitiveState {
  status: 'monitoring' | 'alert' | 'recovering'
  awarenessLevel: 'low' | 'medium' | 'high'
  anomaliesDetected: number
  selfHealthChecks: Record<string, string>
  lastUpdate: string
}

export interface ConsensusResult {
  consensus: boolean
  agreement: number
  participants: number
  decisions: Record<string, any>
  finalDecision: any
  confidence: number
}

export interface AttackMemory {
  id: string
  attackType: string
  technique: string
  mitreId?: string
  timestamp: string
  entities: string[]
  patterns: string[]
  severity: number
  resolved: boolean
  relatedMemoryIds: string[]
  ttl: number
}

export interface MemoryGraph {
  nodes: MemoryGraphNode[]
  edges: MemoryGraphEdge[]
}

export interface MemoryGraphNode {
  id: string
  label: string
  type: 'attack' | 'entity' | 'pattern' | 'technique'
  size?: number
  color?: string
  metadata?: Record<string, any>
}

export interface MemoryGraphEdge {
  id: string
  source: string
  target: string
  label: string
  weight: number
  type: 'correlated' | 'sequence' | 'similar' | 'caused'
}
