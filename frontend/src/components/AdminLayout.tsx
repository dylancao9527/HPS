import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { LayoutDashboard, Users, Download, ShieldCheck, PanelLeftClose, PanelLeftOpen, LogOut } from 'lucide-react'
import ThemeToggle from '@/components/ThemeToggle'
import { useAuth } from '@/hooks/useAuth'
import logoIcon from '@/assets/logo.ico'

export default function AdminLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const { logout } = useAuth()

  return (
    <div className="app-layout admin-layout-shell">
      <nav className="navbar admin-topbar" aria-label="管理员顶栏">
        <div className="nav-brand nav-brand--admin">
          <img src={logoIcon} alt="" className="nav-brand-mark" />
          <div className="nav-brand-copy">
            <span className="nav-brand-title">管理后台</span>
            <span className="nav-brand-subtitle">运营与安全控制台</span>
          </div>
        </div>
        <div className="nav-actions admin-topbar-actions">
          <ThemeToggle />
          <button className="btn btn-ghost btn-sm admin-logout-button" onClick={logout}>
            <LogOut size={16} />
            <span>退出登录</span>
          </button>
        </div>
      </nav>

      <div className="admin-body">
        <aside className={`admin-sidebar${collapsed ? ' collapsed' : ''}`} aria-label="管理员导航">
          <button
            className="sidebar-toggle"
            type="button"
            onClick={() => setCollapsed(!collapsed)}
            aria-expanded={!collapsed}
            aria-controls="admin-sidebar-nav"
          >
            {collapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
            {!collapsed && <span>收起侧栏</span>}
          </button>
          <nav className="admin-sidebar-nav" id="admin-sidebar-nav">
            <NavLink to="/admin" end>
              <LayoutDashboard size={18} />
              <span>系统概览</span>
            </NavLink>
            <NavLink to="/admin/users">
              <Users size={18} />
              <span>用户管理</span>
            </NavLink>
            <NavLink to="/admin/governance">
              <ShieldCheck size={18} />
              <span>预测结果治理</span>
            </NavLink>
            <NavLink to="/admin/export">
              <Download size={18} />
              <span>数据导出</span>
            </NavLink>
          </nav>
        </aside>
        <main className="admin-content" id="admin-content" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}
