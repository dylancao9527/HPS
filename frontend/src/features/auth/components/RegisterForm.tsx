import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import Captcha from '@/components/Captcha'
import { getLatestMockEmail, request, shouldExposeLocalMockEmailCode } from '@/config/api'
import { useAuth } from '@/hooks/useAuth'
import RegisterEmailCodeSection from '@/features/auth/components/RegisterEmailCodeSection'
import {
  getEmailValidationError,
  getErrorMessage,
  getPasswordErrors,
  getPasswordStrength,
  getPasswordValidationError,
} from '@/features/auth/validation'
import type { EmailCodeResponse } from '@/types/auth'

interface RegisterFormProps {
  loginHref: string
}

type SendRegisterCodeResponse = EmailCodeResponse

export default function RegisterForm({ loginHref }: RegisterFormProps) {
  const { register } = useAuth()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [captchaOk, setCaptchaOk] = useState(false)

  const [emailCode, setEmailCode] = useState('')
  const [debugCode, setDebugCode] = useState('')
  const [codeSent, setCodeSent] = useState(false)
  const [codeSending, setCodeSending] = useState(false)
  const [sentEmail, setSentEmail] = useState('')
  const [codeExpiresIn, setCodeExpiresIn] = useState(0)
  const [resendCountdown, setResendCountdown] = useState(0)

  const strength = useMemo(() => getPasswordStrength(password), [password])
  const pwErrors = useMemo(() => getPasswordErrors(password), [password])

  const onCaptchaValid = useCallback((ok: boolean) => setCaptchaOk(ok), [])

  useEffect(() => {
    if (codeExpiresIn <= 0 && resendCountdown <= 0) return
    const timer = window.setInterval(() => {
      setCodeExpiresIn((value) => Math.max(0, value - 1))
      setResendCountdown((value) => Math.max(0, value - 1))
    }, 1000)
    return () => window.clearInterval(timer)
  }, [codeExpiresIn, resendCountdown])

  const handleEmailChange = (value: string) => {
    setEmail(value)
    setEmailCode('')
    setDebugCode('')
    setCodeSent(false)
    setSentEmail('')
    setCodeExpiresIn(0)
    setResendCountdown(0)
  }

  const handleEmailCodeChange = (value: string) => {
    setEmailCode(value.replace(/\D/g, '').slice(0, 6))
  }

  const handleSendCode = async () => {
    setError('')
    const emailError = getEmailValidationError(email)
    if (emailError) {
      setError(emailError)
      return
    }

    setCodeSending(true)
    try {
      const data = await request<SendRegisterCodeResponse>('/auth/send-register-code', {
        method: 'POST',
        body: JSON.stringify({ email: email.trim() }),
      })
      if (data.mock_service === 'local_email' && shouldExposeLocalMockEmailCode()) {
        const mockEmail = await getLatestMockEmail(email.trim(), 'register')
        setDebugCode(mockEmail.code || '')
      } else {
        setDebugCode('')
      }
      setCodeSent(true)
      setSentEmail(email.trim())
      setCodeExpiresIn(data.expires_in_seconds ?? 300)
      setResendCountdown(data.resend_after_seconds ?? 60)
    } catch (err) {
      setError(getErrorMessage(err, '验证码发送失败'))
    } finally {
      setCodeSending(false)
    }
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')

    if (!username.trim() || username.trim().length < 2) {
      setError('用户名不能为空且至少 2 位')
      return
    }
    const emailError = getEmailValidationError(email)
    if (emailError) {
      setError(emailError)
      return
    }
    if (!emailCode.trim()) {
      setError('请输入邮箱验证码')
      return
    }
    const passwordError = getPasswordValidationError(password)
    if (passwordError) {
      setError(passwordError)
      return
    }
    if (password !== confirm) {
      setError('两次密码不一致')
      return
    }
    if (!captchaOk) {
      setError('图形验证码不正确')
      return
    }

    setLoading(true)
    try {
      await register(username, password, email, emailCode)
    } catch (err) {
      setError(getErrorMessage(err, '注册失败'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-form-shell">
      <div className="auth-form-header">
        <h2 className="auth-title">注册</h2>
      </div>
      {error && <div className="error-msg" role="alert">{error}</div>}
      <form onSubmit={handleSubmit}>
        <RegisterEmailCodeSection
          email={email}
          emailCode={emailCode}
          debugCode={debugCode}
          codeSent={codeSent}
          codeSending={codeSending}
          sentEmail={sentEmail}
          codeExpiresIn={codeExpiresIn}
          resendCountdown={resendCountdown}
          onEmailChange={handleEmailChange}
          onEmailCodeChange={handleEmailCodeChange}
          onSendCode={handleSendCode}
        />

        <div className="form-group">
          <label>用户名</label>
          <input type="text" value={username} onChange={(e: ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)} placeholder="请输入用户名（至少2位）" />
        </div>
        <div className="form-group">
          <label>密码</label>
          <input type="password" value={password} onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)} placeholder="8~32位，含至少两种字符类型" />
          {password && (
            <div className="pw-strength">
              <div className="pw-strength-bar">
                <div className="pw-strength-fill" style={{ width: `${(strength.score / 3) * 100}%`, background: strength.color }} />
              </div>
              <span style={{ color: strength.color, fontSize: '0.78rem' }}>
                {strength.label}
              </span>
            </div>
          )}
          {password && pwErrors.length > 0 && (
            <div className="pw-hint">
              {pwErrors.map((item, index) => <span key={index}>• {item}</span>)}
            </div>
          )}
        </div>
        <div className="form-group">
          <label>确认密码</label>
          <input type="password" value={confirm} onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirm(e.target.value)} placeholder="请再次输入密码" />
        </div>
        <div className="form-group">
          <label>图形验证码</label>
          <Captcha onValid={onCaptchaValid} />
        </div>
        <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
          {loading ? '注册中...' : '注册'}
        </button>
      </form>
      <p className="auth-switch">
        已有账号？<Link className="link-btn" to={loginHref}>返回登录</Link>
      </p>
    </div>
  )
}
