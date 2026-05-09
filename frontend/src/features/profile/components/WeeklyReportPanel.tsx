import Card from '@/components/Card'
import WeeklyReportMetricGrid from '@/features/weekly-report/components/WeeklyReportMetricGrid'
import {
  WEEKLY_REPORT_TITLE,
  buildWeeklyReportPeriodPresentation,
} from '@/features/weekly-report/presentation'
import type { WeeklyReportSummary } from '@/features/weekly-report/types'

interface WeeklyReportPanelProps {
  loading: boolean
  error: string
  data: WeeklyReportSummary | null
  onRetry?: () => void
}

export default function WeeklyReportPanel({ loading, error, data, onRetry }: WeeklyReportPanelProps) {
  if (loading) {
    return <div className="card comparison-panel">正在加载周健康报告...</div>
  }

  if (error) {
    return (
      <div className="card comparison-panel comparison-panel--state">
        <p>{error}</p>
        {onRetry && (
          <button type="button" className="btn btn-ghost btn-sm" onClick={onRetry}>
            重新加载
          </button>
        )}
      </div>
    )
  }

  if (!data) {
    return <div className="card comparison-panel">暂无周健康报告</div>
  }

  const period = buildWeeklyReportPeriodPresentation(data)

  return (
    <Card title={WEEKLY_REPORT_TITLE} className="comparison-panel">
      <div className="comparison-hero">
        <div className="comparison-periods">
          <span>{period.currentLabel}</span>
          <span>{period.previousLabel}</span>
        </div>
        <p className="comparison-summary">{data.overall_trend_text}</p>
      </div>

      <WeeklyReportMetricGrid report={data} />
    </Card>
  )
}
