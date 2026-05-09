import { describe, expect, it } from 'vitest'
import {
  normalizePredictionAuditDetail,
  normalizePredictionAuditRecord,
} from '@/features/admin/governanceSession'

describe('admin prediction governance api normalization', () => {
  it('preserves prediction chain governance fields on audit records', () => {
    expect(normalizePredictionAuditRecord({
      prediction_id: 901,
      risk_level: '高风险',
      risk_probability: 0.8123,
      confidence_level: 'low',
      data_days_used: 2,
      anomaly_flags: ['high_risk_low_confidence'],
      input_data: { age: 56, BMI: 27.4, BPMeds: 1 },
      created_at: '2026-04-25T09:30:00',
    })).toMatchObject({
      prediction_id: 901,
      risk_probability: 0.8123,
      data_days_used: 2,
      anomaly_flags: ['high_risk_low_confidence'],
    })
  })

  it('preserves forecast summary on audit detail', () => {
    expect(normalizePredictionAuditDetail({
      prediction_id: 901,
      forecast_summary: {
        forecast_days: 7,
        avg_sys: 142.1,
        avg_dia: 91.2,
        high_bp_days: 4,
      },
    })).toMatchObject({
      prediction_id: 901,
      forecast_summary: {
        forecast_days: 7,
        avg_sys: 142.1,
        avg_dia: 91.2,
        high_bp_days: 4,
      },
    })
  })
})
