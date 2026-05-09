import { useCallback, useState } from 'react'
import { addBPRecord } from '@/features/bp-records/api/bpApi'
import type { CreateBPRecordInput } from '@/features/bp-records/types'
import type { ToastType } from '@/hooks/useFeedback'

type ShowToast = (message: string, type?: ToastType, duration?: number) => void

interface UseBPRecordWriterOptions {
  fallbackError: string
  successMessage?: string
  showToast?: ShowToast
  showErrorToast?: boolean
  throwOnError?: boolean
  onSuccess?: () => Promise<void> | void
}

function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error && error.message ? error.message : fallback
}

export default function useBPRecordWriter({
  fallbackError,
  successMessage,
  showToast,
  showErrorToast = false,
  throwOnError = false,
  onSuccess,
}: UseBPRecordWriterOptions) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const clearError = useCallback(() => {
    setError('')
  }, [])

  const submit = useCallback(
    async (payload: CreateBPRecordInput): Promise<void> => {
      setLoading(true)
      setError('')

      try {
        await addBPRecord(payload)
        await onSuccess?.()
        if (successMessage) showToast?.(successMessage, 'success')
      } catch (caughtError) {
        const message = getErrorMessage(caughtError, fallbackError)
        setError(message)
        if (showErrorToast) showToast?.(message, 'error')
        if (throwOnError) throw new Error(message)
      } finally {
        setLoading(false)
      }
    },
    [fallbackError, onSuccess, showErrorToast, showToast, successMessage, throwOnError],
  )

  return {
    clearError,
    error,
    loading,
    submit,
  }
}
