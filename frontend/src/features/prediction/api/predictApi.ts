import { request } from '@/config/api'
import { normalizePredictionInputData } from '@/features/shared/normalizers'
import type {
  BPDataStatus,
  GuidelineTopicCard,
  PredictionRecommendation,
  PredictionRecommendationPayload,
  PredictionResult,
  RawPredictionResult,
} from '@/types/prediction'

export const USER_FORECAST_DAYS = 7

function isTopicCard(item: unknown): item is GuidelineTopicCard {
  return typeof item === 'object' && item !== null && 'topic' in item && 'summary' in item
}

export function normalizeRecommendations(payload: unknown): PredictionRecommendationPayload | null {
  if (!Array.isArray(payload) || payload.length === 0) return null
  if (isTopicCard(payload[0])) return payload as GuidelineTopicCard[]
  return payload as PredictionRecommendation[]
}

export function normalizePredictionResponse(payload: RawPredictionResult): PredictionResult {
  return {
    ...payload,
    input_data: normalizePredictionInputData(payload.input_data),
    recommendations: normalizeRecommendations(payload.recommendations),
  }
}

export async function predictRisk(): Promise<PredictionResult> {
  const data = await request<RawPredictionResult>('/predict', {
    method: 'POST',
    body: JSON.stringify({ forecast_days: USER_FORECAST_DAYS }),
  })

  return normalizePredictionResponse(data)
}

export async function getBPDataStatus(): Promise<BPDataStatus> {
  return request<BPDataStatus>(`/bp-data-status?forecast_days=${USER_FORECAST_DAYS}`)
}
