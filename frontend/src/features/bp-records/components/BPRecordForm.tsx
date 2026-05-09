import { useState } from 'react'
import type { FormEvent } from 'react'
import Card from '@/components/Card'
import { createInitialBPRecordFormState } from '@/features/bp-records/formState'
import type { BPRecordFormState, CreateBPRecordInput } from '@/features/bp-records/types'
import BPRecordFields from '@/features/bp-records/components/BPRecordFields'

interface BPRecordFormProps {
  onSubmit: (data: CreateBPRecordInput) => void | Promise<void>
  loading: boolean
}

export default function BPRecordForm({ onSubmit, loading }: BPRecordFormProps) {
  const [form, setForm] = useState<BPRecordFormState>(createInitialBPRecordFormState)

  const handleFieldChange = (field: keyof BPRecordFormState, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!form.systolic_bp || !form.diastolic_bp) return

    const payload: CreateBPRecordInput = {
      ...form,
      systolic_bp: Number.parseFloat(form.systolic_bp),
      diastolic_bp: Number.parseFloat(form.diastolic_bp),
      heart_rate: form.heart_rate ? Number.parseFloat(form.heart_rate) : null,
    }

    try {
      await onSubmit(payload)
      setForm((prev) => ({ ...prev, systolic_bp: '', diastolic_bp: '', heart_rate: '' }))
    } catch {
      return
    }
  }

  return (
    <Card title="新增血压记录">
      <form onSubmit={handleSubmit} className="form-grid">
        <BPRecordFields
          form={form}
          idPrefix="bp"
          recordedAtLabel="测量时间"
          onChange={handleFieldChange}
          showPlaceholders
        />
        <button type="submit" className="btn btn-primary" disabled={loading} style={{ gridColumn: '1 / -1' }}>
          {loading ? '保存中...' : '保存记录'}
        </button>
      </form>
    </Card>
  )
}
