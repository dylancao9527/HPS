import {
  WEEKLY_REPORT_CURRENT_PERIOD_LABEL,
  WEEKLY_REPORT_PREVIOUS_PERIOD_LABEL,
  buildWeeklyReportMetrics,
  type WeeklyReportMetricTone,
} from '@/features/weekly-report/presentation'
import type { WeeklyReportSummary } from '@/features/weekly-report/types'

interface WeeklyReportMetricGridProps {
  report: WeeklyReportSummary
  compact?: boolean
}

function getToneLabel(tone: WeeklyReportMetricTone): string {
  if (tone === 'good') return '下降或改善'
  if (tone === 'warning') return '上升或减少'
  if (tone === 'insufficient') return '数据不足'
  return '基本持平'
}

export default function WeeklyReportMetricGrid({ report, compact = false }: WeeklyReportMetricGridProps) {
  const metrics = buildWeeklyReportMetrics(report)

  return (
    <div className={`weekly-report-metric-grid${compact ? ' weekly-report-metric-grid--compact' : ''}`}>
      {metrics.map((metric) => (
        <article
          key={metric.key}
          className={`weekly-report-metric weekly-report-metric--${metric.tone}`}
          aria-label={`${metric.label}：${metric.changeLabel}`}
        >
          <div className="weekly-report-metric-heading">
            <span className="weekly-report-metric-label">{metric.label}</span>
            <span className="weekly-report-metric-tone">{getToneLabel(metric.tone)}</span>
          </div>
          <strong className="weekly-report-metric-change">{metric.changeLabel}</strong>
          {!compact && (
            <>
              <dl className="weekly-report-metric-values">
                <div>
                  <dt>{WEEKLY_REPORT_CURRENT_PERIOD_LABEL}</dt>
                  <dd>{metric.currentLabel}</dd>
                </div>
                <div>
                  <dt>{WEEKLY_REPORT_PREVIOUS_PERIOD_LABEL}</dt>
                  <dd>{metric.previousLabel}</dd>
                </div>
              </dl>
              <p className="weekly-report-metric-helper">{metric.helperText}</p>
            </>
          )}
        </article>
      ))}
    </div>
  )
}
