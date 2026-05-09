import Card from '@/components/Card'
import type { PredictionGovernanceSummary } from '@/types/admin'
import { formatPercentRate } from '@/features/admin/governancePresentation'
import {
  formatConfidenceLevelLabel,
  formatRiskLevelLabel,
} from '@/features/shared/riskPresentation'

interface PredictionGovernanceOverviewProps {
  summary: PredictionGovernanceSummary | null
  loading?: boolean
}

export default function PredictionGovernanceOverview({
  summary,
  loading = false,
}: PredictionGovernanceOverviewProps) {
  if (loading) {
    return (
      <Card title="治理摘要" className="admin-chart-card admin-chart-card--flush">
        <div className="admin-loading-state" role="status" aria-live="polite">
          <div className="spinner" />
          <p className="page-section-desc">正在加载治理摘要…</p>
        </div>
      </Card>
    )
  }

  if (!summary) {
    return (
      <Card title="治理摘要" className="admin-chart-card admin-chart-card--flush">
        <p className="empty-text">暂无治理摘要数据。</p>
      </Card>
    )
  }

  return (
    <Card title="治理摘要" className="admin-chart-card admin-chart-card--flush">
      <div className="summary-grid admin-summary-grid">
        <div className="summary-item">
          <span className="summary-label">预测总数</span>
          <span className="summary-value">{summary.total_predictions ?? 0}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">高风险预测</span>
          <span className="summary-value">{summary.high_risk_predictions}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">低置信度占比</span>
          <span className="summary-value">{formatPercentRate(summary.low_confidence_rate)}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">异常预测</span>
          <span className="summary-value">{summary.anomaly_predictions}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">数据不足预测</span>
          <span className="summary-value">{summary.insufficient_data_predictions}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Prophet 复用/重训</span>
          <span className="summary-value">{summary.prophet_model_reuse_count}/{summary.prophet_model_retrain_count}</span>
        </div>
      </div>

      <div className="admin-chart-grid" style={{ marginBottom: 0 }}>
        <div className="card admin-chart-card admin-chart-card--flush">
          <div className="card-title">风险分布</div>
          <div className="admin-chart-subtitle">按风险等级汇总</div>
          <div className="summary-grid">
            {Object.keys(summary.risk_distribution || {}).length > 0 ? (
              Object.entries(summary.risk_distribution || {}).map(([key, value]) => (
                <div key={key} className="summary-item">
                  <span className="summary-label">{formatRiskLevelLabel(key, '未知')}</span>
                  <span className="summary-value">{value}</span>
                </div>
              ))
            ) : (
              <p className="empty-text">暂无风险分布数据。</p>
            )}
          </div>
        </div>

        <div className="card admin-chart-card admin-chart-card--flush">
          <div className="card-title">置信度分布</div>
          <div className="admin-chart-subtitle">按置信度汇总</div>
          <div className="summary-grid">
            {Object.keys(summary.confidence_distribution || {}).length > 0 ? (
              Object.entries(summary.confidence_distribution || {}).map(([key, value]) => (
                <div key={key} className="summary-item">
                  <span className="summary-label">{formatConfidenceLevelLabel(key, '未知')}</span>
                  <span className="summary-value">{value}</span>
                </div>
              ))
            ) : (
              <p className="empty-text">暂无置信度分布数据。</p>
            )}
          </div>
        </div>
      </div>
    </Card>
  )
}
