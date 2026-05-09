import { useEffect, useState } from 'react'
import { getStats } from '@/features/admin/api/adminApi'
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { AdminStats } from '@/types/admin'
import { chartPalette } from '@/features/shared/chartPalette'

const statConfig: Array<{
  key: keyof Pick<AdminStats, 'total_users' | 'total_bp_records' | 'total_predictions'>
  label: string
  tone: string
}> = [
  { key: 'total_users', label: '注册用户', tone: 'primary' },
  { key: 'total_bp_records', label: '血压记录', tone: 'success' },
  { key: 'total_predictions', label: '预测次数', tone: 'violet' },
]

const chartTooltipStyle = {
  borderRadius: '10px',
  border: '1px solid var(--border)',
  background: 'var(--card-bg)',
}

interface OverviewChartDatum {
  name: string
  value: number
  fill: string
}

export default function AdminOverview() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [loading, setLoading] = useState(true)
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
        setError(caughtError instanceof Error ? caughtError.message : '平台摘要加载失败')
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  if (loading) {
    return (
      <section className="page-section" aria-label="系统概览加载中">
        <div className="card state-card admin-loading-state">
          <div className="spinner" />
          <p className="page-section-desc">正在加载平台摘要…</p>
        </div>
      </section>
    )
  }

  if (!stats) {
    return (
      <section className="page-section" aria-label="系统概览加载失败">
        <div className="card state-card admin-loading-state">
          <p className="page-section-desc">{error || '平台摘要加载失败'}</p>
        </div>
      </section>
    )
  }

  const overviewChartData: OverviewChartDatum[] = [
    { name: '注册用户', value: stats.total_users, fill: chartPalette.diastolic },
    { name: '血压记录', value: stats.total_bp_records, fill: chartPalette.success },
    { name: '预测次数', value: stats.total_predictions, fill: chartPalette.risk },
    { name: '今日新增', value: stats.today_users, fill: chartPalette.warning },
    { name: '今日预测', value: stats.today_predictions, fill: chartPalette.danger },
  ]

  const todayHighlights = [
    {
      label: '今日新增用户',
      value: stats.today_users ?? 0,
      hint: '反映当天注册活跃度',
      tone: 'warning',
    },
    {
      label: '今日预测次数',
      value: stats.today_predictions ?? 0,
      hint: '反映当天预测使用情况',
      tone: 'danger',
    },
    {
      label: '可导出训练样本',
      value: stats.training_export?.exportable_samples ?? 0,
      hint: '当前可用于再训练的有效样本',
      tone: 'violet',
    },
  ]

  return (
    <section className="page-section" aria-labelledby="admin-overview-panels-title">
      <div className="page-section-heading">
        <div>
          <h2 id="admin-overview-panels-title" className="page-section-title">运行看板</h2>
          <p className="page-section-desc">把平台规模、当日活跃和训练样本状态分成摘要卡与对比图，方便先看全局再决定下一步管理动作。</p>
        </div>
      </div>

      <div className="admin-overview-layout">
        <section className="card admin-overview-hero">
          <div className="admin-overview-hero-head">
            <div>
              <div className="card-title">平台运行概况</div>
              <p className="admin-chart-subtitle">围绕用户规模、数据积累与训练样本可用度，快速判断系统当前运行状态。</p>
            </div>
          </div>

          <div className="stats-grid admin-stats-grid-compact">
            {statConfig.map(({ key, label, tone }) => (
              <div className={`stat-card admin-stat-card admin-stat-card--${tone}`} key={key}>
                <div>
                  <div className="stat-value">{stats[key] ?? 0}</div>
                  <div className="stat-label">{label}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="admin-highlight-strip">
            {todayHighlights.map((item) => (
              <div key={item.label} className={`admin-highlight-card admin-highlight-card--${item.tone}`}>
                <span className="admin-highlight-accent" />
                <div>
                  <div className="admin-highlight-label">{item.label}</div>
                  <div className="admin-highlight-value">{item.value}</div>
                  <div className="admin-highlight-hint">{item.hint}</div>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="card admin-chart-card admin-overview-chart-card">
          <div className="admin-chart-header">
            <div>
              <div className="card-title">系统总体数据对比</div>
              <p className="admin-chart-subtitle">通过统一图表对比累计业务规模与当日活跃度，便于展示系统运行成果。</p>
            </div>
          </div>
          <div className="admin-chart-shell">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={overviewChartData} margin={{ top: 8, right: 12, left: 0, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip contentStyle={chartTooltipStyle} formatter={(value: number | string) => [value, '数量']} />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {overviewChartData.map((entry) => (
                    <Cell key={entry.name} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>
    </section>
  )
}
