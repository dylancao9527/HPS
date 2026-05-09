import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { LoginForm } from '@/features/auth'
import { useAuth } from '@/hooks/useAuth'
import ThemeToggle from '@/components/ThemeToggle'
import logoIcon from '@/assets/logo.ico'
import type { UserRole } from '@/types/auth'

interface LoginPageProps {
  role?: UserRole
}

export default function LoginPage({ role = 'user' }: LoginPageProps) {
  const { user } = useAuth()
  const navigate = useNavigate()
  const isAdminLogin = role === 'admin'

  useEffect(() => {
    if (!user) return
    navigate(user.role === 'admin' ? '/admin' : '/', { replace: true })
  }, [user, navigate])

  return (
    <div className="auth-page">
      <div className="auth-theme-toggle">
        <ThemeToggle />
      </div>
      <section className="auth-card card" aria-label="身份验证">
        <div className="auth-brand">
          <img src={logoIcon} alt="" className="nav-brand-mark" />
          <span className="auth-brand-name">高血压风险预测系统</span>
        </div>
        <LoginForm
          loginRole={role}
          registerHref={isAdminLogin ? undefined : '/register'}
          alternateLoginHref={isAdminLogin ? '/login' : '/admin/login'}
          alternateLoginLabel={isAdminLogin ? '普通用户登录' : '管理员登录'}
        />
      </section>
    </div>
  )
}
