import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { PredictionAuditDetail } from '@/types/admin'
import PredictionAuditDetailCard from '@/features/admin/components/PredictionAuditDetailCard'

function makeDetail(): PredictionAuditDetail {
  return {
    prediction_id: 901,
    risk_level: '高风险',
    risk_probability: 0.8123,
    confidence_level: 'low',
    data_days_used: 2,
    input_data: {
      age: 56,
      male: 1,
      BMI: 27.4,
      BPMeds: 1,
      currentSmoker: 0,
      diabetes: 0,
      sysBP: 142,
      diaBP: 91,
    },
    anomaly_flags: ['high_risk_low_confidence'],
    created_at: '2026-04-25T09:30:00',
    fusion_meta: {
      raw_probability: 0.6123,
      fused_probability: 0.6923,
      trend_adjustment: 0.06,
      medication_adjustment: 0.02,
      reasons: ['high_bp_days'],
    },
    forecast_summary: {
      forecast_days: 7,
      avg_sys: 142.1,
      avg_dia: 91.2,
      high_bp_days: 4,
      high_bp_ratio: 0.5714,
    },
    confidence_reasons: ['insufficient_days'],
    recommendations: [],
  }
}

describe('PredictionAuditDetailCard', () => {
  it('keeps professional prediction details in admin governance', () => {
    const { container } = render(<PredictionAuditDetailCard detail={makeDetail()} />)

    expect(screen.getByText('预测结果治理明细 #901')).toBeInTheDocument()
    expect(screen.getByText('输入快照')).toBeInTheDocument()
    expect(screen.getByText('融合元数据')).toBeInTheDocument()
    expect(screen.getByText('模型基础风险')).toBeInTheDocument()
    expect(screen.getByText('趋势修正')).toBeInTheDocument()
    expect(screen.getByText('预测点摘要')).toBeInTheDocument()
    expect(screen.getByText('异常标记')).toBeInTheDocument()
    expect(screen.getByText('置信度原因')).toBeInTheDocument()
    expect(container.textContent).not.toMatch(/临床审核|人工改判/)
  })
})
