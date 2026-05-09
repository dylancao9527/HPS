import type { BPRecordFormState } from '@/features/bp-records/types'

export function formatDateTimeLocal(date: Date): string {
  const adjusted = new Date(date.getTime() - date.getTimezoneOffset() * 60_000)
  return adjusted.toISOString().slice(0, 16)
}

export function createInitialBPRecordFormState(): BPRecordFormState {
  return {
    systolic_bp: '',
    diastolic_bp: '',
    heart_rate: '',
    recorded_at: formatDateTimeLocal(new Date()),
  }
}
