export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',

  DASHBOARD: '/dashboard',
  DASHBOARD_OVERVIEW: '/dashboard/overview',
  DASHBOARD_ANALYTICS: '/dashboard/analytics',

  TRUST: '/trust',
  TRUST_SCORES: '/trust/scores',
  TRUST_HISTORY: '/trust/history',
  TRUST_RELATIONSHIPS: '/trust/relationships',
  TRUST_GRAPH: '/trust/graph',

  AI: '/ai',
  AI_PREDICT: '/ai/predict',
  AI_MODELS: '/ai/models',
  AI_TRAINING: '/ai/training',
  AI_EXPLAIN: '/ai/explain',

  COGNITIVE: '/cognitive',
  COGNITIVE_STATE: '/cognitive/state',
  COGNITIVE_CONSENSUS: '/cognitive/consensus',
  COGNITIVE_GRAPH: '/cognitive/graph',
  COGNITIVE_MEMORY: '/cognitive/memory',

  INCIDENTS: '/incidents',
  INCIDENTS_LIST: '/incidents/list',
  INCIDENTS_DETAILS: '/incidents/:id',
  INCIDENTS_RESPONSE: '/incidents/:id/respond',
  INCIDENTS_SUMMARY: '/incidents/summary',

  DECEPTION: '/deception',
  DECEPTION_HONEYPOTS: '/deception/honeypots',
  DECEPTION_TWINS: '/deception/twins',
  DECEPTION_DASHBOARD: '/deception/dashboard',

  CREDENTIALS: '/credentials',
  CREDENTIALS_GENOME: '/credentials/genome',
  CREDENTIALS_MUTATE: '/credentials/mutate',
  CREDENTIALS_IDENTITY: '/credentials/identity',
  CREDENTIALS_SESSIONS: '/credentials/sessions',

  EVOLUTION: '/evolution',
  EVOLUTION_DASHBOARD: '/evolution/dashboard',
  EVOLUTION_LEARNING: '/evolution/learning',
  EVOLUTION_ADAPTATION: '/evolution/adaptation',
  EVOLUTION_HISTORY: '/evolution/history',

  ADMIN: '/admin',
  ADMIN_USERS: '/admin/users',
  ADMIN_CONFIG: '/admin/config',
  ADMIN_MODELS: '/admin/models',
  ADMIN_LOGS: '/admin/logs',
  ADMIN_ETHICS: '/admin/ethics',

  PROFILE: '/profile',
  SETTINGS: '/settings',
  HELP: '/help',
} as const

export type Route = (typeof ROUTES)[keyof typeof ROUTES]

