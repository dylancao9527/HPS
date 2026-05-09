import Card from '@/components/Card'

interface PasswordSettingsFormState {
  oldPassword: string
  newPassword: string
  confirmPassword: string
}

interface ResetPasswordSettingsFormState {
  email: string
  code: string
  newPassword: string
  confirmPassword: string
  debugCode: string
}

type PasswordField = keyof PasswordSettingsFormState
type ResetPasswordField = keyof ResetPasswordSettingsFormState

interface PasswordSettingsSectionProps {
  passwordMode: 'old_password' | 'email_code'
  passwordForm: PasswordSettingsFormState
  resetPasswordForm: ResetPasswordSettingsFormState
  savingPassword: boolean
  sendingResetCode: boolean
  onChangeMode: (mode: 'old_password' | 'email_code') => void
  onUpdatePasswordField: (field: PasswordField, value: string) => void
  onUpdateResetPasswordField: (field: ResetPasswordField, value: string) => void
  onChangePassword: () => void
  onSendResetCode: () => void
  onResetPasswordByEmail: () => void
}

export default function PasswordSettingsSection({
  passwordMode,
  passwordForm,
  resetPasswordForm,
  savingPassword,
  sendingResetCode,
  onChangeMode,
  onUpdatePasswordField,
  onUpdateResetPasswordField,
  onChangePassword,
  onSendResetCode,
  onResetPasswordByEmail,
}: PasswordSettingsSectionProps) {
  return (
    <Card title="密码设置">
      <div className="profile-password-mode-switch">
        <button
          type="button"
          className={`btn btn-sm ${passwordMode === 'old_password' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => onChangeMode('old_password')}
        >
          旧密码修改
        </button>
        <button
          type="button"
          className={`btn btn-sm ${passwordMode === 'email_code' ? 'btn-primary' : 'btn-ghost'}`}
          onClick={() => onChangeMode('email_code')}
        >
          忘记密码，邮箱验证码修改
        </button>
      </div>

      {passwordMode === 'old_password' ? (
        <>
          <div className="form-grid">
            <div className="form-group">
              <label>旧密码</label>
              <input
                type="password"
                value={passwordForm.oldPassword}
                onChange={(event) => onUpdatePasswordField('oldPassword', event.target.value)}
                placeholder="请输入当前密码"
              />
            </div>
            <div className="form-group">
              <label>新密码</label>
              <input
                type="password"
                value={passwordForm.newPassword}
                onChange={(event) => onUpdatePasswordField('newPassword', event.target.value)}
                placeholder="8~32 位，至少两类字符"
              />
            </div>
            <div className="form-group">
              <label>确认新密码</label>
              <input
                type="password"
                value={passwordForm.confirmPassword}
                onChange={(event) => onUpdatePasswordField('confirmPassword', event.target.value)}
                placeholder="请再次输入新密码"
              />
            </div>
          </div>
          <div className="profile-tip profile-tip--password-rules">
            密码规则：8~32 位，且至少包含字母、数字、符号中的两种。
          </div>
          <button type="button" className="btn btn-primary" onClick={onChangePassword} disabled={savingPassword}>
            {savingPassword ? '修改中...' : '确认修改密码'}
          </button>
        </>
      ) : (
        <>
          <div className="form-grid">
            <div className="form-group">
              <label>邮箱</label>
              <input
                type="email"
                value={resetPasswordForm.email}
                onChange={(event) => onUpdateResetPasswordField('email', event.target.value)}
                placeholder="请输入注册邮箱"
              />
            </div>
            <div className="form-group">
              <label>验证码</label>
              <div className="profile-inline-actions">
                <input
                  type="text"
                  value={resetPasswordForm.code}
                  onChange={(event) => onUpdateResetPasswordField('code', event.target.value)}
                  placeholder="输入 6 位验证码"
                  maxLength={6}
                />
                <button type="button" className="btn btn-ghost btn-sm" onClick={onSendResetCode} disabled={sendingResetCode}>
                  {sendingResetCode ? '发送中...' : '获取验证码'}
                </button>
              </div>
            </div>
            <div className="form-group">
              <label>新密码</label>
              <input
                type="password"
                value={resetPasswordForm.newPassword}
                onChange={(event) => onUpdateResetPasswordField('newPassword', event.target.value)}
                placeholder="8~32 位，至少两类字符"
              />
            </div>
            <div className="form-group">
              <label>确认新密码</label>
              <input
                type="password"
                value={resetPasswordForm.confirmPassword}
                onChange={(event) => onUpdateResetPasswordField('confirmPassword', event.target.value)}
                placeholder="请再次输入新密码"
              />
            </div>
          </div>

          {resetPasswordForm.debugCode && (
            <div className="success-msg profile-debug-code-block profile-debug-code-block--reset">
              本地模拟邮箱验证码：<strong className="profile-debug-code">{resetPasswordForm.debugCode}</strong>
            </div>
          )}

          <div className="profile-tip profile-tip--password-reset">
            该流程与登录页“忘记密码”一致，通过邮箱验证码完成密码重置。
          </div>

          <button type="button" className="btn btn-primary" onClick={onResetPasswordByEmail} disabled={savingPassword}>
            {savingPassword ? '重置中...' : '通过邮箱验证码重置密码'}
          </button>
        </>
      )}
    </Card>
  )
}