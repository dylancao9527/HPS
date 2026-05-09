import { request } from '@/config/api'
import { normalizePredictionInputData } from '@/features/shared/normalizers'
import { normalizeRecommendations } from '@/features/prediction/api/predictApi'
import type { HistoryRecord, HistoryResponse, RawHistoryRecord, RawHistoryResponse } from '@/types/history'

export function normalizeHistoryRecord(record: RawHistoryRecord): HistoryRecord {
  return {
    ...record,
    input_data: normalizePredictionInputData(record.input_data),
    recommendations: normalizeRecommendations(record.recommendations),
  }
}

export function normalizeHistoryResponse(payload: RawHistoryResponse): HistoryResponse {
  return {
    ...payload,
    records: Array.isArray(payload.records)
      ? payload.records.map((record) => normalizeHistoryRecord(record))
      : payload.records,
  }
}

export async function getPredictions(page = 1, startDate = '', endDate = ''): Promise<HistoryResponse> {
  let url = `/predictions?page=${page}&per_page=10`
  if (startDate) url += `&start_date=${startDate}`
  if (endDate) url += `&end_date=${endDate}`

  const data = await request<RawHistoryResponse>(url)
  return normalizeHistoryResponse(data)
}

export async function deletePrediction(id: number | string): Promise<unknown> {
  return request(`/predictions/${id}`, { method: 'DELETE' })
}

export async function batchDeletePredictions(ids: Array<number | string>): Promise<unknown> {
  return request('/predictions/batch', {
    method: 'DELETE',
    body: JSON.stringify({ ids }),
  })
}
