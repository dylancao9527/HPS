import { Link } from 'react-router-dom'
import { TodayHealthTasksSection } from '@/features/health-tasks'
import { WeeklyReportSummarySection } from '@/features/weekly-report'

export default function HomePage() {
  return (
    <div className="page-shell">
      <header className="page-header">
        <div className="page-header-main">
          <h1 className="page-title">首页</h1>
          <p className="page-desc">今日状态与常用入口。</p>
        </div>
      </header>

      <TodayHealthTasksSection />

      <WeeklyReportSummarySection />

      <section className="dashboard-links" aria-label="常用操作">
        <Link className="dashboard-primary-action" to="/predict">
          <span className="dashboard-action-kicker">Risk prediction</span>
          <strong>开始预测</strong>
          <span>评估风险，查看趋势与建议</span>
        </Link>
        <div className="dashboard-secondary-actions">
          <Link className="dashboard-secondary-action" to="/bp-records">
            <strong>记录血压</strong>
            <span>补充今日数据</span>
          </Link>
          <Link className="dashboard-secondary-action" to="/history">
            <strong>查看历史</strong>
            <span>回顾预测结果</span>
          </Link>
        </div>
      </section>
    </div>
  )
}
