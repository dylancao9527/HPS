import Card from '@/components/Card'
import type { ProfileFeedbackField, ProfileFeedbackFormState } from '@/features/profile/profileFormState'

interface ProfileFeedbackSectionProps {
  feedbackForm: ProfileFeedbackFormState
  savingFeedback: boolean
  onUpdateField: (field: ProfileFeedbackField, value: string) => void
  onSaveFeedback: () => void
}

export default function ProfileFeedbackSection({
  feedbackForm,
  savingFeedback,
  onUpdateField,
  onSaveFeedback,
}: ProfileFeedbackSectionProps) {
  return (
    <Card title="其他健康信息">
      <div className="profile-section-intro">
        这类信息用于档案反馈和训练数据导出，与本次风险预测输入分开维护。
      </div>

      <div className="form-section-title">诊断反馈</div>
      <div className="diagnosis-group diagnosis-group--spaced">
        {[
          ['Yes', '已有高血压诊断反馈'],
          ['No', '暂无高血压诊断反馈'],
          ['', '不确定'],
        ].map(([value, label]) => (
          <label key={value} className="diagnosis-option">
            <input
              type="radio"
              name="profile-feedback-diagnosis"
              checked={feedbackForm.diagnosis === value}
              onChange={() => onUpdateField('diagnosis', value)}
            />
            {label}
          </label>
        ))}
      </div>
      <div className="profile-tip profile-tip--feedback">
        若您不确定，可先参考最近几次高血压风险预测结果；该项不作为本次 LightGBM 风险输入。
      </div>

      <button type="button" className="btn btn-primary" onClick={onSaveFeedback} disabled={savingFeedback}>
        {savingFeedback ? '保存中...' : '保存反馈信息'}
      </button>
    </Card>
  )
}
