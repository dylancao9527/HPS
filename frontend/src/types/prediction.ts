export type PredictionConfidenceLevel = 'low' | 'medium' | 'high'
export type PredictionCacheMode =
  | 'fresh_train'
  | 'model_reuse'
  | string
export type RecommendationPriority = 'high' | 'medium' | 'low' | string

export interface PredictionTrendSummary {
  forecast_days?: number | null
  avg_sys?: number | null
  avg_dia?: number | null
  max_sys?: number | null
  max_dia?: number | null
  sys_slope?: number | null
  dia_slope?: number | null
  sys_volatility?: number | null
  dia_volatility?: number | null
  high_bp_days?: number | null
  elevated_bp_days?: number | null
  high_bp_ratio?: number | null
  elevated_bp_ratio?: number | null
  [key: string]: unknown
}

export interface PredictionFusionMeta {
  raw_probability?: number | null
  fused_probability?: number | null
  adjustment?: number | null
  trend_adjustment?: number | null
  medication_adjustment?: number | null
  bp_meds_input?: number | string | null
  bp_meds_model_value?: number | string | null
  bp_meds_policy?: string | null
  reasons?: string[] | null
  trend_summary?: PredictionTrendSummary | null
  [key: string]: unknown
}

export interface PredictionTrainingMeta {
  aggregation_mode?: string | null
  parameter_profile?: string | null
  avg_measurements_per_day?: number | null
  recent_sys_range_mean?: number | null
  recent_dia_range_mean?: number | null
  confidence_level?: PredictionConfidenceLevel | null
  confidence_reasons?: string[] | null
  seasonality?: {
    weekly_enabled?: boolean | null
    monthly_enabled?: boolean | null
    [key: string]: unknown
  } | null
  [key: string]: unknown
}

export interface RawPredictionSnapshot {
  age?: number | string | null
  male?: number | string | null
  gender?: string | null
  BMI?: number | string | null
  bmi?: number | string | null
  sysBP?: number | string | null
  systolic_bp?: number | string | null
  diaBP?: number | string | null
  diastolic_bp?: number | string | null
  heartRate?: number | string | null
  heart_rate?: number | string | null
  currentSmoker?: number | string | null
  current_smoker?: number | string | null
  smoking?: number | string | null
  cigsPerDay?: number | string | null
  cigs_per_day?: number | string | null
  BPMeds?: number | string | null
  bp_meds?: number | string | null
  diabetes?: number | string | null
  glucose?: number | string | null
  totChol?: number | string | null
  tot_chol?: number | string | null
  cholesterol?: number | string | null
  [key: string]: unknown
}

export interface PredictionSnapshot extends RawPredictionSnapshot {
  bmi?: number | string | null
  systolic_bp?: number | string | null
  diastolic_bp?: number | string | null
  heart_rate?: number | string | null
  current_smoker?: number | string | null
  cigs_per_day?: number | string | null
  bp_meds?: number | string | null
  tot_chol?: number | string | null
}

export interface BloodPressureForecastPoint {
  day?: number | string | null
  date?: string | null
  systolic?: number | null
  diastolic?: number | null
  [key: string]: unknown
}

export interface PredictionRecommendation {
  title: string
  content: string
  priority?: RecommendationPriority | null
  basis?: string | null
  [key: string]: unknown
}

export interface GuidelineTopicCard {
  topic: string
  summary: string
  reason: string
  actions: string[]
  source_label?: string | null
}

export type PredictionRecommendationPayload =
  | PredictionRecommendation[]
  | GuidelineTopicCard[]

export interface RawPredictionResult {
  id?: number | string | null
  risk_probability?: number | null
  risk_level?: string | null
  risk_color?: string | null
  cache_mode?: PredictionCacheMode | null
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

export interface PredictionResult extends RawPredictionResult {
  id?: number | string | null
  input_data?: PredictionSnapshot | null
  bp_forecast?: BloodPressureForecastPoint[] | null
  recommendations?: PredictionRecommendationPayload | null
  confidence_reasons?: string[] | null
  fusion_meta?: PredictionFusionMeta | null
  training_meta?: PredictionTrainingMeta | null
}

export interface BPDataStatus {
  status?: 'no_data' | 'insufficient' | 'warning' | 'recommended' | string
  total_days?: number
  minimum_days?: number
  recommended_days_min?: number
  recommended_days_max?: number
  forecast_days?: number
  total_records?: number
  recommended_records_min?: number
  meets_minimum?: boolean
  meets_recommended?: boolean
  [key: string]: unknown
}
