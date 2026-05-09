import type { PredictionSnapshot, RawPredictionSnapshot } from '@/types/prediction'

export interface AdminTrainingExportStats {
  exportable_samples: number
  positive_samples: number
  negative_samples: number
  positive_ratio: number
  diagnosis_labeled_samples: number
  rule_labeled_samples: number
  skipped_users: number
  recent_bp_avg_count: number
}

export interface AdminStats {
  total_users: number
  total_bp_records: number
  total_predictions: number
  today_users: number
  today_predictions: number
  training_export: AdminTrainingExportStats | null
}

export interface AdminUser {
  id: number | string
  username: string
  email: string | null
  role: string
  age?: number | null
  bmi?: number | null
  profile_complete?: boolean | null
  created_at: string | null
}

export interface AdminUsersResponse {
  users: AdminUser[]
  admins: AdminUser[]
  pages: number
  total?: number
  admin_total?: number
}

export interface AdminUserUpdateInput {
  password: string
}

export interface RawPredictionGovernanceSummary {
  total_predictions?: number | null
  risk_distribution?: Record<string, number> | null
  confidence_distribution?: Record<string, number> | null
  anomaly_counts?: Record<string, number> | null
  high_risk_predictions?: number | null
  low_confidence_predictions?: number | null
  low_confidence_rate?: number | null
  anomaly_predictions?: number | null
  insufficient_data_predictions?: number | null
  prophet_model_reuse_count?: number | null
  prophet_model_retrain_count?: number | null
  [key: string]: unknown
}

export interface PredictionGovernanceSummary {
  total_predictions: number
  risk_distribution: Record<string, number>
  confidence_distribution: Record<string, number>
  anomaly_counts: Record<string, number>
  high_risk_predictions: number
  low_confidence_predictions: number
  low_confidence_rate: number
  anomaly_predictions: number
  insufficient_data_predictions: number
  prophet_model_reuse_count: number
  prophet_model_retrain_count: number
}

export interface RawPredictionAuditRecord {
  prediction_id?: number | string | null
  risk_level?: string | null
  risk_probability?: number | null
  confidence_level?: string | null
  data_days_used?: number | null
  input_data?: RawPredictionSnapshot | null
  anomaly_flags?: string[] | null
  created_at?: string | null
  [key: string]: unknown
}

export interface PredictionAuditRecord {
  prediction_id: number | string | null
  risk_level: string | null
  risk_probability: number | null
  confidence_level: string | null
  data_days_used: number | null
  input_data: PredictionSnapshot | null
  anomaly_flags: string[]
  created_at: string | null
}

export interface RawPredictionAuditListResponse {
  records?: RawPredictionAuditRecord[] | null
  total?: number | null
  page?: number | null
  pages?: number | null
  [key: string]: unknown
}

export interface PredictionAuditListResponse {
  records: PredictionAuditRecord[]
  total: number
  page: number
  pages: number
}

export interface RawPredictionAuditDetail extends RawPredictionAuditRecord {
  fusion_meta?: Record<string, unknown> | null
  forecast_summary?: Record<string, unknown> | null
  confidence_reasons?: unknown[] | null
  recommendations?: unknown[] | null
}

export interface PredictionAuditDetail {
  prediction_id: number | string | null
  risk_level: string | null
  risk_probability: number | null
  confidence_level: string | null
  data_days_used: number | null
  input_data: PredictionSnapshot | null
  anomaly_flags: string[]
  created_at: string | null
  fusion_meta: Record<string, unknown>
  forecast_summary: Record<string, unknown>
  confidence_reasons: unknown[]
  recommendations: unknown[]
}
