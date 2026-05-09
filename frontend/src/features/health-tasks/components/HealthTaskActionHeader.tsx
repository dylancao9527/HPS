export interface HealthTaskActionPresentation {
  buttonLabel: string
  buttonClassName: string
  helperCopy: string
}

interface HealthTaskActionHeaderProps {
  quickAction: HealthTaskActionPresentation
  onQuickRecord: () => void
}

export default function HealthTaskActionHeader({
  quickAction,
  onQuickRecord,
}: HealthTaskActionHeaderProps) {
  return (
    <div className="health-task-header">
      <div>
        <span className="page-eyebrow">Today task</span>
        <h2 className="page-section-title">今日健康任务</h2>
        <p className="page-section-desc">先确认今天是否已记录，再决定是否需要继续监测。</p>
      </div>
      <div className="health-task-cta">
        <button type="button" className={quickAction.buttonClassName} onClick={onQuickRecord}>
          {quickAction.buttonLabel}
        </button>
        <p className="health-task-cta-copy">{quickAction.helperCopy}</p>
      </div>
    </div>
  )
}
