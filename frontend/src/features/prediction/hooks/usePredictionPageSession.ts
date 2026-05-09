import { useCallback, useEffect, useState } from 'react'
import {
  getTodayHealthTaskSummary,
  type HealthTaskSummary,
} from '@/features/health-tasks'
import useBPRecordWriter from '@/features/bp-records/hooks/useBPRecordWriter'
import { getPredictionTrendText } from '@/features/prediction/utils'
import { useFeedback } from '@/hooks/useFeedback'
import type { CreateBPRecordInput } from '@/features/bp-records/types'
import type { PredictionResult } from '@/types/prediction'

type IsActive = () => boolean

export function usePredictionPageSession() {
  const { showToast } = useFeedback()
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [healthTaskSummary, setHealthTaskSummary] = useState<HealthTaskSummary | null>(null)
  const [healthTaskLoading, setHealthTaskLoading] = useState(false)
  const [healthTaskError, setHealthTaskError] = useState('')
  const [quickRecordOpen, setQuickRecordOpen] = useState(false)
  const [statusRefreshKey, setStatusRefreshKey] = useState(0)

  const loadHealthTasks = useCallback(async (isActive: IsActive = () => true): Promise<string> => {
    setHealthTaskLoading(true)
    setHealthTaskError('')

    try {
      const summary = await getTodayHealthTaskSummary()
      if (!isActive()) return ''
      setHealthTaskSummary(summary)
      return ''
    } catch (error) {
      const message = error instanceof Error ? error.message : '任务信息加载失败，请稍后重试'
      if (!isActive()) return message
      setHealthTaskError(message)
      return message
    } finally {
      if (isActive()) setHealthTaskLoading(false)
    }
  }, [])

  const handleQuickRecordSuccess = useCallback(async () => {
    setQuickRecordOpen(false)
    setStatusRefreshKey((prev) => prev + 1)

    const refreshError = await loadHealthTasks()
    if (refreshError) {
      showToast(refreshError, 'error')
    }
  }, [loadHealthTasks, showToast])

  const quickRecordWriter = useBPRecordWriter({
    fallbackError: '保存失败，请检查输入后重试',
    successMessage: '今日血压记录已保存',
    showToast,
    onSuccess: handleQuickRecordSuccess,
  })

  useEffect(() => {
    let active = true
    void loadHealthTasks(() => active)

    return () => {
      active = false
    }
  }, [loadHealthTasks])

  const handleResult = useCallback((nextResult: PredictionResult) => {
    setResult(nextResult)
  }, [])

  const handleReset = useCallback(() => {
    setResult(null)
  }, [])

  const openQuickRecord = useCallback(() => {
    quickRecordWriter.clearError()
    setQuickRecordOpen(true)
  }, [quickRecordWriter])

  const closeQuickRecord = useCallback(() => {
    setQuickRecordOpen(false)
  }, [])

  const isUsingMedication = result?.input_data?.bp_meds === 1
  const trendText = getPredictionTrendText(result?.bp_forecast)

  return {
    handleReset,
    handleResult,
    healthTasks: {
      error: healthTaskError,
      loading: healthTaskLoading,
      onQuickRecord: openQuickRecord,
      onRetry: () => void loadHealthTasks(),
      summary: healthTaskSummary,
    },
    isUsingMedication,
    quickRecord: {
      error: quickRecordWriter.error,
      loading: quickRecordWriter.loading,
      onClose: closeQuickRecord,
      onSubmit: (payload: CreateBPRecordInput) => quickRecordWriter.submit(payload),
      open: quickRecordOpen,
    },
    result,
    statusRefreshKey,
    trendText,
  }
}
