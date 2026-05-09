import { NavLink, Outlet } from 'react-router-dom'
import { Activity, CalendarDays, ClipboardList, HeartPulse, History, Home, UserRound } from 'lucide-react'
import ThemeToggle from '@/components/ThemeToggle'
import UserDropdown from '@/components/UserDropdown'
import logoIcon from '@/assets/logo.ico'

const navItems = [
  { to: '/', label: '首页', icon: Home, end: true },
  { to: '/predict', label: '7天预测', icon: HeartPulse },
  { to: '/bp-records', label: '血压记录', icon: Activity },
  { to: '/weekly-report', label: '周健康报告', icon: CalendarDays },
  { to: '/history', label: '预测历史', icon: History },
  { to: '/profile', label: '个人档案', icon: UserRound },
]

export default function Layout() {
  return (
    <div className="app-layout app-shell">
      <aside className="app-sidebar" aria-label="主导航">
        <div className="nav-brand app-sidebar-brand">
          <img src={logoIcon} alt="" className="nav-brand-mark" />
          <div className="nav-brand-copy">
            <span className="nav-brand-title">高血压风险预测系统</span>
            <span className="nav-brand-subtitle">健康管理工作台</span>
          </div>
        </div>

        <nav className="nav-links app-sidebar-nav">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end}>
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="app-sidebar-note">
          <ClipboardList size={16} />
          <span>仅供健康管理参考</span>
        </div>
      </aside>

      <div className="app-shell-main">
        <header className="app-topbar">
          <div className="app-topbar-copy">
            <span className="app-topbar-kicker">Health prediction</span>
            <span className="app-topbar-title">日常记录、7天风险预测与建议</span>
          </div>
          <div className="nav-actions">
            <ThemeToggle />
            <UserDropdown />
          </div>
        </header>

        <main className="main-content" id="main-content" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
