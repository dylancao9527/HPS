import { useCallback, useEffect, useState } from 'react'
import { getWeeklyReport } from '@/features/weekly-report/api/weeklyReportApi'
import type { WeeklyReportSummary } from '@/features/weekly-report/types'

export default function useWeeklyReport() {
  const [report, setReport] = useState<WeeklyReportSummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const nextReport = await getWeeklyReport()
      setReport(nextReport)
    } catch (caughtError) {
      setReport(null)
      setError(caughtError instanceof Error ? caughtError.message : '周健康报告加载失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    let active = true

    ;(async () => {
      setLoading(true)
      setError('')

      try {
        const nextReport = await getWeeklyReport()
        if (!active) return
        setReport(nextReport)
      } catch (caughtError) {
        if (!active) return
        setReport(null)
        setError(caughtError instanceof Error ? caughtError.message : '周健康报告加载失败，请稍后重试')
      } finally {
        if (active) setLoading(false)
      }
    })()

    return () => {
      active = false
    }
  }, [])

  return { report, loading, error, reload: load }
}
