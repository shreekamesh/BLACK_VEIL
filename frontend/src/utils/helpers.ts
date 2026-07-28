import { TRUST_LEVELS, SEVERITY_COLORS, INCIDENT_STATUS_COLORS } from './constants'

export function getTrustLevel(score: number): keyof typeof TRUST_LEVELS {
  if (score >= 80) return 'VERY_HIGH'
  if (score >= 60) return 'HIGH'
  if (score >= 40) return 'MEDIUM'
  if (score >= 20) return 'LOW'
  return 'CRITICAL'
}

export function getTrustColor(score: number): string {
  const level = getTrustLevel(score)
  return TRUST_LEVELS[level].color
}

export function getTrustLabel(score: number): string {
  const level = getTrustLevel(score)
  return TRUST_LEVELS[level].label
}

export function getSeverityColor(severity: string): string {
  return SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS] || '#6b7280'
}

export function getIncidentStatusColor(status: string): string {
  return INCIDENT_STATUS_COLORS[status as keyof typeof INCIDENT_STATUS_COLORS] || '#6b7280'
}

export function getIncidentStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    NEW: 'New',
    INVESTIGATING: 'Investigating',
    CONTAINED: 'Contained',
    RESOLVED: 'Resolved',
    CLOSED: 'Closed',
  }
  return labels[status] || status
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}

export function range(start: number, end: number): number[] {
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
}

export function groupBy<T>(items: T[], key: keyof T): Record<string, T[]> {
  return items.reduce(
    (result, item) => {
      const groupKey = String(item[key])
      if (!result[groupKey]) {
        result[groupKey] = []
      }
      result[groupKey].push(item)
      return result
    },
    {} as Record<string, T[]>,
  )
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null

  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(() => {
      func(...args)
    }, wait)
  }
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 15)
}

export function classNames(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ')
}
