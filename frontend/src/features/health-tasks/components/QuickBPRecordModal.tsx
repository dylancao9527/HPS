import { useState } from 'react'
import type { FormEvent } from 'react'
import BPRecordFields from '@/features/bp-records/components/BPRecordFields'
import { createInitialBPRecordFormState } from '@/features/bp-records/formState'
import type { BPRecordFormState } from '@/features/bp-records/types'
import type { CreateBPRecordInput } from '@/features/bp-records/types'

interface QuickBPRecordModalProps {
  open: boolean
  loading: boolean
  error: string
  onClose: () => void
  onSubmit: (payload: CreateBPRecordInput) => Promise<void> | void
}

function toUtcIsoString(value: string): string {
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? value : parsed.toISOString()
}

export default function QuickBPRecordModal({
  open,
  loading,
  error,
  onClose,
  onSubmit,
}: QuickBPRecordModalProps) {
  if (!open) return null

  return <QuickBPRecordModalContent loading={loading} error={error} onClose={onClose} onSubmit={onSubmit} />
}

function QuickBPRecordModalContent({
  loading,
  error,
  onClose,
  onSubmit,
}: Omit<QuickBPRecordModalProps, 'open'>) {
  const [form, setForm] = useState<BPRecordFormState>(createInitialBPRecordFormState)

  const handleFieldChange = (field: keyof BPRecordFormState, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!form.systolic_bp || !form.diastolic_bp) return

    await onSubmit({
      systolic_bp: Number.parseFloat(form.systolic_bp),
      diastolic_bp: Number.parseFloat(form.diastolic_bp),
      heart_rate: form.heart_rate ? Number.parseFloat(form.heart_rate) : null,
      recorded_at: toUtcIsoString(form.recorded_at),
    })
  }

  return (
    <div className="modal-overlay" data-testid="quick-bp-overlay" onClick={onClose}>
      <div
        className="modal-content quick-bp-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="quick-bp-modal-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <h3 id="quick-bp-modal-title">快捷录入</h3>
            <p className="page-section-desc">直接补录今天的血压数据，保存后首页任务状态会立即刷新。</p>
          </div>
          <button type="button" className="modal-close" onClick={onClose} aria-label="关闭快捷录入">
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="quick-bp-form">
          <div className="form-grid">
            <BPRecordFields
              form={form}
              idPrefix="quick-bp"
              recordedAtLabel="记录时间"
              onChange={handleFieldChange}
            />
          </div>

          {error && (
            <div className="error-msg" role="alert">
              {error}
            </div>
          )}

          <div className="quick-bp-actions">
            <button type="button" className="btn btn-ghost" onClick={onClose}>
              取消
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? '保存中...' : '保存今日记录'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
