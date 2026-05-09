import type { HealthTaskSummary } from '@/features/health-tasks/types'
import HealthTaskActionHeader from '@/features/health-tasks/components/HealthTaskActionHeader'
import type { HealthTaskActionPresentation } from '@/features/health-tasks/components/HealthTaskActionHeader'
import HealthTaskMetricGrid from '@/features/health-tasks/components/HealthTaskMetricGrid'
import HealthTaskStateView from '@/features/health-tasks/components/HealthTaskStateView'

interface TodayHealthTasksPanelProps {
  summary: HealthTaskSummary | null
  loading: boolean
  error: string
  onRetry: () => void
  onQuickRecord: () => void
}

function getQuickActionPresentation(
  suggestedAction: HealthTaskSummary['suggested_action'],
): HealthTaskActionPresentation {
  if (suggestedAction === 'monitor_alert') {
    return {
      buttonLabel: '继续监测',
      buttonClassName: 'btn btn-ghost',
      helperCopy: '当前建议先继续观察今天的变化，再按需补充一条记录。',
    }
  }

  if (suggestedAction === 'keep_tracking') {
    return {
      buttonLabel: '保持跟踪',
      buttonClassName: 'btn btn-ghost',
      helperCopy: '当前状态较平稳，继续按计划记录即可。',
    }
  }

  return {
    buttonLabel: '快捷录入',
    buttonClassName: 'btn btn-primary',
    helperCopy: '建议尽快完成今天的记录，便于后续持续监测。',
  }
}

export default function TodayHealthTasksPanel({
  summary,
  loading,
  error,
  onRetry,
  onQuickRecord,
}: TodayHealthTasksPanelProps) {
  if (loading) {
    return <HealthTaskStateView message="正在加载今日健康任务..." />
  }

  if (error) {
    return <HealthTaskStateView message={error} tone="error" onRetry={onRetry} />
  }

  if (!summary) {
    return <HealthTaskStateView message="暂无任务信息" />
  }

  const quickAction = getQuickActionPresentation(summary.suggested_action)

  return (
    <section className="health-task-panel card" aria-label="今日健康任务">
      <HealthTaskActionHeader quickAction={quickAction} onQuickRecord={onQuickRecord} />
      <HealthTaskMetricGrid summary={summary} />
    </section>
  )
}
