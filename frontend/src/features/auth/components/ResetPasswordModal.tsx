import { X } from 'lucide-react'

interface ResetPasswordModalProps {
  resetStep: 1 | 2
  resetEmail: string
  resetCode: string
  debugCode: string
  newPassword: string
  resetMsg: string
  resetErr: string
  codeExpiresIn: number
  resendCountdown: number
  onClose: () => void
  onEmailChange: (value: string) => void
  onCodeChange: (value: string) => void
  onNewPasswordChange: (value: string) => void
  onForgot: () => void
  onReset: () => void
}

export default function ResetPasswordModal({
  resetStep,
  resetEmail,
  resetCode,
  debugCode,
  newPassword,
  resetMsg,
  resetErr,
  codeExpiresIn,
  resendCountdown,
  onClose,
  onEmailChange,
  onCodeChange,
  onNewPasswordChange,
  onForgot,
  onReset,
}: ResetPasswordModalProps) {
  const canResend = resendCountdown <= 0
  const expiryText = codeExpiresIn > 0
    ? `有效期 ${formatSeconds(codeExpiresIn)}`
    : '验证码已过期，请重新获取'

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content auth-reset-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="reset-password-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <h3 id="reset-password-title">找回密码</h3>
          <button type="button" className="modal-close" onClick={onClose} aria-label="关闭找回密码弹层">
            <X size={20} />
          </button>
        </div>

        {resetMsg && <div className="success-msg">{resetMsg}</div>}
        {resetErr && <div className="error-msg" role="alert">{resetErr}</div>}

        {resetStep === 1 && (
          <>
            <div className="form-group">
              <label>注册邮箱</label>
              <input
                type="email"
                value={resetEmail}
                onChange={(event) => onEmailChange(event.target.value)}
                placeholder="请输入注册时使用的邮箱"
              />
            </div>
            <button type="button" className="btn btn-primary btn-block" onClick={onForgot} disabled={!canResend}>
              {canResend ? '获取验证码' : `${resendCountdown} 秒后重发`}
            </button>
          </>
        )}

        {resetStep === 2 && (
          <>
            <div className={`auth-email-code-status${codeExpiresIn <= 0 ? ' is-expired' : ''}`}>
              <span>验证码已发送至 {resetEmail}</span>
              <strong>{expiryText}</strong>
            </div>
            {debugCode && (
              <div className="success-msg auth-debug-code">
                本地模拟邮箱验证码：<strong>{debugCode}</strong>
                <span>生产环境将通过邮件发送</span>
              </div>
            )}
            <div className="form-group">
              <label>验证码</label>
              <input
                type="text"
                value={resetCode}
                onChange={(event) => onCodeChange(event.target.value)}
                placeholder="输入 6 位验证码"
                maxLength={6}
              />
            </div>
            <div className="form-group">
              <label>新密码</label>
              <input
                type="password"
                value={newPassword}
                onChange={(event) => onNewPasswordChange(event.target.value)}
                placeholder="至少 8 位"
              />
            </div>
            <button type="button" className="btn btn-primary btn-block" onClick={onReset}>
              重置密码
            </button>
            <button type="button" className="btn btn-ghost btn-block" onClick={onForgot} disabled={!canResend}>
              {canResend ? '重新获取验证码' : `${resendCountdown} 秒后重发`}
            </button>
          </>
        )}
      </div>
    </div>
  )
}

function formatSeconds(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  if (minutes <= 0) return `${seconds} 秒`
  return `${minutes} 分 ${seconds.toString().padStart(2, '0')} 秒`
}
