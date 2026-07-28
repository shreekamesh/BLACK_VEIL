import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { apiClient } from '@/api/client'
import { CognitiveState, ConsensusResult, MemoryGraph } from '@/types/cognitive'

export interface CognitiveStateType {
  currentState: CognitiveState | null
  perceptionState: any | null
  reasoningState: any | null
  memoryState: any | null
  metaCognitiveState: any | null
  consensusResult: ConsensusResult | null
  memoryGraph: MemoryGraph | null
  isLoading: boolean
  error: string | null
}

const initialState: CognitiveStateType = {
  currentState: null,
  perceptionState: null,
  reasoningState: null,
  memoryState: null,
  metaCognitiveState: null,
  consensusResult: null,
  memoryGraph: null,
  isLoading: false,
  error: null,
}

export const fetchCognitiveState = createAsyncThunk(
  'cognitive/fetchState',
  async (stateType: string, { rejectWithValue }) => {
    try {
      return await apiClient.get(`/cognitive/state/${stateType}`)
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch cognitive state')
    }
  },
)

export const fetchPerceptionState = createAsyncThunk(
  'cognitive/fetchPerception',
  async (_, { rejectWithValue }) => {
    try {
      return await apiClient.get('/cognitive/perception')
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch perception state')
    }
  },
)

export const fetchReasoningState = createAsyncThunk(
  'cognitive/fetchReasoning',
  async (_, { rejectWithValue }) => {
    try {
      return await apiClient.get('/cognitive/reasoning')
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch reasoning state')
    }
  },
)

export const fetchMemoryState = createAsyncThunk(
  'cognitive/fetchMemory',
  async (_, { rejectWithValue }) => {
    try {
      return await apiClient.get('/cognitive/memory')
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch memory state')
    }
  },
)

export const fetchMetaCognitiveState = createAsyncThunk(
  'cognitive/fetchMetaCognitive',
  async (_, { rejectWithValue }) => {
    try {
      return await apiClient.get('/cognitive/meta-cognitive')
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch meta-cognitive state')
    }
  },
)

const cognitiveSlice = createSlice({
  name: 'cognitive',
  initialState,
  reducers: {
    updatePerceptionState: (state, action: PayloadAction<any>) => {
      state.perceptionState = action.payload
    },
    updateReasoningState: (state, action: PayloadAction<any>) => {
      state.reasoningState = action.payload
    },
    updateMemoryState: (state, action: PayloadAction<any>) => {
      state.memoryState = action.payload
    },
    clearCognitiveError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCognitiveState.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(fetchCognitiveState.fulfilled, (state, action) => {
        state.isLoading = false
        state.currentState = action.payload as unknown as CognitiveState
      })
      .addCase(fetchCognitiveState.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.payload as string
      })
      .addCase(fetchPerceptionState.fulfilled, (state, action) => {
        state.perceptionState = action.payload
      })
      .addCase(fetchReasoningState.fulfilled, (state, action) => {
        state.reasoningState = action.payload
      })
      .addCase(fetchMemoryState.fulfilled, (state, action) => {
        state.memoryState = action.payload
      })
      .addCase(fetchMetaCognitiveState.fulfilled, (state, action) => {
        state.metaCognitiveState = action.payload
      })
  },
})

export const {
  updatePerceptionState,
  updateReasoningState,
  updateMemoryState,
  clearCognitiveError,
} = cognitiveSlice.actions

export default cognitiveSlice.reducer

