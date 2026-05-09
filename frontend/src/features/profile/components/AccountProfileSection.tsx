import Card from '@/components/Card'
import AvatarUpload from '@/components/AvatarUpload'

interface AccountProfileFormState {
  username: string
  email: string
  emailCode: string
  emailDebugCode: string
  nickname: string
  avatar: string
}

type AccountProfileField = keyof AccountProfileFormState

interface AccountProfileSectionProps {
  accountForm: AccountProfileFormState
  emailChanged: boolean
  savingAccount: boolean
  sendingEmailCode: boolean
  onUpdateField: (field: AccountProfileField, value: string) => void
  onSendChangeEmailCode: () => void
  onSaveAccount: () => void
}

export default function AccountProfileSection({
  accountForm,
  emailChanged,
  savingAccount,
  sendingEmailCode,
  onUpdateField,
  onSendChangeEmailCode,
  onSaveAccount,
}: AccountProfileSectionProps) {
  return (
    <Card title="账号与展示信息">
      <div className="profile-header">
        <AvatarUpload value={accountForm.avatar} onChange={(value: string) => onUpdateField('avatar', value)} />
        <div className="profile-header-info">
          <div className="form-grid profile-form-grid profile-form-grid--account-primary">
            <div className="form-group">
              <label>用户名</label>
              <input
                type="text"
                value={accountForm.username}
                onChange={(event) => onUpdateField('username', event.target.value)}
                placeholder="请输入用户名"
              />
            </div>
            <div className="form-group">
              <label>昵称</label>
              <input
                type="text"
                value={accountForm.nickname}
                onChange={(event) => onUpdateField('nickname', event.target.value)}
                placeholder="输入您的昵称或真实姓名"
              />
            </div>
          </div>

          <div className="form-grid profile-form-grid profile-form-grid--account-email">
            <div className="form-group">
              <label>邮箱</label>
              <input
                type="email"
                value={accountForm.email}
                onChange={(event) => onUpdateField('email', event.target.value)}
                placeholder="请输入邮箱"
              />
            </div>
            <div className="form-group">
              <label>新邮箱验证码</label>
              <div className="profile-inline-actions">
                <input
                  type="text"
                  value={accountForm.emailCode}
                  onChange={(event) => onUpdateField('emailCode', event.target.value)}
                  placeholder={emailChanged ? '修改邮箱时必填' : '邮箱未变更无需填写'}
                  maxLength={6}
                />
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={onSendChangeEmailCode}
                  disabled={sendingEmailCode || !emailChanged}
                >
                  {sendingEmailCode ? '发送中...' : '获取验证码'}
                </button>
              </div>
            </div>
          </div>

          <div className="profile-tip profile-tip--account-email">
            修改邮箱时，需要先获取新邮箱验证码并填写后再保存。
          </div>

          {accountForm.emailDebugCode && emailChanged && (
            <div className="success-msg profile-debug-code-block profile-debug-code-block--account">
              本地模拟邮箱验证码：<strong className="profile-debug-code">{accountForm.emailDebugCode}</strong>
              <br />
              <span className="profile-debug-code-hint">生产环境中该验证码应通过新邮箱发送。</span>
            </div>
          )}

          <button type="button" className="btn btn-primary btn-sm" onClick={onSaveAccount} disabled={savingAccount}>
            {savingAccount ? '保存中...' : '保存账号与展示信息'}
          </button>
        </div>
      </div>
    </Card>
  )
}