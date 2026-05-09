import { Link } from 'react-router-dom'
import { AdminOverview } from '@/features/admin'

export default function AdminOverviewPage() {
  return (
    <div className="page-shell">
      <header className="page-header">
        <div className="page-header-main">
          <span className="page-eyebrow">Admin overview</span>
          <h1 className="page-title">系统概览</h1>
          <p className="page-desc">聚焦平台规模、当日活跃和训练样本可用度，优先回答管理员“现在最需要关注什么”。</p>
        </div>
        <div className="page-header-actions">
          <Link className="btn btn-ghost btn-sm" to="/admin/governance">进入预测治理</Link>
        </div>
      </header>
      <AdminOverview />
    </div>
  )
}
