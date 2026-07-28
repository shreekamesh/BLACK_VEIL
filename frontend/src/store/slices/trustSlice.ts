import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { apiClient } from '@/api/client'
import type { TrustScore, TrustHistory, TrustGraph, TrustSummary } from '@/types/trust'

interface TrustState {
  scores: Record<string, TrustScore>
  selectedEntity: string | null
  history: TrustHistory | null
  graph: TrustGraph | null
  summary: TrustSummary | null
  isLoading: boolean
  error: string | null
}

const initialState: TrustState = {
  scores: {},
  selectedEntity: null,
  history: null,
  graph: null,
  summary: null,
  isLoading: false,
  error: null,
}

export const fetchTrustScore = createAsyncThunk(
  'trust/fetchScore',
  async (entityId: string, { rejectWithValue }) => {
    try {
      return await apiClient.get<TrustScore>(`/trust/score/${entityId}`)
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch trust score')
    }
  },
)

export const fetchTrustHistory = createAsyncThunk(
  'trust/fetchHistory',
  async ({ entityId, limit }: { entityId: string; limit?: number }, { rejectWithValue }) => {
    try {
      return await apiClient.get<TrustHistory>(`/trust/history/${entityId}`, { limit })
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch trust history')
    }
  },
)

export const fetchTrustGraph = createAsyncThunk(
  'trust/fetchGraph',
  async (_, { rejectWithValue }) => {
    try {
      return await apiClient.get<TrustGraph>('/trust/graph')
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch trust graph')
    }
  },
)

export const fetchTrustSummary = createAsyncThunk(
  'trust/fetchSummary',
  async (_, { rejectWithValue }) => {
    try {
      return await apiClient.get<TrustSummary>('/trust/summary')
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch trust summary')
    }
  },
)

const trustSlice = createSlice({
  name: 'trust',
  initialState,
  reducers: {
    setSelectedEntity: (state, action: PayloadAction<string | null>) => {
      state.selectedEntity = action.payload
    },
    updateTrustScore: (state, action: PayloadAction<TrustScore>) => {
      state.scores[action.payload.entityId] = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTrustScore.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchTrustScore.fulfilled, (state, action) => {
        state.isLoading = false
        state.scores[action.payload.entityId] = action.payload
      })
      .addCase(fetchTrustScore.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(fetchTrustHistory.fulfilled, (state, action) => {
        state.history = action.payload
      })
      .addCase(fetchTrustGraph.fulfilled, (state, action) => {
        state.graph = action.payload
      })
      .addCase(fetchTrustSummary.fulfilled, (state, action) => {
        state.summary = action.payload
      })
  },
})

export const { setSelectedEntity, updateTrustScore, clearError } = trustSlice.actions
export default trustSlice.reducer

