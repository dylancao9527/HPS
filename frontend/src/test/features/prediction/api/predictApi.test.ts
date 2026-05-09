import { beforeEach, describe, expect, it, vi } from 'vitest'
import { request } from '@/config/api'
import { getBPDataStatus, predictRisk } from '@/features/prediction/api/predictApi'

vi.mock('@/config/api', () => ({
  request: vi.fn(),
}))

const mockedRequest = vi.mocked(request)

describe('prediction API forecast period contract', () => {
  beforeEach(() => {
    mockedRequest.mockReset()
  })

  it('always requests the fixed future 7 day prediction', async () => {
    mockedRequest.mockResolvedValueOnce({ risk_probability: 0.42 })

    await predictRisk()

    expect(mockedRequest).toHaveBeenCalledWith('/predict', {
      method: 'POST',
      body: JSON.stringify({ forecast_days: 7 }),
    })
  })

  it('checks blood pressure readiness for the fixed future 7 day period', async () => {
    mockedRequest.mockResolvedValueOnce({ forecast_days: 7 })

    await getBPDataStatus()

    expect(mockedRequest).toHaveBeenCalledWith('/bp-data-status?forecast_days=7')
  })
})
