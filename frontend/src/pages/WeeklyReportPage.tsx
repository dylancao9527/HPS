import { Link } from 'react-router-dom'
import WeeklyBloodPressureChart from '@/features/weekly-report/components/WeeklyBloodPressureChart'
import WeeklyReportMetricGrid from '@/features/weekly-report/components/WeeklyReportMetricGrid'
import useWeeklyReport from '@/features/weekly-report/hooks/useWeeklyReport'
import {
  WEEKLY_REPORT_DATA_NOTE,
  WEEKLY_REPORT_SCOPE_TEXT,
  WEEKLY_REPORT_TITLE,
  buildWeeklyReportPeriodPresentation,
  hasInsufficientWeeklyReportData,
} from '@/features/weekly-report/presentation'

export default function WeeklyReportPage() {
  const { report, loading, error, reload } = useWeeklyReport()
  const hasInsufficientData = report ? hasInsufficientWeeklyReportData(report) : false
  const period = report ? buildWeeklyReportPeriodPresentation(report) : null

  return (
    <div className="page-shell">
      <header className="page-header">
        <div className="page-header-main">
          <span className="page-eyebrow">Weekly health report</span>
          <h1 className="page-title">{WEEKLY_REPORT_TITLE}</h1>
          <p className="page-desc">{WEEKLY_REPORT_SCOPE_TEXT}，回顾血压记录、偏高天数、记录持续性和风险概率变化。</p>
        </div>
        <div className="page-header-actions">
          <Link className="btn btn-ghost btn-sm" to="/bp-records">补充血压记录</Link>
        </div>
        {period && (
          <div className="page-meta-list" aria-label="报告周期">
            <span className="page-meta-chip">{period.currentLabel}</span>
            <span className="page-meta-chip">{period.previousLabel}</span>
          </div>
        )}
      </header>

      {loading && <section className="card weekly-report-state">正在加载周健康报告...</section>}

      {error && (
        <section className="card weekly-report-state weekly-report-state--error">
          <span>{error}</span>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => void reload()}>
            重试
          </button>
        </section>
      )}

      {report && !loading && !error && (
        <>
          <section className="card weekly-report-overview" aria-label="报告摘要">
            <div>
              <h2 className="card-title">报告概览</h2>
              <p>{report.overall_trend_text}</p>
            </div>
            {hasInsufficientData && (
              <p className="weekly-report-data-note">{WEEKLY_REPORT_DATA_NOTE}</p>
            )}
          </section>

          <section className="weekly-report-section" aria-labelledby="weekly-report-metrics-title">
            <div className="page-section-heading">
              <div>
                <h2 id="weekly-report-metrics-title" className="page-section-title">四项对比指标</h2>
                <p className="page-section-desc">所有指标只用于健康管理回顾，不作为临床诊断结论。</p>
              </div>
            </div>
            <WeeklyReportMetricGrid report={report} />
          </section>

          <section className="card weekly-report-chart-card" aria-labelledby="weekly-report-chart-title">
            <div>
              <h2 id="weekly-report-chart-title" className="card-title">平均血压对比</h2>
              <p className="weekly-report-chart-copy">按自然日聚合后的平均收缩压和舒张压。</p>
            </div>
            <WeeklyBloodPressureChart report={report} />
          </section>
        </>
      )}
    </div>
  )
}
