export interface DeceptionInstance {
  deceptionId: string
  deceptionType: 'HONEYPOT' | 'DECOY' | 'TWIN' | 'CREDENTIAL' | 'SERVICE'
  deceptionSubtype?: string
  targetEntity?: string
  status: 'active' | 'triggered' | 'evolved' | 'expired'
  effectivenessScore: number
  detectionProbability: number
  interactionCount: number
  generation: number
  deployedAt: string
  lastInteraction?: string
  payloadSummary?: Record<string, any>
  configSummary?: Record<string, any>
}

export interface DeployDeceptionRequest {
  deceptionType: string
  deceptionSubtype?: string
  targetEntity?: string
  initialEffectiveness?: number
  initialDetectionProb?: number
  payload?: Record<string, any>
  config?: Record<string, any>
}

export interface HoneypotConfig {
  name: string
  type: string
  port: number
  protocol: string
  services: string[]
  banner: string
  interactionLimit: number
  logLevel: string
}

export interface DigitalTwinConfig {
  sourceSystem: string
  replicaName: string
  services: string[]
  dataMapping: Record<string, string>
  syncInterval: number
  isolationLevel: string
}

export interface DeceptionStats {
  totalDeceptions: number
  activeDeceptions: number
  triggeredDeceptions: number
  avgEffectiveness: number
  avgDetectionProb: number
  totalInteractions: number
  avgGeneration: number
  byType: Record<string, number>
  byStatus: Record<string, number>
}

export interface InteractionEvent {
  id: string
  deceptionId: string
  attackerIp?: string
  technique: string
  techniqueId?: string
  timestamp: string
  action: string
  data: Record<string, any>
  detected: boolean
}
