export interface Incident {
  id: string
  type: string
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO'
  status: 'NEW' | 'INVESTIGATING' | 'CONTAINED' | 'RESOLVED' | 'CLOSED'
  title: string
  description?: string
  source?: string
  target?: string
  attackVector?: string
  mitreId?: string
  confidence?: number
  riskScore?: number
  evidence?: Record<string, any>
  timeline?: Record<string, any>[]
  detectedAt: string
  resolvedAt?: string
  assignedTo?: string
  responses?: IncidentResponse[]
}

export interface IncidentResponse {
  id: string
  type: string
  action: string
  status: string
  executedAt?: string
}

export interface IncidentSummary {
  total: number
  bySeverity: Record<string, number>
  byStatus: Record<string, number>
  byType?: Record<string, number>
  trend?: { date: string; count: number }[]
}

export interface IncidentCreateRequest {
  title: string
  description?: string
  severity: string
  source?: string
  attackType?: string
  affectedAssets?: string[]
  indicators?: Record<string, any>[]
  evidence?: Record<string, any>
}

export interface IncidentRespondRequest {
  actionType: 'isolate' | 'block' | 'rotate' | 'alert' | 'deploy'
  description?: string
  parameters?: Record<string, any>
}

export interface IncidentFilter {
  status?: string
  severity?: string
  type?: string
  assignedTo?: string
  dateFrom?: string
  dateTo?: string
  search?: string
}

export interface IncidentStats {
  total: number
  critical: number
  high: number
  medium: number
  low: number
  info: number
  open: number
  investigating: number
  contained: number
  resolved: number
  closed: number
  avgResponseTime: number
  responseRate: number
}
