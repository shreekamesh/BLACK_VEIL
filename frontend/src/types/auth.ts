export interface User {
  id: string
  username: string
  email: string
  fullName: string
  role: 'admin' | 'analyst' | 'viewer' | 'system'
  isActive: boolean
  lastLogin?: string
  createdAt: string
  permissions: string[]
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  fullName: string
  role?: 'admin' | 'analyst' | 'viewer' | 'system'
}

export interface AuthResponse {
  user: User
  token: string
  refreshToken: string
  expiresIn: number
}

export interface TokenPayload {
  sub: string
  username: string
  role: string
  permissions: string[]
  iat: number
  exp: number
  type: 'access' | 'refresh'
}

export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface Session {
  id: string
  userId: string
  ipAddress: string
  userAgent: string
  lastActivity: string
  createdAt: string
  isCurrent: boolean
}

export interface ApiKey {
  id: string
  name: string
  key: string
  permissions: string[]
  createdAt: string
  lastUsed?: string
  expiresAt?: string
  isActive: boolean
}
