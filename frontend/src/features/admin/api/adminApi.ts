import { API_BASE, request } from '@/config/api'
import {
  buildPredictionAuditQueryString,
  buildPredictionGovernanceExportQueryString,
  normalizePredictionAuditDetail,
  normalizePredictionAuditListResponse,
  normalizePredictionGovernanceSummary,
} from '@/features/admin/governanceSession'
import type { PredictionAuditFilters } from '@/features/admin/governanceSession'
import type {
  AdminStats,
  AdminUserUpdateInput,
  AdminUsersResponse,
  PredictionAuditDetail,
  PredictionAuditListResponse,
  PredictionGovernanceSummary,
  RawPredictionAuditDetail,
  RawPredictionAuditListResponse,
  RawPredictionGovernanceSummary,
} from '@/types/admin'

export type { PredictionAuditFilters } from '@/features/admin/governanceSession'

interface ListPredictionAuditsParams {
  page?: number
  perPage?: number
  filters?: Partial<PredictionAuditFilters>
}

interface GovernanceStatsResponse {
  governance?: RawPredictionGovernanceSummary | null
}

export async function getUsers(page: number = 1): Promise<AdminUsersResponse> {
  return request<AdminUsersResponse>(`/admin/users?page=${page}`)
}

export async function deleteUser(id: number | string): Promise<Record<string, never>> {
  return request<Record<string, never>>(`/admin/users/${encodeURIComponent(String(id))}`, { method: 'DELETE' })
}

export async function batchDeleteUsers(ids: Array<number | string>): Promise<Record<string, never>> {
  return request<Record<string, never>>('/admin/users/batch', {
    method: 'DELETE',
    body: JSON.stringify({ ids }),
  })
}

export async function updateUser(id: number | string, data: AdminUserUpdateInput): Promise<Record<string, never>> {
  return request<Record<string, never>>(`/admin/users/${encodeURIComponent(String(id))}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function getStats(): Promise<AdminStats> {
  return request<AdminStats>('/admin/stats')
}

export async function getPredictionGovernanceSummary(): Promise<PredictionGovernanceSummary> {
  const data = await request<GovernanceStatsResponse>('/admin/stats')
  return normalizePredictionGovernanceSummary(data.governance)
}

export async function listPredictionAudits({
  page = 1,
  perPage = 20,
  filters = {},
}: ListPredictionAuditsParams = {}): Promise<PredictionAuditListResponse> {
  const query = buildPredictionAuditQueryString({ page, perPage, filters })
  const data = await request<RawPredictionAuditListResponse>(`/admin/governance/predictions?${query}`)
  return normalizePredictionAuditListResponse(data)
}

export async function getPredictionAuditDetail(
  predictionId: number | string,
): Promise<PredictionAuditDetail> {
  const data = await request<RawPredictionAuditDetail>(`/admin/governance/predictions/${predictionId}`)
  return normalizePredictionAuditDetail(data)
}

async function fetchAdminBlob(path: string): Promise<Blob> {
  const token = localStorage.getItem('token')
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'GET',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || '下载失败')
  }

  return response.blob()
}

export async function downloadTrainingExport(): Promise<Blob> {
  return fetchAdminBlob('/admin/export/training')
}

export async function downloadPredictionGovernanceExport(
  filters: Partial<PredictionAuditFilters> = {},
): Promise<Blob> {
  const query = buildPredictionGovernanceExportQueryString(filters)
  const suffix = query ? `?${query}` : ''
  return fetchAdminBlob(`/admin/governance/export${suffix}`)
}
