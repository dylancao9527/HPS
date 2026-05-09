interface RegisterEmailCodeSectionProps {
  email: string
  emailCode: string
  debugCode: string
  codeSent: boolean
  codeSending: boolean
  sentEmail: string
  codeExpiresIn: number
  resendCountdown: number
  onEmailChange: (value: string) => void
  onEmailCodeChange: (value: string) => void
  onSendCode: () => void
}

function formatSeconds(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  if (minutes <= 0) return `${seconds} 秒`
  return `${minutes} 分 ${seconds.toString().padStart(2, '0')} 秒`
}

export default function RegisterEmailCodeSection({
  email,
  emailCode,
  debugCode,
  codeSent,
  codeSending,
  sentEmail,
  codeExpiresIn,
  resendCountdown,
  onEmailChange,
  onEmailCodeChange,
  onSendCode,
}: RegisterEmailCodeSectionProps) {
  const canResend = resendCountdown <= 0
  const emailCodeStatus = codeExpiresIn > 0
    ? `有效期 ${formatSeconds(codeExpiresIn)}`
    : '验证码已过期，请重新获取'

  return (
    <>
      <div className="form-group">
        <label>邮箱</label>
        <div className="auth-input-row">
          <input
            type="email"
            value={email}
            onChange={(event) => onEmailChange(event.target.value)}
            placeholder="用于登录和找回密码"
          />
          <button type="button" className="btn btn-primary" onClick={onSendCode} disabled={codeSending || !canResend}>
            {codeSending ? '发送中...' : !canResend ? `${resendCountdown} 秒后重发` : codeSent ? '重新发送' : '发送验证码'}
          </button>
        </div>
      </div>

      {codeSent && (
        <div className={`auth-email-code-status${codeExpiresIn <= 0 ? ' is-expired' : ''}`}>
          <span>验证码已发送至 {sentEmail || email}</span>
          <strong>{emailCodeStatus}</strong>
        </div>
      )}

      {codeSent && debugCode && (
        <div className="success-msg auth-debug-code">
          本地模拟邮箱验证码：<strong>{debugCode}</strong>
          <span>生产环境通过邮件发送</span>
        </div>
      )}

      <div className="form-group">
        <label>邮箱验证码</label>
        <input
          type="text"
          value={emailCode}
          onChange={(event) => onEmailCodeChange(event.target.value)}
          placeholder={codeSent ? '输入 6 位验证码' : '请先获取验证码'}
          maxLength={6}
          disabled={!codeSent}
        />
      </div>
    </>
  )
}
