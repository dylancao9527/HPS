import { request } from '@/config/api'
import type { WeeklyReportSummary } from '@/features/weekly-report/types'

export async function getWeeklyReport(): Promise<WeeklyReportSummary> {
  return request<WeeklyReportSummary>('/weekly-report')
}
