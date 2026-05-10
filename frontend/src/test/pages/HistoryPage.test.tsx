import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import HistoryPage from '@/pages/HistoryPage'

const getPredictionsMock = vi.hoisted(() => vi.fn())
const batchDeletePredictionsMock = vi.hoisted(() => vi.fn())
const deletePredictionMock = vi.hoisted(() => vi.fn())
const confirmMock = vi.hoisted(() => vi.fn())
const showToastMock = vi.hoisted(() => vi.fn())

vi.mock('@/features/history', async () => {
  const actual = await vi.importActual<typeof import('@/features/history')>('@/features/history')
  return {
    ...actual,
    getPredictions: getPredictionsMock,
    batchDeletePredictions: batchDeletePredictionsMock,
    deletePrediction: deletePredictionMock,
  }
})

vi.mock('@/hooks/useFeedback', () => ({
  useFeedback: () => ({
    confirm: confirmMock,
    showToast: showToastMock,
  }),
}))

describe('HistoryPage batch selection', () => {
  it('batch deletes only records visible in the current list', async () => {
    getPredictionsMock
      .mockResolvedValueOnce({
        records: [
          {
            id: 1,
            created_at: '2026-05-01T08:00:00',
            risk_level: '低风险',
            risk_probability: 0.12,
            bp_forecast: [],
          },
        ],
        pages: 2,
      })
      .mockResolvedValueOnce({
        records: [
          {
            id: 2,
            created_at: '2026-05-02T08:00:00',
            risk_level: '高风险',
            risk_probability: 0.82,
            bp_forecast: [],
          },
        ],
        pages: 2,
      })
      .mockResolvedValueOnce({
        records: [
          {
            id: 2,
            created_at: '2026-05-02T08:00:00',
            risk_level: '高风险',
            risk_probability: 0.82,
            bp_forecast: [],
          },
        ],
        pages: 2,
      })
    confirmMock.mockResolvedValue(true)
    batchDeletePredictionsMock.mockResolvedValue({})

    render(<HistoryPage />)

    const firstPageCheckbox = await screen.findByLabelText(/选择 2026\/5\/1/)
    fireEvent.click(firstPageCheckbox)
    fireEvent.click(screen.getByRole('button', { name: '下一页' }))

    const secondPageCheckbox = await screen.findByLabelText(/选择 2026\/5\/2/)
    fireEvent.click(secondPageCheckbox)
    fireEvent.click(await screen.findByRole('button', { name: /批量删除/ }))

    await waitFor(() => {
      expect(batchDeletePredictionsMock).toHaveBeenCalledWith([2])
    })
  })
})
