import { format, formatDistanceToNow, parseISO, differenceInDays, differenceInHours, differenceInMinutes } from 'date-fns'

export function formatDate(date: string | Date, formatStr: string = 'MMM dd, yyyy HH:mm'): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, formatStr)
}

export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  return formatDistanceToNow(d, { addSuffix: true })
}

export function formatShortDate(date: string | Date): string {
  return formatDate(date, 'MMM dd')
}

export function formatTime(date: string | Date): string {
  return formatDate(date, 'HH:mm:ss')
}

export function formatTimeAgo(date: string | Date): string {
  const d = typeof date === 'string' ? parseISO(date) : date
  const now = new Date()
  const minutes = differenceInMinutes(now, d)
  const hours = differenceInHours(now, d)
  const days = differenceInDays(now, d)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return formatDate(date, 'MMM dd')
}

export function getTimeRangePreset(preset: string): { start: Date; end: Date } {
  const end = new Date()
  let start: Date

  switch (preset) {
    case '1h':
      start = new Date(end.getTime() - 60 * 60 * 1000)
      break
    case '6h':
      start = new Date(end.getTime() - 6 * 60 * 60 * 1000)
      break
    case '24h':
      start = new Date(end.getTime() - 24 * 60 * 60 * 1000)
      break
    case '7d':
      start = new Date(end.getTime() - 7 * 24 * 60 * 60 * 1000)
      break
    case '30d':
      start = new Date(end.getTime() - 30 * 24 * 60 * 60 * 1000)
      break
    default:
      start = new Date(end.getTime() - 24 * 60 * 60 * 1000)
  }

  return { start, end }
}

export function isExpired(date: string | Date): boolean {
  const d = typeof date === 'string' ? parseISO(date) : date
  return d < new Date()
}

export function getDuration(start: string | Date, end?: string | Date): string {
  const s = typeof start === 'string' ? parseISO(start) : start
  const e = end ? (typeof end === 'string' ? parseISO(end) : end) : new Date()

  const minutes = differenceInMinutes(e, s)
  const hours = differenceInHours(e, s)
  const days = differenceInDays(e, s)

  if (days > 0) return `${days}d ${hours % 24}h`
  if (hours > 0) return `${hours}h ${minutes % 60}m`
  return `${minutes}m`
}
