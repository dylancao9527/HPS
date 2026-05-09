import Card from '@/components/Card'
import SelInput from '@/components/SelInput'

interface HealthProfileFormState {
  age: string
  male: string
  height: string
  weight: string
  current_smoker: string
  cigs_per_day: string
  bp_meds: string
  diabetes: string
  tot_chol: string
  glucose: string
}

interface BmiStatusView {
  label: string
  color: string
}

type HealthProfileField = keyof HealthProfileFormState

function FieldLabel({
  badge,
  children,
  htmlFor,
}: {
  badge?: '必填' | '选填'
  children: string
  htmlFor: string
}) {
  return (
    <label htmlFor={htmlFor}>
      {children}
      {badge && (
        <span className={`profile-field-badge profile-field-badge--${badge === '必填' ? 'required' : 'optional'}`}>
          {badge}
        </span>
      )}
    </label>
  )
}

interface HealthProfileSectionProps {
  healthForm: HealthProfileFormState
  bmi: string | null
  bmiStatus: BmiStatusView
  bmiToneClass: string
  smokerEnabled: boolean
  savingHealth: boolean
  onUpdateField: (field: HealthProfileField, value: string) => void
  onSaveHealth: () => void
}

export default function HealthProfileSection({
  healthForm,
  bmi,
  bmiStatus,
  bmiToneClass,
  smokerEnabled,
  savingHealth,
  onUpdateField,
  onSaveHealth,
}: HealthProfileSectionProps) {
  return (
    <Card title="风险因素档案">
      <div className="profile-section-intro">
        年龄、性别、身高和体重是生成 7 天风险预测前的最低必填项，其余风险因素可先留空后续补充。
      </div>

      <div className="form-section-title">基本信息</div>
      <div className="form-grid profile-form-grid profile-form-grid--basic">
        <div className="form-group">
          <FieldLabel htmlFor="risk-profile-age" badge="必填">年龄</FieldLabel>
          <input
            id="risk-profile-age"
            type="number"
            min="1"
            max="120"
            required
            value={healthForm.age}
            onChange={(event) => onUpdateField('age', event.target.value)}
            placeholder="请输入年龄"
          />
        </div>
        <SelInput
          id="risk-profile-sex"
          label="性别"
          labelBadge="必填"
          required
          value={healthForm.male}
          onChange={(value: string) => onUpdateField('male', value)}
          options={[
            ['1', '男'],
            ['0', '女'],
          ]}
        />
      </div>

      <div className="form-section-title">身体指标</div>
      <div className={`form-grid profile-form-grid ${bmi ? 'profile-form-grid--body-has-bmi' : 'profile-form-grid--body'}`}>
        <div className="form-group">
          <FieldLabel htmlFor="risk-profile-height" badge="必填">身高 (cm)</FieldLabel>
          <input
            id="risk-profile-height"
            type="number"
            min="80"
            max="250"
            step="0.1"
            required
            value={healthForm.height}
            onChange={(event) => onUpdateField('height', event.target.value)}
            placeholder="请输入身高"
          />
        </div>
        <div className="form-group">
          <FieldLabel htmlFor="risk-profile-weight" badge="必填">体重 (kg)</FieldLabel>
          <input
            id="risk-profile-weight"
            type="number"
            min="20"
            max="300"
            step="0.1"
            required
            value={healthForm.weight}
            onChange={(event) => onUpdateField('weight', event.target.value)}
            placeholder="请输入体重"
          />
        </div>
      </div>
      {bmi && (
        <div className="bmi-display bmi-display--spaced">
          <span>
            BMI：<strong>{bmi}</strong>
          </span>
          <span className={bmiToneClass}>{bmiStatus.label}</span>
        </div>
      )}

      <div className="form-section-title">风险相关特征</div>
      <div className="form-grid profile-form-grid profile-form-grid--risk">
        <SelInput
          id="risk-profile-current-smoker"
          label="当前是否吸烟"
          value={healthForm.current_smoker}
          onChange={(value: string) => onUpdateField('current_smoker', value)}
          options={[
            ['0', '否'],
            ['1', '是'],
          ]}
        />
        <div className="form-group">
          <FieldLabel htmlFor="risk-profile-cigs-per-day">日吸烟支数</FieldLabel>
          <input
            id="risk-profile-cigs-per-day"
            type="number"
            min="0"
            max="80"
            value={healthForm.cigs_per_day}
            onChange={(event) => onUpdateField('cigs_per_day', event.target.value)}
            placeholder={smokerEnabled ? '请输入每日支数' : '未吸烟时固定为 0'}
            disabled={!smokerEnabled}
          />
        </div>
        <SelInput
          id="risk-profile-bp-meds"
          label="是否长期按医嘱服用降压药"
          labelBadge="选填"
          value={healthForm.bp_meds}
          onChange={(value: string) => onUpdateField('bp_meds', value)}
          options={[
            ['', '未填写'],
            ['0', '否'],
            ['1', '是'],
          ]}
        />
        <SelInput
          id="risk-profile-diabetes"
          label="是否患糖尿病"
          labelBadge="选填"
          value={healthForm.diabetes}
          onChange={(value: string) => onUpdateField('diabetes', value)}
          options={[
            ['', '未填写'],
            ['0', '否'],
            ['1', '是'],
          ]}
        />
      </div>

      <div className="profile-tip profile-tip--smoking">
        当前不吸烟时，系统会自动将“日吸烟支数”按 0 处理。
      </div>
      <div className="profile-tip profile-tip--medication">
        “降压药”仅指医生已处方并持续使用的降压药；偶尔服药或短期自行用药不建议勾选“是”。
      </div>

      <div className="form-section-title">化验指标（选填）</div>
      <div className="form-grid profile-form-grid profile-form-grid--lab">
        <div className="form-group">
          <FieldLabel htmlFor="risk-profile-tot-chol" badge="选填">总胆固醇 (mg/dL)</FieldLabel>
          <input
            id="risk-profile-tot-chol"
            type="number"
            min="50"
            max="500"
            value={healthForm.tot_chol}
            onChange={(event) => onUpdateField('tot_chol', event.target.value)}
            placeholder="选填"
          />
        </div>
        <div className="form-group">
          <FieldLabel htmlFor="risk-profile-glucose" badge="选填">血糖 (mg/dL)</FieldLabel>
          <input
            id="risk-profile-glucose"
            type="number"
            min="40"
            max="500"
            value={healthForm.glucose}
            onChange={(event) => onUpdateField('glucose', event.target.value)}
            placeholder="选填"
          />
        </div>
      </div>

      <button type="button" className="btn btn-primary" onClick={onSaveHealth} disabled={savingHealth}>
        {savingHealth ? '保存中...' : '保存风险因素档案'}
      </button>
    </Card>
  )
}
