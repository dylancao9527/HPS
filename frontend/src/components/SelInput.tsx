type SelectOption = string | [string, string]

interface SelInputProps {
  id?: string
  label: string
  labelBadge?: '必填' | '选填'
  required?: boolean
  value: string
  onChange: (value: string) => void
  options: SelectOption[]
}

export default function SelInput({
  id,
  label,
  labelBadge,
  required = false,
  value,
  onChange,
  options,
}: SelInputProps) {
  return (
    <div className="form-group">
      <label htmlFor={id}>
        {label}
        {labelBadge && (
          <span className={`profile-field-badge profile-field-badge--${labelBadge === '必填' ? 'required' : 'optional'}`}>
            {labelBadge}
          </span>
        )}
      </label>
      <select id={id} required={required} value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((option) => {
          const [optionValue, text] = Array.isArray(option) ? option : [option, option]
          return <option key={optionValue} value={optionValue}>{text}</option>
        })}
      </select>
    </div>
  )
}
