import { request } from '@/config/api'
import type { HealthTaskSummary } from '@/features/health-tasks/types'

export async function getTodayHealthTaskSummary(): Promise<HealthTaskSummary> {
  return request<HealthTaskSummary>('/health-tasks/today')
}
