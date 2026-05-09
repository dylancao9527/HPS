import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { HistoryDetail } from '@/types/history'
import HistoryDetailPanel from '@/features/history/components/HistoryDetailPanel'

vi.mock('recharts', async () => {
  const React = await import('react')
  const passThrough = ({ children }: { children?: React.ReactNode }) => React.createElement('div', null, children)
  const leaf = () => React.createElement('div')
  return {
    CartesianGrid: leaf,
    Line: leaf,
    LineChart: passThrough,
    ResponsiveContainer: passThrough,
    Tooltip: leaf,
    XAxis: leaf,
    YAxis: leaf,
  }
})

function makeDetail(): HistoryDetail {
  return {
    id: 901,
    created_at: '2026-04-25T09:30:00',
    risk_level: '中风险',
    risk_probability: 0.421,
    confidence_level: 'medium',
    data_days_used: 12,
    forecast_days: 7,
    input_data: {
      age: 56,
      bmi: 27.4,
      systolic_bp: 138,
      diastolic_bp: 86,
      bp_meds: 1,
    },
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
  }
}

describe('HistoryDetailPanel', () => {
  it('shows user prediction summary without professional detail sections', () => {
    render(<HistoryDetailPanel detail={makeDetail()} onClose={vi.fn()} />)

    expect(screen.getByText('用户端预测摘要')).toBeInTheDocument()
    expect(screen.getByText('7天风险预测')).toBeInTheDocument()
    expect(screen.getByText('未来7天血压趋势')).toBeInTheDocument()
    expect(screen.getByText('健康建议')).toBeInTheDocument()
    expect(screen.getByText(/仅作健康管理参考/)).toBeInTheDocument()

    expect(screen.queryByText(/输入数据快照|输入快照|置信度|参考记录天数|关键解读|详细解释|历史对比/)).not.toBeInTheDocument()
  })
})
