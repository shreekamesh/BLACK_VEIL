import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { apiClient } from '@/api/client'

export interface DashboardMetrics {
  totalThreats: number
  threatChange?: number
  averageTrust: number
  trustChange?: number
  averageConfidence: number
  confidenceChange?: number
  activeDeceptions: number
  deceptionChange?: number
  activeIncidents: number
  systemHealth: number
  predictionsToday: number
}

export interface SecurityStatus {
  status: 'safe' | 'warning' | 'danger'
  threatLevel: number
  totalAttacks: number
  blockedAttacks: number
  activeIncidents: number
  lastUpdate: string
}

export interface AttackTimelinePoint {
  timestamp: string
  attacks: number
  blocked: number
  alerts: number
}

export interface RecentActivity {
  id: string
  type: string
  message: string
  severity: string
  timestamp: string
  entity: string
}

export interface DashboardData {
  metrics: DashboardMetrics
  securityStatus: SecurityStatus
  attackTimeline: AttackTimelinePoint[]
  trustHeatmap: any[]
  aiConfidenceData: any[]
  incidentSummary: any
  deceptionStatus: any
  recentActivities: RecentActivity[]
  lastUpdated: string
}

interface DashboardState {
  data: DashboardData | null
  isLoading: boolean
  error: string | null
}

const initialState: DashboardState = {
  data: null,
  isLoading: false,
  error: null,
}

export const fetchDashboardData = createAsyncThunk(
  'dashboard/fetchData',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<DashboardData>('/analytics/dashboard')
      return response
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch dashboard data')
    }
  },
)

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    updateMetrics: (state, action: PayloadAction<Partial<DashboardMetrics>>) => {
      if (state.data) {
        state.data.metrics = { ...state.data.metrics, ...action.payload }
        state.data.lastUpdated = new Date().toISOString()
      }
    },
    updateSecurityStatus: (state, action: PayloadAction<SecurityStatus>) => {
      if (state.data) {
        state.data.securityStatus = action.payload
        state.data.lastUpdated = new Date().toISOString()
      }
    },
    addActivity: (state, action: PayloadAction<RecentActivity>) => {
      if (state.data) {
        state.data.recentActivities.unshift(action.payload)
        if (state.data.recentActivities.length > 50) {
          state.data.recentActivities.pop()
        }
      }
    },
    clearDashboard: (state) => {
      state.data = null
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardData.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchDashboardData.fulfilled, (state, action) => {
        state.isLoading = false
        state.data = action.payload
      })
      .addCase(fetchDashboardData.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
  },
})

export const { updateMetrics, updateSecurityStatus, addActivity, clearDashboard } =
  dashboardSlice.actions
export default dashboardSlice.reducer

