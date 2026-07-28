export interface PredictionRequest {
  inputData: Record<string, any>
  models?: string[]
  returnExplanations?: boolean
  returnFeatureImportance?: boolean
  timeoutSeconds?: number
}

export interface PredictionResponse {
  requestId: string
  predictions: ModelPrediction[]
  ensemblePrediction?: Record<string, any>
  consensusPrediction?: Record<string, any>
  finalClassification?: string
  overallConfidence?: number
  totalLatencyMs: number
  timestamp: string
  correlationId: string
}

export interface ModelPrediction {
  modelName: string
  modelVersion: string
  prediction: number
  confidence: number
  probabilities?: Record<string, number>
  latencyMs: number
  modelType: string
  domain: string
}

export interface EnsemblePrediction {
  modelName: string
  modelVersion: string
  ensembleWeights: Record<string, number>
  prediction: number
  confidence: number
  agreement: number
}

export interface ModelInfo {
  modelName: string
  modelVersion: string
  modelType: 'cnn' | 'dnn' | 'ann' | 'rf' | 'xgboost' | 'transformer'
  domain: string
  featureCount: number
  outputClasses: string[]
  isLoaded: boolean
  accuracy?: number
  precision?: number
  recall?: number
  f1Score?: number
  lastTrained?: string
  trainingSamples?: number
  status: 'active' | 'training' | 'failed' | 'inactive'
}

export interface TrainingRequest {
  modelType: string
  trainingConfig: TrainingConfig
  dataSource: DataSource
  modelVersion?: string
  useGpu?: boolean
  notifyOnCompletion?: boolean
}

export interface TrainingConfig {
  epochs: number
  batchSize: number
  learningRate: number
  validationSplit: number
  optimizer: string
  lossFunction: string
  earlyStopping: boolean
  patience: number
}

export interface DataSource {
  type: 's3' | 'local' | 'api' | 'database'
  uri: string
  format: 'csv' | 'json' | 'parquet' | 'tfrecord'
  schema?: string
}

export interface TrainingStatus {
  jobId: string
  modelName: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  startedAt?: string
  completedAt?: string
  metrics?: Record<string, number>
  error?: string
}

export interface FeatureImportance {
  features: Record<string, number>
  method: 'shap' | 'lime' | 'integrated_gradients'
  baselineScore: number
}

export interface Explanation {
  method: string
  topFeatures: { name: string; importance: number }[]
  baselineScore: number
  summary: string
}
