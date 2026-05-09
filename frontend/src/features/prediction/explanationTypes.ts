import type { PredictionFusionMeta, PredictionSnapshot } from '@/types/prediction'

export type InsightTone = 'high' | 'medium' | 'positive' | 'neutral'

export interface ExplanationReason {
  code: string
  label: string
  description: string
}

export interface PredictionInsightFactor {
  id: string
  title: string
  value: string
  tone: InsightTone
  description: string
}

export interface PredictionComparisonMetric {
  label: string
  current: string
  previous: string
  delta: string
  tone: 'increase' | 'decrease' | 'neutral'
}

export interface PredictionComparison {
  summary: string
  previousCreatedAt: string | null
  previousRiskLevel: string | null
  deltaProbability: number | null
  metrics: PredictionComparisonMetric[]
}

export interface PredictionInsightSource {
  input_data?: PredictionSnapshot | null
  fusion_meta?: PredictionFusionMeta | null
}
