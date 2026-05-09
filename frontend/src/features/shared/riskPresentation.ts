import type { BloodPressureForecastPoint, PredictionConfidenceLevel } from '@/types/prediction'

export type RiskToneKey = 'low' | 'medium' | 'high' | 'custom'
export type TrendTextContext = 'prediction' | 'history'

export const confidenceLabels: Record<PredictionConfidenceLevel, string> = {
  low: '低',
  medium: '中',
  high: '高',
}

const riskLevelLabels: Record<string, string> = {
  low: '低风险',
  medium: '中风险',
  high: '高风险',
  '低风险': '低风险',
  '中风险': '中风险',
  '高风险': '高风险',
}

const riskToneKeys: Record<string, Exclude<RiskToneKey, 'custom'>> = {
  low: 'low',
  medium: 'medium',
  high: 'high',
  '低风险': 'low',
  '中风险': 'medium',
  '高风险': 'high',
}

export const RISK_LEVEL_FILTER_OPTIONS = [
  { value: '', label: '全部' },
  { value: '高风险', label: '高风险' },
  { value: '中风险', label: '中风险' },
  { value: '低风险', label: '低风险' },
] as const

export const CONFIDENCE_LEVEL_FILTER_OPTIONS: Array<{
  value: '' | PredictionConfidenceLevel
  label: string
}> = [
  { value: '', label: '全部' },
  { value: 'high', label: confidenceLabels.high },
  { value: 'medium', label: confidenceLabels.medium },
  { value: 'low', label: confidenceLabels.low },
]

function isUnknownValue(value?: string | null): boolean {
  return value === 'unknown' || value === '未知'
}

export function formatRiskLevelLabel(value?: string | null, emptyLabel = '—'): string {
  if (!value) return emptyLabel
  if (isUnknownValue(value)) return '未知'
  return riskLevelLabels[value] ?? value
}

export function formatConfidenceLevelLabel(value?: string | null, emptyLabel = '—'): string {
  if (!value) return emptyLabel
  if (isUnknownValue(value)) return '未知'
  return confidenceLabels[value as PredictionConfidenceLevel] ?? value
}

export function formatRiskProbability(value?: number | null, emptyLabel = '—'): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return emptyLabel
  return `${(value * 100).toFixed(1)}%`
}

export function getRiskToneKey(value?: string | null): RiskToneKey {
  if (!value || isUnknownValue(value)) return 'custom'
  return riskToneKeys[value] ?? 'custom'
}

export function getRiskToneClass(value: string | null | undefined, classPrefix: string, fallback = ''): string {
  const tone = getRiskToneKey(value)
  if (tone === 'custom') return fallback
  return `${classPrefix}--${tone}`
}

export function getBloodPressureTrendText(
  bpForecast?: BloodPressureForecastPoint[] | null,
  context: TrendTextContext = 'prediction',
): string {
  const copy = context === 'history'
    ? {
        insufficient: '趋势参考',
        upward: '整体有上升趋势',
        downward: '整体有下降趋势',
        stable: '整体较为平稳',
      }
    : {
        insufficient: '未来几天整体趋势可作为日常参考',
        upward: '未来几天血压整体有上升趋势，建议加强监测',
        downward: '未来几天血压整体有下降趋势，可继续保持当前管理习惯',
        stable: '未来几天血压整体较为平稳，可继续日常监测',
      }

  if (!bpForecast || bpForecast.length < 2) return copy.insufficient

  const first = bpForecast[0]
  const last = bpForecast[bpForecast.length - 1]
  const sysDelta = (last?.systolic ?? 0) - (first?.systolic ?? 0)
  const diaDelta = (last?.diastolic ?? 0) - (first?.diastolic ?? 0)

  if (sysDelta >= 5 || diaDelta >= 3) return copy.upward
  if (sysDelta <= -5 || diaDelta <= -3) return copy.downward
  return copy.stable
}
