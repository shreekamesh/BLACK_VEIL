import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { apiClient } from '@/api/client'
import { Incident, IncidentFilter, IncidentSummary } from '@/types/incident'

interface IncidentState {
  incidents: Incident[]
  selectedIncident: Incident | null
  filter: IncidentFilter
  summary: IncidentSummary | null
  isLoading: boolean
  isSubmitting: boolean
  error: string | null
  total: number
  page: number
  pageSize: number
}

const initialState: IncidentState = {
  incidents: [],
  selectedIncident: null,
  filter: {},
  summary: null,
  isLoading: false,
  isSubmitting: false,
  error: null,
  total: 0,
  page: 1,
  pageSize: 20,
}

export const fetchIncidents = createAsyncThunk(
  'incidents/fetchAll',
  async (params: { page?: number; pageSize?: number; filter?: IncidentFilter } = {}, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<{ incidents: Incident[]; count: number }>(
        '/incidents',
        { ...params.filter, limit: params.pageSize, offset: ((params.page || 1) - 1) * (params.pageSize || 20) },
      )
      return response
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch incidents')
    }
  },
)

export const fetchIncidentById = createAsyncThunk(
  'incidents/fetchById',
  async (incidentId: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<Incident>(`/incidents/\${incidentId}`)
      return response
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch incident')
    }
  },
)

export const createIncident = createAsyncThunk(
  'incidents/create',
  async (incident: Partial<Incident>, { rejectWithValue }) => {
    try {
      const response = await apiClient.post<Incident>('/incidents', incident)
      return response
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create incident')
    }
  },
)

export const respondToIncident = createAsyncThunk(
  'incidents/respond',
  async ({ incidentId, response: action }: { incidentId: string; response: string }, { rejectWithValue }) => {
    try {
      await apiClient.post(`/incidents/\${incidentId}/respond`, { action })
      return { incidentId, action }
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to respond to incident')
    }
  },
)

export const fetchIncidentSummary = createAsyncThunk(
  'incidents/fetchSummary',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<IncidentSummary>('/incidents/summary')
      return response
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch incident summary')
    }
  },
)

const incidentSlice = createSlice({
  name: 'incidents',
  initialState,
  reducers: {
    setFilter: (state, action: PayloadAction<IncidentFilter>) => {
      state.filter = action.payload
      state.page = 1
    },
    clearFilter: (state) => {
      state.filter = {}
      state.page = 1
    },
    setPage: (state, action: PayloadAction<number>) => {
      state.page = action.payload
    },
    clearSelectedIncident: (state) => {
      state.selectedIncident = null
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchIncidents.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchIncidents.fulfilled, (state, action) => {
        state.isLoading = false
        state.incidents = action.payload.incidents
        state.total = action.payload.count
      })
      .addCase(fetchIncidents.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(fetchIncidentById.pending, (state) => {
        state.isLoading = true
      })
      .addCase(fetchIncidentById.fulfilled, (state, action) => {
        state.isLoading = false
        state.selectedIncident = action.payload
      })
      .addCase(fetchIncidentById.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(createIncident.pending, (state) => {
        state.isSubmitting = true
      })
      .addCase(createIncident.fulfilled, (state) => {
        state.isSubmitting = false
      })
      .addCase(createIncident.rejected, (state, action) => {
        state.isSubmitting = false
        state.error = action.payload as string
      })
      .addCase(fetchIncidentSummary.fulfilled, (state, action) => {
        state.summary = action.payload
      })
  },
})

export const { setFilter, clearFilter, setPage, clearSelectedIncident, clearError } = incidentSlice.actions
export default incidentSlice.reducer
