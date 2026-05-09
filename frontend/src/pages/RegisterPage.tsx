import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { RegisterForm } from '@/features/auth'
import { useAuth } from '@/hooks/useAuth'
import ThemeToggle from '@/components/ThemeToggle'
import logoIcon from '@/assets/logo.ico'

export default function RegisterPage() {
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!user) return
    navigate(user.role === 'admin' ? '/admin' : '/', { replace: true })
  }, [user, navigate])

  return (
    <div className="auth-page">
      <div className="auth-theme-toggle">
        <ThemeToggle />
      </div>
      <section className="auth-card card" aria-label="注册账号">
        <div className="auth-brand">
          <img src={logoIcon} alt="" className="nav-brand-mark" />
          <span className="auth-brand-name">高血压风险预测系统</span>
        </div>
        <div className="auth-route-pill">
          <Link className="btn btn-ghost btn-sm" to="/login">普通用户登录</Link>
          <Link className="btn btn-ghost btn-sm" to="/admin/login">管理员登录</Link>
        </div>
        <RegisterForm loginHref="/login" />
      </section>
    </div>
  )
}
