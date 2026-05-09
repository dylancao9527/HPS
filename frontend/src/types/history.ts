import type {
  BloodPressureForecastPoint,
  PredictionConfidenceLevel,
  PredictionFusionMeta,
  PredictionRecommendation,
  PredictionRecommendationPayload,
  PredictionSnapshot,
  PredictionTrainingMeta,
  RawPredictionSnapshot,
} from '@/types/prediction'

export interface RawHistoryRecord {
  id?: number | string
  created_at?: string | null
  risk_level?: string | null
  risk_probability?: number | null
  confidence_level?: PredictionConfidenceLevel | null
  confidence_reasons?: string[] | null
  forecast_days?: number | null
  data_days_used?: number | null
  input_data?: RawPredictionSnapshot | null
  bp_forecast?: BloodPressureForecastPoint[] | null
  recommendations?: PredictionRecommendationPayload | null
  fusion_meta?: PredictionFusionMeta | null
  training_meta?: PredictionTrainingMeta | null
  [key: string]: unknown
}

export interface HistoryRecord extends RawHistoryRecord {
  input_data?: PredictionSnapshot | null
  bp_forecast?: BloodPressureForecastPoint[] | null
  recommendations?: PredictionRecommendationPayload | null
  confidence_reasons?: string[] | null
  fusion_meta?: PredictionFusionMeta | null
  training_meta?: PredictionTrainingMeta | null
}

export type HistoryDetail = HistoryRecord

export interface RawHistoryResponse {
  records?: RawHistoryRecord[] | null
  total?: number
  page?: number
  pages?: number
  [key: string]: unknown
}

export interface HistoryResponse extends RawHistoryResponse {
  records?: HistoryRecord[] | null
}
