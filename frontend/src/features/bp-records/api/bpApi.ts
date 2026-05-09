import { request } from '@/config/api'
import type { BPRecord, BPRecordsResponse, CreateBPRecordInput } from '@/features/bp-records/types'

export async function getBPRecords(page: number = 1, perPage: number = 10): Promise<BPRecordsResponse> {
  return request<BPRecordsResponse>(`/bp-records?page=${page}&per_page=${perPage}`)
}

export async function addBPRecord(data: CreateBPRecordInput): Promise<BPRecord> {
  return request<BPRecord>('/bp-records', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function deleteBPRecord(id: number): Promise<Record<string, never>> {
  return request<Record<string, never>>(`/bp-records/${id}`, { method: 'DELETE' })
}

export async function batchDeleteBPRecords(ids: number[]): Promise<Record<string, never>> {
  return request<Record<string, never>>('/bp-records/batch', {
    method: 'DELETE',
    body: JSON.stringify({ ids }),
  })
}
