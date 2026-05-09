import { describe, expect, it } from 'vitest'
import {
  ANOMALY_TYPE_FILTER_OPTIONS,
  formatAnomalyFlagLabel,
  formatPercentRate,
} from '@/features/admin/governancePresentation'

describe('admin governance presentation', () => {
  it('formats anomaly labels and core metric rates', () => {
    expect(formatAnomalyFlagLabel('high_risk_low_confidence')).toBe('高风险且低置信度')
    expect(formatAnomalyFlagLabel('unknown_flag')).toBe('unknown_flag')
    expect(formatPercentRate(0.3333)).toBe('33.3%')
    expect(ANOMALY_TYPE_FILTER_OPTIONS.map((option) => option.value)).toContain('insufficient_data_prediction')
  })
})
