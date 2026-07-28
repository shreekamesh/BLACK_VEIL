export interface PaginationParams {
  page: number
  pageSize: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface ApiError {
  status: number
  message: string
  code?: string
  details?: Record<string, string[]>
}

export interface ApiResponse<T> {
  data: T
  message?: string
  status: string
  timestamp: string
}

export interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
  group?: string
}

export interface BreadcrumbItem {
  label: string
  path?: string
  icon?: React.ReactNode
}

export interface TabConfig {
  label: string
  value: string
  icon?: React.ReactNode
  count?: number
  disabled?: boolean
}

export interface TimeRange {
  start: Date
  end: Date
  preset: '1h' | '6h' | '24h' | '7d' | '30d' | 'custom'
}

export interface SortConfig {
  field: string
  direction: 'asc' | 'desc'
}

export interface FilterConfig {
  field: string
  operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains' | 'in' | 'between'
  value: any
}
