import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import PredictionForm from '@/features/prediction/components/PredictionForm'
import { getBPDataStatus, predictRisk } from '@/features/prediction/api/predictApi'

const authState = vi.hoisted(() => ({
  user: { profile_complete: true },
}))
const navigateMock = vi.hoisted(() => vi.fn())

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({ user: authState.user }),
}))

vi.mock('react-router-dom', () => ({
  useNavigate: () => navigateMock,
}))

vi.mock('@/features/prediction/api/predictApi', () => ({
  USER_FORECAST_DAYS: 7,
  getBPDataStatus: vi.fn(),
  predictRisk: vi.fn(),
}))

const mockedGetBPDataStatus = vi.mocked(getBPDataStatus)
const mockedPredictRisk = vi.mocked(predictRisk)

describe('PredictionForm', () => {
  afterEach(() => {
    cleanup()
  })

  beforeEach(() => {
    authState.user = { profile_complete: true }
    navigateMock.mockReset()
    mockedGetBPDataStatus.mockReset()
    mockedPredictRisk.mockReset()
  })

  it('uses fixed 7 day readiness without forecast period choices', async () => {
    mockedGetBPDataStatus.mockResolvedValueOnce({
      status: 'recommended',
      total_days: 21,
      total_records: 30,
      forecast_days: 7,
      meets_minimum: true,
      meets_recommended: true,
    })
    mockedPredictRisk.mockResolvedValueOnce({ risk_probability: 0.32 })
    const onResult = vi.fn()

    render(<PredictionForm onResult={onResult} />)

    expect(await screen.findByText('未来 7 天风险预测')).toBeInTheDocument()
    expect(screen.getByText('无需选择周期')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: '3 天' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: '14 天' })).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: '开始预测' }))

    await waitFor(() => expect(mockedPredictRisk).toHaveBeenCalledWith())
    expect(onResult).toHaveBeenCalledWith({ risk_probability: 0.32 })
  })

  it('does not prompt users to complete optional risk factors after a successful prediction', async () => {
    mockedGetBPDataStatus.mockResolvedValueOnce({
      status: 'recommended',
      total_days: 21,
      total_records: 30,
      forecast_days: 7,
      meets_minimum: true,
      meets_recommended: true,
    })
    mockedPredictRisk.mockResolvedValueOnce({
      risk_probability: 0.42,
      input_data: {
        age: 58,
        BMI: 25.1,
        currentSmoker: null,
        BPMeds: null,
        diabetes: null,
        totChol: null,
        glucose: null,
      },
      anomaly_flags: ['missing_key_profile_fields'],
    })
    const onResult = vi.fn()

    render(<PredictionForm onResult={onResult} />)

    fireEvent.click(await screen.findByRole('button', { name: '开始预测' }))

    await waitFor(() => expect(onResult).toHaveBeenCalled())
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    expect(screen.queryByText('模型输入字段缺失')).not.toBeInTheDocument()
    expect(screen.queryByText(/完善更多风险因素/)).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: '前往风险因素档案' })).not.toBeInTheDocument()
  })

  it('turns backend risk factor profile blocks into an actionable profile prompt', async () => {
    mockedGetBPDataStatus.mockResolvedValueOnce({
      status: 'recommended',
      total_days: 21,
      total_records: 30,
      forecast_days: 7,
      meets_minimum: true,
      meets_recommended: true,
    })
    mockedPredictRisk.mockRejectedValueOnce(new Error('请先完善风险因素档案'))

    render(<PredictionForm onResult={vi.fn()} />)

    fireEvent.click(await screen.findByRole('button', { name: '开始预测' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('请先完善风险因素档案')
    expect(screen.getByText('完善后再回到这里生成 7 天风险预测。')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: '前往风险因素档案' }))

    expect(navigateMock).toHaveBeenCalledWith('/profile?tab=risk-factors')
  })

  it('links incomplete readiness directly to the risk factor profile tab', async () => {
    authState.user = { profile_complete: false }
    mockedGetBPDataStatus.mockResolvedValueOnce({
      status: 'recommended',
      total_days: 21,
      total_records: 30,
      forecast_days: 7,
      meets_minimum: true,
      meets_recommended: true,
    })

    render(<PredictionForm onResult={vi.fn()} />)

    fireEvent.click(await screen.findByRole('button', { name: '前往填写' }))

    expect(screen.getByText('风险因素档案')).toBeInTheDocument()
    expect(navigateMock).toHaveBeenCalledWith('/profile?tab=risk-factors')
  })
})
