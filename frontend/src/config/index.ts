export interface AppConfig {
  api: {
    baseUrl: string
    timeout: number
    retries: number
    retryDelay: number
    webSocketUrl: string
  }
  theme: {
    darkMode: boolean
    primaryColor: string
    secondaryColor: string
  }
  environment: 'development' | 'staging' | 'production'
  version: string
  appName: string
  debug: boolean
}

const env = import.meta.env

export const config: AppConfig = {
  api: {
    baseUrl: env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
    timeout: parseInt(env.VITE_API_TIMEOUT || '30000'),
    retries: parseInt(env.VITE_API_RETRIES || '3'),
    retryDelay: parseInt(env.VITE_API_RETRY_DELAY || '1000'),
    webSocketUrl: env.VITE_WS_URL || 'ws://localhost:8000',
  },
  theme: {
    darkMode: env.VITE_DARK_MODE === 'true',
    primaryColor: env.VITE_PRIMARY_COLOR || '#00d4ff',
    secondaryColor: env.VITE_SECONDARY_COLOR || '#7c3aed',
  },
  environment: (env.VITE_ENVIRONMENT || 'development') as AppConfig['environment'],
  version: env.VITE_APP_VERSION || '5.0.0',
  appName: env.VITE_APP_NAME || 'BLACK VEIL V5',
  debug: env.VITE_DEBUG === 'true',
}

