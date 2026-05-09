import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import PredictionPage from '@/pages/PredictionPage'

const predictionSessionMock = vi.hoisted(() => vi.fn())

vi.mock('@/features/health-tasks', async () => {
  const React = await import('react')
  return {
    QuickBPRecordModal: () => null,
    TodayHealthTasksPanel: () => React.createElement('div', null, '今日任务'),
  }
})

vi.mock('@/features/prediction', async () => {
  const React = await import('react')
  const actual = await vi.importActual<typeof import('@/features/prediction')>('@/features/prediction')
  return {
    ...actual,
    PredictionChartPanel: () => React.createElement('div', null, '未来7天血压趋势图'),
    PredictionForm: () => React.createElement('div', null, '预测准备'),
    PredictionInsightPanel: () => React.createElement('div', null, '关键影响因素与历史对比'),
    PredictionRecommendationPanel: () => React.createElement('div', null, '健康建议'),
    usePredictionPageSession: predictionSessionMock,
  }
})

function makeSession() {
  return {
    comparison: null,
    comparisonLoading: false,
    confidenceLabel: '中',
    detailsOpen: false,
    handleReset: vi.fn(),
    handleResult: vi.fn(),
    healthTasks: {
      error: '',
      loading: false,
      onQuickRecord: vi.fn(),
      onRetry: vi.fn(),
      summary: null,
    },
    isCachedResult: true,
    isUsingMedication: false,
    quickRecord: {
      error: '',
      loading: false,
      onClose: vi.fn(),
      onSubmit: vi.fn(),
      open: false,
    },
    result: {
      id: 901,
      risk_probability: 0.421,
      risk_level: '中风险',
      cache_mode: 'model_reuse',
      confidence_level: 'medium',
      data_days_used: 12,
      forecast_days: 7,
      bp_forecast: [
        { day: 1, systolic: 132, diastolic: 84 },
        { day: 2, systolic: 134, diastolic: 85 },
      ],
      recommendations: [
        {
          topic: 'follow_up',
          summary: '继续记录血压。',
          reason: '未来7天血压趋势平稳。',
          actions: ['每天固定时间测量血压。'],
        },
      ],
    },
    statusRefreshKey: 0,
    toggleDetails: vi.fn(),
    trendText: '未来7天血压趋势整体平稳。',
  }
}

describe('PredictionPage user summary', () => {
  it('shows a simple 7 day risk summary without professional model detail', () => {
    predictionSessionMock.mockReturnValue(makeSession())

    render(<PredictionPage />)

    expect(screen.getByText('高血压风险概率')).toBeInTheDocument()
    expect(screen.getByText('风险等级')).toBeInTheDocument()
    expect(screen.getByText('未来7天血压趋势图')).toBeInTheDocument()
    expect(screen.getByText('健康建议')).toBeInTheDocument()
    expect(screen.getByText('仅作健康管理参考')).toBeInTheDocument()

    expect(screen.queryByText(/Prophet|LightGBM|级联模型|置信度|模型复用|参考记录天数|详细解释|关键影响因素|历史对比/)).not.toBeInTheDocument()
  })
})
