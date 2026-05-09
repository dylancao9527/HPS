/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react'
import type { MouseEvent, ReactNode } from 'react'

export type ToastType = 'info' | 'success' | 'error'

export interface ToastPayload {
  message: string
  type: ToastType
}

export interface ConfirmOptions {
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  danger?: boolean
}

export type ConfirmResult = boolean

interface ConfirmState {
  title: string
  message: string
  confirmText: string
  cancelText: string
  danger: boolean
  resolve: (result: ConfirmResult) => void
}

interface FeedbackContextValue {
  showToast: (message: string, type?: ToastType, duration?: number) => void
  confirm: (options?: ConfirmOptions) => Promise<ConfirmResult>
}

interface FeedbackProviderProps {
  children: ReactNode
}

const FeedbackContext = createContext<FeedbackContextValue | null>(null)

export function FeedbackProvider({ children }: FeedbackProviderProps) {
  const [toast, setToast] = useState<ToastPayload | null>(null)
  const [confirmState, setConfirmState] = useState<ConfirmState | null>(null)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const showToast = useCallback((message: string, type: ToastType = 'info', duration: number = 2600) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }

    setToast({ message, type })

    timerRef.current = setTimeout(() => {
      setToast(null)
      timerRef.current = null
    }, duration)
  }, [])

  const closeToast = useCallback((): void => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
    setToast(null)
  }, [])

  const confirm = useCallback((options: ConfirmOptions = {}): Promise<ConfirmResult> => {
    return new Promise((resolve) => {
      setConfirmState({
        title: options.title || '请确认操作',
        message: options.message || '确定继续吗？',
        confirmText: options.confirmText || '确定',
        cancelText: options.cancelText || '取消',
        danger: Boolean(options.danger),
        resolve,
      })
    })
  }, [])

  const resolveConfirm = useCallback((result: ConfirmResult): void => {
    setConfirmState((prev) => {
      if (prev?.resolve) prev.resolve(result)
      return null
    })
  }, [])

  const value = useMemo<FeedbackContextValue>(
    () => ({ showToast, confirm }),
    [showToast, confirm],
  )

  return (
    <FeedbackContext.Provider value={value}>
      {children}

      {toast && (
        <div className={`toast toast-${toast.type}`} role="status" aria-live="polite">
          <span>{toast.message}</span>
          <button className="toast-close" onClick={closeToast} aria-label="关闭提示">×</button>
        </div>
      )}

      {confirmState && (
        <div className="modal-overlay" onClick={() => resolveConfirm(false)}>
          <div className="modal-content confirm-modal" onClick={(e: MouseEvent<HTMLDivElement>) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{confirmState.title}</h3>
            </div>
            <p className="confirm-text">{confirmState.message}</p>
            <div className="confirm-actions">
              <button className="btn btn-ghost" onClick={() => resolveConfirm(false)}>
                {confirmState.cancelText}
              </button>
              <button
                className={`btn ${confirmState.danger ? 'btn-danger' : 'btn-primary'}`}
                onClick={() => resolveConfirm(true)}
              >
                {confirmState.confirmText}
              </button>
            </div>
          </div>
        </div>
      )}
    </FeedbackContext.Provider>
  )
}

export function useFeedback(): FeedbackContextValue {
  const ctx = useContext(FeedbackContext)
  if (!ctx) throw new Error('useFeedback must be used within FeedbackProvider')
  return ctx
}
