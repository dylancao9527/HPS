import { useCallback, useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import Captcha from '@/components/Captcha'
import { useAuth } from '@/hooks/useAuth'
import { getLatestMockEmail, request, shouldExposeLocalMockEmailCode } from '@/config/api'
import ResetPasswordModal from '@/features/auth/components/ResetPasswordModal'
import {
  getEmailValidationError,
  getErrorMessage,
  getPasswordValidationError,
} from '@/features/auth/validation'
import type { EmailCodeResponse, UserRole } from '@/types/auth'

interface LoginFormProps {
  loginRole: UserRole
  registerHref?: string
  alternateLoginHref?: string
  alternateLoginLabel?: string
}

type ForgotPasswordResponse = EmailCodeResponse

interface ResetPasswordResponse {
  message?: string
}

export default function LoginForm({
  loginRole,
  registerHref,
  alternateLoginHref,
  alternateLoginLabel,
}: LoginFormProps) {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [captchaOk, setCaptchaOk] = useState(false)

  const [showReset, setShowReset] = useState(false)
  const [resetStep, setResetStep] = useState<1 | 2>(1)
  const [resetEmail, setResetEmail] = useState('')
  const [resetCode, setResetCode] = useState('')
  const [debugCode, setDebugCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [resetMsg, setResetMsg] = useState('')
  const [resetErr, setResetErr] = useState('')
  const [resetCodeExpiresIn, setResetCodeExpiresIn] = useState(0)
  const [resetResendCountdown, setResetResendCountdown] = useState(0)

  const onCaptchaValid = useCallback((ok: boolean) => setCaptchaOk(ok), [])

  useEffect(() => {
    if (resetCodeExpiresIn <= 0 && resetResendCountdown <= 0) return
    const timer = window.setInterval(() => {
      setResetCodeExpiresIn((value) => Math.max(0, value - 1))
      setResetResendCountdown((value) => Math.max(0, value - 1))
    }, 1000)
    return () => window.clearInterval(timer)
  }, [resetCodeExpiresIn, resetResendCountdown])

  const resetModalState = () => {
    setShowReset(false)
    setResetStep(1)
    setResetEmail('')
    setResetCode('')
    setDebugCode('')
    setNewPassword('')
    setResetMsg('')
    setResetErr('')
    setResetCodeExpiresIn(0)
    setResetResendCountdown(0)
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')
    if (!username.trim()) {
      setError('请输入用户名或邮箱')
      return
    }
    if (!password) {
      setError('请输入密码')
      return
    }
    if (loginRole === 'admin' && !captchaOk) {
      setError('图形验证码不正确')
      return
    }

    setLoading(true)
    try {
      await login(username, password, {
        loginRole,
      })
    } catch (err) {
      setError(getErrorMessage(err, '登录失败'))
    } finally {
      setLoading(false)
    }
  }

  const handleForgot = async () => {
    setResetErr('')
    const emailError = getEmailValidationError(resetEmail)
    if (emailError) {
      setResetErr(emailError)
      return
    }
    try {
      const data = await request<ForgotPasswordResponse>('/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email: resetEmail }),
      })
      if (data.mock_service === 'local_email' && shouldExposeLocalMockEmailCode()) {
        const mockEmail = await getLatestMockEmail(resetEmail.trim(), 'reset_password')
        setDebugCode(mockEmail.code || '')
      } else {
        setDebugCode('')
      }
      setResetCode('')
      setResetStep(2)
      setResetCodeExpiresIn(data.expires_in_seconds ?? 300)
      setResetResendCountdown(data.resend_after_seconds ?? 60)
    } catch (err) {
      setResetErr(getErrorMessage(err, '验证码发送失败'))
    }
  }

  const handleReset = async () => {
    setResetErr('')
    if (!resetCode.trim()) {
      setResetErr('请输入验证码')
      return
    }

    const passwordError = getPasswordValidationError(newPassword)
    if (passwordError) {
      setResetErr(passwordError)
      return
    }

    try {
      const data = await request<ResetPasswordResponse>('/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify({ email: resetEmail, code: resetCode, new_password: newPassword }),
      })
      setResetMsg(data.message || '')
      setTimeout(() => {
        resetModalState()
      }, 2000)
    } catch (err) {
      setResetErr(getErrorMessage(err, '密码重置失败'))
    }
  }

  const openReset = () => {
    setShowReset(true)
    setResetStep(1)
    setResetEmail('')
    setResetCode('')
    setDebugCode('')
    setNewPassword('')
    setResetMsg('')
    setResetErr('')
    setResetCodeExpiresIn(0)
    setResetResendCountdown(0)
  }

  return (
    <>
      <div className="auth-form-shell">
        <div className="auth-form-header">
          <h2 className="auth-title">{loginRole === 'admin' ? '管理员登录' : '普通用户登录'}</h2>
        </div>
        {error && <div className="error-msg" role="alert">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>用户名 / 邮箱</label>
            <input type="text" value={username} onChange={(e: ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)} placeholder="请输入用户名或邮箱" />
          </div>
          <div className="form-group">
            <label>密码</label>
            <input type="password" value={password} onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)} placeholder="请输入密码" />
          </div>
          {loginRole === 'admin' && (
            <div className="form-group">
              <label>图形验证码</label>
              <Captcha onValid={onCaptchaValid} />
            </div>
          )}
          <div className="auth-inline-action">
            <button type="button" className="link-btn" onClick={openReset}>
              忘记密码？
            </button>
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? '登录中...' : '登录'}
          </button>
        </form>
        <div className="auth-route-links">
          {registerHref && (
            <span>还没有账号？<Link className="link-btn" to={registerHref}>立即注册</Link></span>
          )}
          {alternateLoginHref && alternateLoginLabel && (
            <Link className="link-btn" to={alternateLoginHref}>{alternateLoginLabel}</Link>
          )}
        </div>
      </div>

      {showReset && (
        <ResetPasswordModal
          resetStep={resetStep}
          resetEmail={resetEmail}
          resetCode={resetCode}
          debugCode={debugCode}
          newPassword={newPassword}
          resetMsg={resetMsg}
          resetErr={resetErr}
          codeExpiresIn={resetCodeExpiresIn}
          resendCountdown={resetResendCountdown}
          onClose={() => setShowReset(false)}
          onEmailChange={setResetEmail}
          onCodeChange={(value) => setResetCode(value.replace(/\D/g, '').slice(0, 6))}
          onNewPasswordChange={setNewPassword}
          onForgot={handleForgot}
          onReset={handleReset}
        />
      )}
    </>
  )
}
