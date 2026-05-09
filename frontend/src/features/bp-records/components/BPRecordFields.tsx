import type { BPRecordFormState } from '@/features/bp-records/types'

interface BPRecordFieldsProps {
  form: BPRecordFormState
  idPrefix: string
  recordedAtLabel: string
  onChange: (field: keyof BPRecordFormState, value: string) => void
  showPlaceholders?: boolean
}

export default function BPRecordFields({
  form,
  idPrefix,
  recordedAtLabel,
  onChange,
  showPlaceholders = false,
}: BPRecordFieldsProps) {
  return (
    <>
      <div className="form-group">
        <label htmlFor={`${idPrefix}-systolic`}>收缩压 (mmHg)</label>
        <input
          id={`${idPrefix}-systolic`}
          type="number"
          value={form.systolic_bp}
          required
          min={70}
          max={250}
          onChange={(event) => onChange('systolic_bp', event.target.value)}
          placeholder={showPlaceholders ? '如 120' : undefined}
        />
      </div>
      <div className="form-group">
        <label htmlFor={`${idPrefix}-diastolic`}>舒张压 (mmHg)</label>
        <input
          id={`${idPrefix}-diastolic`}
          type="number"
          value={form.diastolic_bp}
          required
          min={40}
          max={150}
          onChange={(event) => onChange('diastolic_bp', event.target.value)}
          placeholder={showPlaceholders ? '如 80' : undefined}
        />
      </div>
      <div className="form-group">
        <label htmlFor={`${idPrefix}-heart-rate`}>心率 (bpm，选填)</label>
        <input
          id={`${idPrefix}-heart-rate`}
          type="number"
          value={form.heart_rate}
          min={40}
          max={200}
          onChange={(event) => onChange('heart_rate', event.target.value)}
          placeholder={showPlaceholders ? '如 75' : undefined}
        />
      </div>
      <div className="form-group">
        <label htmlFor={`${idPrefix}-recorded-at`}>{recordedAtLabel}</label>
        <input
          id={`${idPrefix}-recorded-at`}
          type="datetime-local"
          value={form.recorded_at}
          onChange={(event) => onChange('recorded_at', event.target.value)}
        />
      </div>
    </>
  )
}
