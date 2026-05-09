import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ExportPanel, getStats } from '@/features/admin'
import type { AdminStats } from '@/types/admin'

export default function AdminExportPage() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    getStats()
      .then((data) => {
        if (!active) return
        setStats(data)
      })
      .catch((caughtError: unknown) => {
        if (!active) return
        setError(caughtError instanceof Error ? caughtError.message : '导出摘要加载失败')
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <div className="page-shell">
      <header className="page-header">
        <div className="page-header-main">
          <span className="page-eyebrow">Admin export</span>
          <h1 className="page-title">数据导出</h1>
          <p className="page-desc">先确认当前训练样本规模与标签来源，再执行导出动作，避免在缺少上下文时直接触发数据输出。</p>
        </div>
        <div className="page-header-actions">
          <Link className="btn btn-ghost btn-sm" to="/admin/governance">查看预测治理</Link>
        </div>
        {stats?.training_export && (
          <div className="page-meta-list" aria-label="导出摘要">
            <span className="page-meta-chip">可导出 {stats.training_export.exportable_samples} 条样本</span>
            <span className="page-meta-chip">正样本 {(stats.training_export.positive_ratio * 100).toFixed(1)}%</span>
          </div>
        )}
      </header>

      <section className="page-section" aria-labelledby="admin-export-panel-title">
        <div className="page-section-heading">
          <div>
            <h2 id="admin-export-panel-title" className="page-section-title">导出与样本概况</h2>
            <p className="page-section-desc">图表和摘要用于帮助管理员先理解当前数据状态，再决定是否执行训练数据导出。</p>
          </div>
        </div>
        <ExportPanel stats={stats} />
        {error && <p className="page-section-desc">{error}</p>}
      </section>
    </div>
  )
}
