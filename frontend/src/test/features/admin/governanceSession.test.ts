import { describe, expect, it } from 'vitest'
import {
  buildPredictionAuditFilterChips,
  buildPredictionAuditQueryString,
  buildPredictionGovernanceExportQueryString,
  normalizePredictionAuditDetail,
  normalizePredictionAuditFilters,
  resolveSelectedPredictionId,
} from '@/features/admin/governanceSession'

describe('admin governance session', () => {
  it('normalizes filters and builds filter chips for the page header', () => {
    const filters = normalizePredictionAuditFilters({
      riskLevel: 'high',
      confidenceLevel: 'low',
      hasAnomaly: 'true',
      anomalyType: 'high_risk_low_confidence',
    })

    expect(buildPredictionAuditFilterChips(filters)).toEqual([
      '风险: 高风险',
      '置信度: 低',
      '仅异常',
      '异常: 高风险且低置信度',
    ])

    expect(
      buildPredictionAuditFilterChips({
        ...filters,
        anomalyType: 'missing_key_profile_fields',
      }),
    ).toContain('异常: 模型输入字段缺失')
  })

  it('builds list and export query strings from the same filter contract', () => {
    const filters = {
      riskLevel: 'medium',
      confidenceLevel: 'low',
      hasAnomaly: 'false',
      anomalyType: 'insufficient_data_prediction',
    }

    expect(buildPredictionAuditQueryString({ page: 2, perPage: 20, filters })).toBe(
      'page=2&per_page=20&risk_level=medium&confidence_level=low&anomaly_type=insufficient_data_prediction&has_anomaly=false',
    )
    expect(buildPredictionGovernanceExportQueryString(filters)).toBe(
      'risk_level=medium&confidence_level=low&anomaly_type=insufficient_data_prediction&has_anomaly=false',
    )
  })

  it('keeps selected detail when the row remains available', () => {
    const records = [
      {
        prediction_id: 901,
        risk_level: null,
        risk_probability: null,
        confidence_level: null,
        data_days_used: null,
        input_data: null,
        anomaly_flags: [],
        created_at: null,
      },
      {
        prediction_id: 902,
        risk_level: null,
        risk_probability: null,
        confidence_level: null,
        data_days_used: null,
        input_data: null,
        anomaly_flags: [],
        created_at: null,
      },
    ]

    expect(resolveSelectedPredictionId(records, 902)).toBe(902)
    expect(resolveSelectedPredictionId(records, 999)).toBe(901)
    expect(resolveSelectedPredictionId([], 999)).toBeNull()
  })

  it('normalizes audit detail input aliases for governance detail views', () => {
    const detail = normalizePredictionAuditDetail({
      prediction_id: 901,
      input_data: { BMI: 27.4, BPMeds: 1, currentSmoker: 0 },
      forecast_summary: { forecast_days: 7 },
      confidence_reasons: ['short_history'],
      recommendations: [{ topic: 'follow_up' }],
    })

    expect(detail.input_data?.bmi).toBe(27.4)
    expect(detail.input_data?.bp_meds).toBe(1)
    expect(detail.input_data?.current_smoker).toBe(0)
    expect(detail.forecast_summary).toEqual({ forecast_days: 7 })
    expect(detail.confidence_reasons).toEqual(['short_history'])
  })
})
