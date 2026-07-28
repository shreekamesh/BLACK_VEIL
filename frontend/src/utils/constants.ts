export const APP_NAME = 'BLACK VEIL V5'
export const APP_DESCRIPTION = 'Cognitive Autonomous Cyber Defense Organism'
export const APP_VERSION = '5.0.0'

export const DRAWER_WIDTH = 260
export const DRAWER_COLLAPSED_WIDTH = 72
export const HEADER_HEIGHT = 64

export const TRUST_LEVELS = {
  CRITICAL: { min: 0, max: 19, color: '#ef4444', label: 'Critical' },
  LOW: { min: 20, max: 39, color: '#f97316', label: 'Low' },
  MEDIUM: { min: 40, max: 59, color: '#f59e0b', label: 'Medium' },
  HIGH: { min: 60, max: 79, color: '#10b981', label: 'High' },
  VERY_HIGH: { min: 80, max: 100, color: '#06b6d4', label: 'Very High' },
} as const

export const SEVERITY_COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#f59e0b',
  LOW: '#6b7280',
  INFO: '#3b82f6',
} as const

export const INCIDENT_STATUS_COLORS = {
  NEW: '#f59e0b',
  INVESTIGATING: '#3b82f6',
  CONTAINED: '#8b5cf6',
  RESOLVED: '#10b981',
  CLOSED: '#6b7280',
} as const

export const INCIDENT_STATUS_LABELS = {
  NEW: 'New',
  INVESTIGATING: 'Investigating',
  CONTAINED: 'Contained',
  RESOLVED: 'Resolved',
  CLOSED: 'Closed',
} as const

export const TIME_RANGES = [
  { label: '1 Hour', value: '1h' },
  { label: '6 Hours', value: '6h' },
  { label: '24 Hours', value: '24h' },
  { label: '7 Days', value: '7d' },
  { label: '30 Days', value: '30d' },
] as const

export const REFRESH_INTERVALS = {
  REAL_TIME: 1000,
  FAST: 5000,
  NORMAL: 15000,
  SLOW: 30000,
  STATIC: 60000,
} as const

export const CHART_COLORS = [
  '#00d4ff',
  '#7c3aed',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#3b82f6',
  '#8b5cf6',
  '#ec4899',
  '#14b8a6',
  '#f97316',
] as const

export const PAGINATION_DEFAULTS = {
  PAGE_SIZE: 10,
  PAGE_SIZE_OPTIONS: [5, 10, 25, 50],
} as const
