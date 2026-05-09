import { ArrowRight, CalendarDays } from 'lucide-react'
import { Link } from 'react-router-dom'
import WeeklyReportMetricGrid from '@/features/weekly-report/components/WeeklyReportMetricGrid'
import useWeeklyReport from '@/features/weekly-report/hooks/useWeeklyReport'
import {
  WEEKLY_REPORT_DATA_NOTE,
  WEEKLY_REPORT_TITLE,
  buildWeeklyReportPeriodPresentation,
  hasInsufficientWeeklyReportData,
} from '@/features/weekly-report/presentation'

export default function WeeklyReportSummarySection() {
  const { report, loading, error, reload } = useWeeklyReport()

  if (loading) {
    return (
      <section className="weekly-report-summary card" aria-label="周健康报告">
        <div className="weekly-report-state">正在加载周健康报告...</div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="weekly-report-summary card" aria-label="周健康报告">
        <div className="weekly-report-state weekly-report-state--error">
          <span>{error}</span>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => void reload()}>
            重试
          </button>
        </div>
      </section>
    )
  }

  if (!report) {
    return (
      <section className="weekly-report-summary card" aria-label="周健康报告">
        <div className="weekly-report-state">暂无周健康报告</div>
      </section>
    )
  }

  const hasInsufficientData = hasInsufficientWeeklyReportData(report)
  const period = buildWeeklyReportPeriodPresentation(report)

  return (
    <section className="weekly-report-summary card" aria-label="周健康报告">
      <div className="weekly-report-summary-header">
        <div>
          <span className="page-eyebrow">Weekly report</span>
          <h2 className="card-title">{WEEKLY_REPORT_TITLE}</h2>
          <p className="weekly-report-summary-copy">{report.overall_trend_text}</p>
        </div>
        <Link className="btn btn-ghost" to="/weekly-report">
          查看详情
          <ArrowRight size={16} aria-hidden="true" />
        </Link>
      </div>

      <div className="weekly-report-period-row" aria-label="报告周期">
        <span>
          <CalendarDays size={16} aria-hidden="true" />
          {period.currentLabel}
        </span>
        <span>{period.previousLabel}</span>
      </div>

      <WeeklyReportMetricGrid report={report} compact />

      {hasInsufficientData && (
        <p className="weekly-report-data-note">{WEEKLY_REPORT_DATA_NOTE}</p>
      )}
    </section>
  )
}
