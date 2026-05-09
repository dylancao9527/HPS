import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getTodayHealthTaskSummary } from '@/features/health-tasks/api/healthTaskApi'
import type { HealthTaskSummary } from '@/features/health-tasks/types'
import TodayHealthTasksPanel from '@/features/health-tasks/components/TodayHealthTasksPanel'

export default function TodayHealthTasksSection() {
  const navigate = useNavigate()
  const [taskSummary, setTaskSummary] = useState<HealthTaskSummary | null>(null)
  const [taskLoading, setTaskLoading] = useState(false)
  const [taskError, setTaskError] = useState('')

  const loadTaskSummary = async () => {
    setTaskLoading(true)
    try {
      const summary = await getTodayHealthTaskSummary()
      setTaskSummary(summary)
      setTaskError('')
    } catch {
      setTaskSummary(null)
      setTaskError('今日任务加载失败，请稍后重试。')
    } finally {
      setTaskLoading(false)
    }
  }

  useEffect(() => {
    let active = true

    ;(async () => {
      try {
        const summary = await getTodayHealthTaskSummary()
        if (!active) return
        setTaskSummary(summary)
        setTaskError('')
      } catch {
        if (!active) return
        setTaskSummary(null)
        setTaskError('今日任务加载失败，请稍后重试。')
      }
    })()

    return () => {
      active = false
    }
  }, [])

  return (
    <TodayHealthTasksPanel
      summary={taskSummary}
      loading={taskLoading}
      error={taskError}
      onRetry={() => {
        void loadTaskSummary()
      }}
      onQuickRecord={() => {
        navigate('/bp-records')
      }}
    />
  )
}
