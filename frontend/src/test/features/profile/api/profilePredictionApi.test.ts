import { beforeEach, describe, expect, it, vi } from 'vitest'
import { request } from '@/config/api'
import { getPredictionTrend } from '@/features/profile/api/profilePredictionApi'

vi.mock('@/config/api', () => ({
  request: vi.fn(),
}))

const mockedRequest = vi.mocked(request)

describe('profile prediction trend API', () => {
  beforeEach(() => {
    mockedRequest.mockReset()
  })

  it('requests the lightweight profile prediction trend route', async () => {
    mockedRequest.mockResolvedValueOnce({ records: [] })

    await getPredictionTrend(120)

    expect(mockedRequest).toHaveBeenCalledWith('/profile/prediction-trend?limit=120')
  })
})
