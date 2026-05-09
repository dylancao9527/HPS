import type { InputHTMLAttributes } from 'react'

interface NumInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'value' | 'onChange'> {
  label: string
  value: number | string
  onChange: (value: number) => void
}

export default function NumInput({ label, value, onChange, ...props }: NumInputProps) {
  return (
    <div className="form-group">
      <label>{label}</label>
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        {...props}
      />
    </div>
  )
}
