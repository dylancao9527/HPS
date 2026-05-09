import { normalizePredictionInputData } from '@/features/shared/normalizers'
import type {
  PredictionAuditDetail,
  PredictionAuditListResponse,
  PredictionAuditRecord,
  PredictionGovernanceSummary,
  RawPredictionAuditDetail,
  RawPredictionAuditListResponse,
  RawPredictionAuditRecord,
  RawPredictionGovernanceSummary,
} from '@/types/admin'
import { formatAnomalyFlagLabel } from '@/features/admin/governancePresentation'
import {
  formatConfidenceLevelLabel,
  formatRiskLevelLabel,
} from '@/features/shared/riskPresentation'

export interface PredictionAuditFilters {
  riskLevel: string
  confidenceLevel: string
  hasAnomaly: string
  anomalyType: string
}

export const DEFAULT_PREDICTION_AUDIT_FILTERS: PredictionAuditFilters = {
  riskLevel: '',
  confidenceLevel: '',
  hasAnomaly: '',
  anomalyType: '',
}

interface BuildAuditQueryParams {
  page?: number
  perPage?: number
  filters?: Partial<PredictionAuditFilters>
}

export function normalizePredictionAuditFilters(
  filters: Partial<PredictionAuditFilters> = {},
): PredictionAuditFilters {
  return {
    riskLevel: filters.riskLevel ?? '',
    confidenceLevel: filters.confidenceLevel ?? '',
    hasAnomaly: filters.hasAnomaly ?? '',
    anomalyType: filters.anomalyType ?? '',
  }
}

function appendFilterParams(query: URLSearchParams, filters: Partial<PredictionAuditFilters>): void {
  if (filters.riskLevel) query.set('risk_level', filters.riskLevel)
  if (filters.confidenceLevel) query.set('confidence_level', filters.confidenceLevel)
  if (filters.anomalyType) query.set('anomaly_type', filters.anomalyType)
  if (filters.hasAnomaly !== '' && filters.hasAnomaly !== undefined && filters.hasAnomaly !== null) {
    query.set('has_anomaly', String(filters.hasAnomaly))
  }
}

export function buildPredictionAuditQueryString({
  page = 1,
  perPage = 20,
  filters = {},
}: BuildAuditQueryParams = {}): string {
  const query = new URLSearchParams({ page: String(page), per_page: String(perPage) })
  appendFilterParams(query, normalizePredictionAuditFilters(filters))
  return query.toString()
}

export function buildPredictionGovernanceExportQueryString(
  filters: Partial<PredictionAuditFilters> = {},
): string {
  const query = new URLSearchParams()
  appendFilterParams(query, normalizePredictionAuditFilters(filters))
  return query.toString()
}

export function buildPredictionAuditFilterChips(filters: PredictionAuditFilters): string[] {
  const chips: string[] = []
  if (filters.riskLevel) chips.push(`风险: ${formatRiskLevelLabel(filters.riskLevel)}`)
  if (filters.confidenceLevel) chips.push(`置信度: ${formatConfidenceLevelLabel(filters.confidenceLevel)}`)
  if (filters.hasAnomaly === 'true') chips.push('仅异常')
  if (filters.hasAnomaly === 'false') chips.push('仅正常')
  if (filters.anomalyType) chips.push(`异常: ${formatAnomalyFlagLabel(filters.anomalyType)}`)
  return chips
}

export function resolveSelectedPredictionId(
  records: PredictionAuditRecord[],
  previous: number | string | null,
): number | string | null {
  if (previous && records.some((row) => row.prediction_id === previous)) {
    return previous
  }
  return records[0]?.prediction_id ?? null
}

export function normalizePredictionGovernanceSummary(
  summary: RawPredictionGovernanceSummary | null | undefined,
): PredictionGovernanceSummary {
  if (!summary || typeof summary !== 'object') {
    return {
      total_predictions: 0,
      risk_distribution: {},
      confidence_distribution: {},
      anomaly_counts: {},
      high_risk_predictions: 0,
      low_confidence_predictions: 0,
      low_confidence_rate: 0,
      anomaly_predictions: 0,
      insufficient_data_predictions: 0,
      prophet_model_reuse_count: 0,
      prophet_model_retrain_count: 0,
    }
  }

  return {
    total_predictions: typeof summary.total_predictions === 'number' ? summary.total_predictions : 0,
    risk_distribution: summary.risk_distribution ?? {},
    confidence_distribution: summary.confidence_distribution ?? {},
    anomaly_counts: summary.anomaly_counts ?? {},
    high_risk_predictions: typeof summary.high_risk_predictions === 'number' ? summary.high_risk_predictions : 0,
    low_confidence_predictions: typeof summary.low_confidence_predictions === 'number' ? summary.low_confidence_predictions : 0,
    low_confidence_rate: typeof summary.low_confidence_rate === 'number' ? summary.low_confidence_rate : 0,
    anomaly_predictions: typeof summary.anomaly_predictions === 'number' ? summary.anomaly_predictions : 0,
    insufficient_data_predictions: typeof summary.insufficient_data_predictions === 'number' ? summary.insufficient_data_predictions : 0,
    prophet_model_reuse_count: typeof summary.prophet_model_reuse_count === 'number' ? summary.prophet_model_reuse_count : 0,
    prophet_model_retrain_count: typeof summary.prophet_model_retrain_count === 'number' ? summary.prophet_model_retrain_count : 0,
  }
}

export function normalizePredictionAuditRecord(record: RawPredictionAuditRecord | null | undefined): PredictionAuditRecord {
  if (!record || typeof record !== 'object') {
    return {
      prediction_id: null,
      risk_level: null,
      risk_probability: null,
      confidence_level: null,
      data_days_used: null,
      input_data: null,
      anomaly_flags: [],
      created_at: null,
    }
  }

  return {
    prediction_id: record.prediction_id ?? null,
    risk_level: record.risk_level ?? null,
    risk_probability: typeof record.risk_probability === 'number' ? record.risk_probability : null,
    confidence_level: record.confidence_level ?? null,
    data_days_used: typeof record.data_days_used === 'number' ? record.data_days_used : null,
    input_data: normalizePredictionInputData(record.input_data) ?? null,
    anomaly_flags: Array.isArray(record.anomaly_flags) ? record.anomaly_flags.filter((flag): flag is string => typeof flag === 'string') : [],
    created_at: record.created_at ?? null,
  }
}

export function normalizePredictionAuditListResponse(
  payload: RawPredictionAuditListResponse | null | undefined,
): PredictionAuditListResponse {
  if (!payload || typeof payload !== 'object') {
    return {
      records: [],
      total: 0,
      page: 1,
      pages: 1,
    }
  }

  return {
    records: Array.isArray(payload.records)
      ? payload.records.map((record) => normalizePredictionAuditRecord(record))
      : [],
    total: typeof payload.total === 'number' ? payload.total : 0,
    page: typeof payload.page === 'number' ? payload.page : 1,
    pages: typeof payload.pages === 'number' ? payload.pages : 1,
  }
}

export function normalizePredictionAuditDetail(
  payload: RawPredictionAuditDetail | null | undefined,
): PredictionAuditDetail {
  const record = normalizePredictionAuditRecord(payload)

  if (!payload || typeof payload !== 'object') {
    return {
      ...record,
      fusion_meta: {},
      forecast_summary: {},
      confidence_reasons: [],
      recommendations: [],
    }
  }

  return {
    ...record,
    fusion_meta: payload.fusion_meta ?? {},
    forecast_summary: payload.forecast_summary ?? {},
    confidence_reasons: Array.isArray(payload.confidence_reasons) ? payload.confidence_reasons : [],
    recommendations: Array.isArray(payload.recommendations) ? payload.recommendations : [],
  }
}
