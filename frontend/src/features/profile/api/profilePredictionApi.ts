import { request } from '@/config/api'
import type { ProfilePredictionTrendResponse } from '@/types/profile'

export async function getPredictionTrend(limit: number = 20): Promise<ProfilePredictionTrendResponse> {
  return request<ProfilePredictionTrendResponse>(`/profile/prediction-trend?limit=${limit}`)
}
