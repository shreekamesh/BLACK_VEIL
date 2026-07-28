import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { apiClient } from '@/api/client'
import type { PredictionResponse, ModelInfo, TrainingStatus } from '@/types/ai'

interface AIState {
  predictions: Record<string, PredictionResponse>
  models: ModelInfo[]
  selectedModel: string | null
  trainingJobs: TrainingStatus[]
  predictLoading: boolean
  modelsLoading: boolean
  error: string | null
}

const initialState: AIState = {
  predictions: {},
  models: [],
  selectedModel: null,
  trainingJobs: [],
  predictLoading: false,
  modelsLoading: false,
  error: null,
}

export const fetchModels = createAsyncThunk(
  'ai/fetchModels',
  async (_, { rejectWithValue }) => {
    try {
      return await apiClient.get<ModelInfo[]>('/models')
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch models')
    }
  },
)

export const fetchModelById = createAsyncThunk(
  'ai/fetchModel',
  async (modelId: string, { rejectWithValue }) => {
    try {
      return await apiClient.get<ModelInfo>(`/models/${modelId}`)
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch model')
    }
  },
)

const aiSlice = createSlice({
  name: 'ai',
  initialState,
  reducers: {
    setSelectedModel: (state, action: PayloadAction<string | null>) => {
      state.selectedModel = action.payload
    },
    addPrediction: (state, action: PayloadAction<PredictionResponse>) => {
      state.predictions[action.payload.requestId] = action.payload
    },
    addTrainingJob: (state, action: PayloadAction<TrainingStatus>) => {
      state.trainingJobs.push(action.payload)
    },
    updateTrainingJob: (state, action: PayloadAction<TrainingStatus>) => {
      const index = state.trainingJobs.findIndex((j) => j.jobId === action.payload.jobId)
      if (index !== -1) {
        state.trainingJobs[index] = action.payload
      }
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchModels.pending, (state) => {
        state.modelsLoading = true
        state.error = null
      })
      .addCase(fetchModels.fulfilled, (state, action) => {
        state.modelsLoading = false
        state.models = action.payload
      })
      .addCase(fetchModels.rejected, (state, action) => {
        state.modelsLoading = false
        state.error = action.payload as string
      })
      .addCase(fetchModelById.fulfilled, (state, action) => {
        const index = state.models.findIndex((m) => m.modelName === action.payload.modelName)
        if (index !== -1) {
          state.models[index] = action.payload
        } else {
          state.models.push(action.payload)
        }
      })
  },
})

export const { setSelectedModel, addPrediction, addTrainingJob, updateTrainingJob, clearError } =
  aiSlice.actions
export default aiSlice.reducer

