import type { ExplanationReason, PredictionComparisonMetric } from '@/features/prediction/explanationTypes'

export function toNumber(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
}

export function toBinary(value: unknown): number | null {
  if (value === 1 || value === '1' || value === 'Yes' || value === true) return 1
  if (value === 0 || value === '0' || value === 'No' || value === false) return 0
  return null
}

export function formatNumber(value: number | null, digits = 1): string {
  if (value == null) return '-'
  return Number.isInteger(value) ? String(value) : value.toFixed(digits)
}

export function formatMetricValue(value: unknown, unit = ''): string {
  const numeric = toNumber(value)
  if (numeric == null) return '-'
  return `${formatNumber(numeric)}${unit}`
}

export function normalizeCodes(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value.filter((item): item is string => typeof item === 'string' && item.trim() !== '')
}

export function buildReasonList(codes: unknown, catalog: Record<string, Omit<ExplanationReason, 'code'>>): ExplanationReason[] {
  return normalizeCodes(codes).map((code) => ({
    code,
    label: catalog[code]?.label || code,
    description: catalog[code]?.description || '该规则参与了本次结果的解释，请结合当前输入数据和趋势信息综合理解。',
  }))
}

export function buildProbabilitySummary(deltaProbability: number | null, previousRiskLevel?: string | null, currentRiskLevel?: string | null): string {
  const levelChanged = previousRiskLevel && currentRiskLevel && previousRiskLevel !== currentRiskLevel
  if (deltaProbability == null) {
    return levelChanged
      ? `风险等级由 ${previousRiskLevel} 变为 ${currentRiskLevel}。`
      : '已找到上一条预测记录，可用于观察当前结果是否发生明显变化。'
  }

  const absDelta = Math.abs(deltaProbability)
  const deltaText = `${absDelta.toFixed(1)} 个百分点`
  if (absDelta < 1) {
    return levelChanged
      ? `风险概率变化不大，但风险等级由 ${previousRiskLevel} 变为 ${currentRiskLevel}。`
      : '与上一次预测相比，整体风险基本持平。'
  }

  if (deltaProbability > 0) {
    return levelChanged
      ? `与上一次相比，风险上升 ${deltaText}，风险等级由 ${previousRiskLevel} 变为 ${currentRiskLevel}。`
      : `与上一次相比，风险上升 ${deltaText}。`
  }

  return levelChanged
    ? `与上一次相比，风险下降 ${deltaText}，风险等级由 ${previousRiskLevel} 变为 ${currentRiskLevel}。`
    : `与上一次相比，风险下降 ${deltaText}。`
}

export function buildMetricDelta(currentValue: unknown, previousValue: unknown, unit = ''): PredictionComparisonMetric['delta'] {
  const current = toNumber(currentValue)
  const previous = toNumber(previousValue)
  if (current == null || previous == null) return '—'
  const delta = current - previous
  if (Math.abs(delta) < 0.05) return '基本持平'
  const sign = delta > 0 ? '+' : ''
  return `${sign}${formatNumber(delta)}${unit}`
}

export function resolveMetricTone(currentValue: unknown, previousValue: unknown): PredictionComparisonMetric['tone'] {
  const current = toNumber(currentValue)
  const previous = toNumber(previousValue)
  if (current == null || previous == null || Math.abs(current - previous) < 0.05) return 'neutral'
  return current > previous ? 'increase' : 'decrease'
}
