import { describe, expect, it } from 'vitest'
import type { PredictionAuditDetail } from '@/types/admin'
import { buildAuditDetailPresentation } from '@/features/admin/auditDetailPresentation'

function makeDetail(overrides: Partial<PredictionAuditDetail> = {}): PredictionAuditDetail {
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
      heartRate: 72,
      totChol: 190,
      glucose: 96,
    },
    anomaly_flags: ['high_risk_low_confidence'],
    created_at: '2026-04-25T09:30:00',
    fusion_meta: {
      raw_probability: 0.6123,
      fused_probability: 0.6923,
      adjustment: 0.08,
      trend_adjustment: 0.06,
      medication_adjustment: 0.02,
      bp_meds_input: 1,
      bp_meds_model_value: 0,
      bp_meds_policy: 'neutralized_for_conservative_inference',
      reasons: ['high_bp_days'],
    },
    forecast_summary: {
      forecast_days: 7,
      avg_sys: 142.1,
      avg_dia: 91.2,
      max_sys: 150,
      max_dia: 96,
      high_bp_days: 4,
      elevated_bp_days: 7,
      high_bp_ratio: 0.5714,
      elevated_bp_ratio: 1,
    },
    confidence_reasons: ['insufficient_days', { reason_code: 'custom_signal', content: '自定义置信度说明' }],
    recommendations: [
      {
        topic: 'follow_up',
        summary: '预测血压处于2级高血压范围，建议定期随访。',
        reason: '未来7天血压均值偏高。',
        actions: ['连续记录家庭血压。'],
        source_label: '中国高血压防治指南（2024年修订版）',
      },
      {
        title: '旧格式建议',
        content: '保持低盐饮食。',
        priority: 'high',
        basis: '风险等级偏高。',
      },
    ],
    ...overrides,
  }
}

describe('admin audit detail presentation', () => {
  it('formats audit detail into domain sections without raw json blocks', () => {
    const presentation = buildAuditDetailPresentation(makeDetail())

    expect(presentation.inputRows).toContainEqual({ label: '年龄', value: '56 岁' })
    expect(presentation.inputRows).toContainEqual({ label: '收缩压', value: '142 mmHg' })
    expect(presentation.inputRows).toContainEqual({ label: '降压药', value: '是' })
    expect(presentation.fusionRows).toContainEqual({ label: '模型基础风险', value: '61.2%' })
    expect(presentation.fusionRows).toContainEqual({ label: '趋势修正', value: '+6.0 个百分点' })
    expect(presentation.forecastRows).toContainEqual({ label: '高血压范围占比', value: '57.1%' })

    expect(presentation.fusionReasons[0]).toMatchObject({
      code: 'high_bp_days',
      label: '预测期内出现高血压天数',
    })
    expect(presentation.confidenceReasons[0]).toMatchObject({
      code: 'insufficient_days',
      label: '历史记录天数偏少',
    })
    expect(presentation.confidenceReasons[1]).toMatchObject({
      code: 'custom_signal',
      description: '自定义置信度说明',
    })
    expect(presentation.recommendations[0]).toMatchObject({
      badge: '随访建议',
      summary: '预测血压处于2级高血压范围，建议定期随访。',
      actions: ['连续记录家庭血压。'],
    })
    expect(presentation.recommendations[1]).toMatchObject({
      badge: '重点干预',
      title: '旧格式建议',
      summary: '保持低盐饮食。',
    })
  })

  it('falls back to fusion trend summary when detail forecast summary is absent', () => {
    const presentation = buildAuditDetailPresentation(makeDetail({
      forecast_summary: {},
      fusion_meta: {
        trend_summary: {
          forecast_days: 7,
          avg_sys: 128,
          high_bp_days: 0,
        },
        reasons: [],
      },
    }))

    expect(presentation.forecastRows).toContainEqual({ label: '预测天数', value: '7 天' })
    expect(presentation.forecastRows).toContainEqual({ label: '平均收缩压', value: '128 mmHg' })
  })
})
