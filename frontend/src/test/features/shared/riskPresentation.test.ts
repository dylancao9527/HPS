import { describe, expect, it } from 'vitest'
import {
  CONFIDENCE_LEVEL_FILTER_OPTIONS,
  RISK_LEVEL_FILTER_OPTIONS,
  confidenceLabels,
  formatConfidenceLevelLabel,
  formatRiskLevelLabel,
  formatRiskProbability,
  getBloodPressureTrendText,
  getRiskToneKey,
} from '@/features/shared/riskPresentation'

describe('risk presentation', () => {
  it('formats risk levels consistently for UI labels and tone keys', () => {
    expect(formatRiskLevelLabel('高风险')).toBe('高风险')
    expect(formatRiskLevelLabel('medium')).toBe('中风险')
    expect(formatRiskLevelLabel('low')).toBe('低风险')
    expect(formatRiskLevelLabel(null)).toBe('—')
    expect(formatRiskLevelLabel('unknown')).toBe('未知')

    expect(getRiskToneKey('高风险')).toBe('high')
    expect(getRiskToneKey('medium')).toBe('medium')
    expect(getRiskToneKey('unexpected')).toBe('custom')
  })

  it('formats risk probabilities without inventing missing values', () => {
    expect(formatRiskProbability(0.2364)).toBe('23.6%')
    expect(formatRiskProbability(1)).toBe('100.0%')
    expect(formatRiskProbability(null)).toBe('—')
  })

  it('formats confidence labels and filter options with Chinese display text', () => {
    expect(confidenceLabels).toEqual({
      low: '低',
      medium: '中',
      high: '高',
    })
    expect(formatConfidenceLevelLabel('high')).toBe('高')
    expect(formatConfidenceLevelLabel('unknown')).toBe('未知')
    expect(formatConfidenceLevelLabel(null)).toBe('—')

    expect(RISK_LEVEL_FILTER_OPTIONS.map((option) => option.label)).toEqual([
      '全部',
      '高风险',
      '中风险',
      '低风险',
    ])
    expect(CONFIDENCE_LEVEL_FILTER_OPTIONS.map((option) => option.label)).toEqual([
      '全部',
      '高',
      '中',
      '低',
    ])
  })

  it('derives shared blood pressure trend text for prediction and history contexts', () => {
    const upwardForecast = [
      { day: 1, systolic: 132, diastolic: 82 },
      { day: 7, systolic: 138, diastolic: 86 },
    ]
    const stableForecast = [
      { day: 1, systolic: 132, diastolic: 82 },
      { day: 7, systolic: 134, diastolic: 83 },
    ]

    expect(getBloodPressureTrendText(upwardForecast, 'prediction')).toBe(
      '未来几天血压整体有上升趋势，建议加强监测',
    )
    expect(getBloodPressureTrendText(upwardForecast, 'history')).toBe('整体有上升趋势')
    expect(getBloodPressureTrendText(stableForecast, 'history')).toBe('整体较为平稳')
    expect(getBloodPressureTrendText([], 'prediction')).toBe('未来几天整体趋势可作为日常参考')
  })
})
