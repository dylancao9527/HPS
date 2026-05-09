import type { BloodPressureForecastPoint, PredictionSnapshot } from '@/types/prediction'
import {
  confidenceLabels,
  formatConfidenceLevelLabel,
  formatRiskLevelLabel,
  formatRiskProbability,
  getBloodPressureTrendText,
  getRiskToneClass as getSharedRiskToneClass,
} from '@/features/shared/riskPresentation'

export {
  confidenceLabels,
  formatConfidenceLevelLabel,
  formatRiskLevelLabel,
  formatRiskProbability,
}

export function formatGender(input?: PredictionSnapshot | null): string {
  if (input?.male === 1 || input?.male === '1') return '男'
  if (input?.male === 0 || input?.male === '0') return '女'
  if (input?.gender === 'Male') return '男'
  if (input?.gender === 'Female') return '女'
  return '-'
}

export function formatYesNo(value: unknown): string {
  if (value === 1 || value === '1' || value === 'Yes') return '是'
  if (value === 0 || value === '0' || value === 'No') return '否'
  return '-'
}

export function getSnapshotValue(value: unknown): string | number {
  if (value === undefined || value === null || value === '') return '-'
  return value as string | number
}

export function getHistoryTrendText(bpForecast?: BloodPressureForecastPoint[] | null): string {
  return getBloodPressureTrendText(bpForecast, 'history')
}

export function getRiskToneClass(riskLevel?: string | null): string {
  return getSharedRiskToneClass(riskLevel, 'history-risk-badge')
}

export function formatDateTime(value?: string | null): string {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}
