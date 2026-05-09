import type { ReactNode } from 'react'
import type { HealthTaskSummary } from '@/features/health-tasks/types'

interface HealthTaskMetricGridProps {
  summary: HealthTaskSummary
}

interface HealthTaskMetric {
  label: string
  value?: ReactNode
  copy?: string
  tone?: HealthTaskSummary['alert_level']
}

function formatRecordTime(value: string): string {
  return new Date(value).toLocaleString('zh-CN')
}

function getAlertLabel(alertLevel: HealthTaskSummary['alert_level']): string {
  if (alertLevel === 'danger') return '连续偏高'
  if (alertLevel === 'warning') return '需继续监测'
  return '暂无预警'
}

function HealthTaskMetricCard({ label, value, copy, tone }: HealthTaskMetric) {
  return (
    <article className={`health-task-card${tone ? ` health-task-card--${tone}` : ''}`}>
      <span className="health-task-label">{label}</span>
      {value && <strong className="health-task-value">{value}</strong>}
      {copy && <p className="health-task-copy">{copy}</p>}
    </article>
  )
}

export default function HealthTaskMetricGrid({ summary }: HealthTaskMetricGridProps) {
  const metrics: HealthTaskMetric[] = [
    {
      label: '今日状态',
      value: summary.today_status_text,
    },
    {
      label: '连续打卡',
      value: `连续 ${summary.current_streak_days} 天`,
    },
    {
      label: '连续偏高预警',
      value: getAlertLabel(summary.alert_level),
      copy: summary.alert_message,
      tone: summary.alert_level,
    },
    {
      label: '最近一次血压',
      value: summary.latest_record
        ? `${summary.latest_record.systolic_bp} / ${summary.latest_record.diastolic_bp} mmHg`
        : undefined,
      copy: summary.latest_record
        ? `心率 ${summary.latest_record.heart_rate ?? '-'} bpm · ${formatRecordTime(summary.latest_record.recorded_at)}`
        : '暂无血压记录，先完成今天的第一条记录。',
    },
  ]

  return (
    <div className="health-task-grid">
      {metrics.map((metric) => (
        <HealthTaskMetricCard key={metric.label} {...metric} />
      ))}
    </div>
  )
}
