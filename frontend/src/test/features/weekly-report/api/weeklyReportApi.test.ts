import { beforeEach, describe, expect, it, vi } from 'vitest'
import { request } from '@/config/api'
import { getWeeklyReport } from '@/features/weekly-report/api/weeklyReportApi'

vi.mock('@/config/api', () => ({
  request: vi.fn(),
}))

const mockedRequest = vi.mocked(request)

describe('weekly report API', () => {
  beforeEach(() => {
    mockedRequest.mockReset()
  })

  it('requests the canonical weekly report route', async () => {
    mockedRequest.mockResolvedValueOnce({ current_period: '', previous_period: '' })

    await getWeeklyReport()

    expect(mockedRequest).toHaveBeenCalledWith('/weekly-report')
  })
})
