interface HealthTaskStateViewProps {
  message: string
  tone?: 'default' | 'error'
  onRetry?: () => void
}

export default function HealthTaskStateView({
  message,
  tone = 'default',
  onRetry,
}: HealthTaskStateViewProps) {
  return (
    <section className="health-task-panel card" aria-label="今日健康任务">
      <div className={`health-task-state${tone === 'error' ? ' health-task-state--error' : ''}`}>
        {tone === 'error' ? <p>{message}</p> : message}
        {onRetry && (
          <button type="button" className="btn btn-ghost btn-sm" onClick={onRetry}>
            重新加载
          </button>
        )}
      </div>
    </section>
  )
}
