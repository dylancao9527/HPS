import type { HistoryRecord } from '@/types/history'
import type { PredictionResult } from '@/types/prediction'
import type { PredictionComparison, PredictionComparisonMetric } from '@/features/prediction/explanationTypes'
import { buildMetricDelta, buildProbabilitySummary, formatMetricValue, resolveMetricTone } from '@/features/prediction/explanationUtils'

export function formatProbability(value?: number | null): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return '-'
  return `${(value * 100).toFixed(1)}%`
}

export function formatSignedProbabilityDelta(value?: number | null): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return '—'
  const signed = value > 0 ? '+' : ''
  return `${signed}${value.toFixed(1)} 个百分点`
}

export function buildPredictionComparison(current: PredictionResult, previous?: HistoryRecord | null): PredictionComparison | null {
  if (!previous) return null

  const deltaProbability =
    typeof current.risk_probability === 'number' && typeof previous.risk_probability === 'number'
      ? (current.risk_probability - previous.risk_probability) * 100
      : null

  const metrics: PredictionComparisonMetric[] = [
    {
      label: '风险概率',
      current: formatProbability(current.risk_probability),
      previous: formatProbability(previous.risk_probability),
      delta: formatSignedProbabilityDelta(deltaProbability),
      tone:
        deltaProbability == null || Math.abs(deltaProbability) < 0.05
          ? 'neutral'
          : deltaProbability > 0
            ? 'increase'
            : 'decrease',
    },
    {
      label: '收缩压',
      current: formatMetricValue(current.input_data?.systolic_bp ?? current.input_data?.sysBP, ' mmHg'),
      previous: formatMetricValue(previous.input_data?.systolic_bp ?? previous.input_data?.sysBP, ' mmHg'),
      delta: buildMetricDelta(
        current.input_data?.systolic_bp ?? current.input_data?.sysBP,
        previous.input_data?.systolic_bp ?? previous.input_data?.sysBP,
        ' mmHg',
      ),
      tone: resolveMetricTone(
        current.input_data?.systolic_bp ?? current.input_data?.sysBP,
        previous.input_data?.systolic_bp ?? previous.input_data?.sysBP,
      ),
    },
    {
      label: '舒张压',
      current: formatMetricValue(current.input_data?.diastolic_bp ?? current.input_data?.diaBP, ' mmHg'),
      previous: formatMetricValue(previous.input_data?.diastolic_bp ?? previous.input_data?.diaBP, ' mmHg'),
      delta: buildMetricDelta(
        current.input_data?.diastolic_bp ?? current.input_data?.diaBP,
        previous.input_data?.diastolic_bp ?? previous.input_data?.diaBP,
        ' mmHg',
      ),
      tone: resolveMetricTone(
        current.input_data?.diastolic_bp ?? current.input_data?.diaBP,
        previous.input_data?.diastolic_bp ?? previous.input_data?.diaBP,
      ),
    },
    {
      label: 'BMI',
      current: formatMetricValue(current.input_data?.bmi ?? current.input_data?.BMI),
      previous: formatMetricValue(previous.input_data?.bmi ?? previous.input_data?.BMI),
      delta: buildMetricDelta(
        current.input_data?.bmi ?? current.input_data?.BMI,
        previous.input_data?.bmi ?? previous.input_data?.BMI,
      ),
      tone: resolveMetricTone(
        current.input_data?.bmi ?? current.input_data?.BMI,
        previous.input_data?.bmi ?? previous.input_data?.BMI,
      ),
    },
  ]

  return {
    summary: buildProbabilitySummary(deltaProbability, previous.risk_level, current.risk_level),
    previousCreatedAt: previous.created_at ?? null,
    previousRiskLevel: previous.risk_level ?? null,
    deltaProbability,
    metrics,
  }
}
