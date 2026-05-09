export const anomalyFlagLabels: Record<string, string> = {
  high_risk_without_recommendation: '高风险但无建议',
  high_risk_low_confidence: '高风险且低置信度',
  insufficient_data_prediction: '数据不足仍预测',
  missing_key_profile_fields: '模型输入字段缺失',
  elevated_forecast_low_risk: '预测血压偏高但低风险',
}

export const ANOMALY_TYPE_FILTER_OPTIONS = [
  { value: '', label: '全部异常类型' },
  ...Object.entries(anomalyFlagLabels).map(([value, label]) => ({ value, label })),
] as const

export function formatAnomalyFlagLabel(flag: string): string {
  return anomalyFlagLabels[flag] ?? flag
}

export function formatAnomalyFlagList(flags?: string[] | null): string {
  if (!flags || !flags.length) return '无'
  return flags.map(formatAnomalyFlagLabel).join(' | ')
}

export function formatPercentRate(value: number | null | undefined): string {
  const numericValue = typeof value === 'number' ? value : 0
  return `${(numericValue * 100).toFixed(1)}%`
}
