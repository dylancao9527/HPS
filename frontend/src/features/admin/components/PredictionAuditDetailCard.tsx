import Card from '@/components/Card'
import type { PredictionAuditDetail } from '@/types/admin'
import {
  buildAuditDetailPresentation,
  type AuditDetailReason,
  type AuditDetailRecommendation,
  type AuditDetailRow,
} from '@/features/admin/auditDetailPresentation'
import { formatAnomalyFlagList } from '@/features/admin/governancePresentation'
import {
  formatConfidenceLevelLabel,
  formatRiskLevelLabel,
  formatRiskProbability,
} from '@/features/shared/riskPresentation'

interface PredictionAuditDetailCardProps {
  detail: PredictionAuditDetail | null
  loading?: boolean
}

function DetailRowGrid({ rows }: { rows: AuditDetailRow[] }) {
  return (
    <div className="admin-detail-row-grid">
      {rows.map((row) => (
        <div key={row.label} className="admin-detail-row">
          <span className="admin-detail-label">{row.label}</span>
          <span className="admin-detail-value">{row.value}</span>
        </div>
      ))}
    </div>
  )
}

function ReasonList({
  items,
  emptyText,
}: {
  items: AuditDetailReason[]
  emptyText: string
}) {
  if (!items.length) {
    return <p className="empty-text admin-detail-empty">{emptyText}</p>
  }

  return (
    <ul className="admin-detail-reason-list">
      {items.map((item) => (
        <li key={`${item.code}-${item.label}`} className="admin-detail-reason-item">
          <span className="admin-detail-reason-title">{item.label}</span>
          <p>{item.description}</p>
        </li>
      ))}
    </ul>
  )
}

function RecommendationCards({ items }: { items: AuditDetailRecommendation[] }) {
  if (!items.length) {
    return <p className="empty-text admin-detail-empty">暂无指南型健康建议。</p>
  }

  return (
    <div className="admin-guideline-list">
      {items.map((item) => (
        <article key={item.key} className="admin-guideline-item">
          <div className="admin-guideline-header">
            <span className="admin-guideline-badge">{item.badge}</span>
            <h4>{item.title}</h4>
          </div>
          <p className="admin-guideline-summary">{item.summary}</p>
          {item.reason && <p className="admin-guideline-reason">{item.reason}</p>}
          {item.actions.length > 0 && (
            <ul className="prediction-action-list admin-guideline-actions">
              {item.actions.map((action) => (
                <li key={action} className="prediction-action-item">{action}</li>
              ))}
            </ul>
          )}
          {item.sourceLabel && <p className="admin-guideline-source">{item.sourceLabel}</p>}
        </article>
      ))}
    </div>
  )
}

export default function PredictionAuditDetailCard({
  detail,
  loading = false,
}: PredictionAuditDetailCardProps) {
  if (loading) {
    return (
      <Card title="预测结果治理明细" className="admin-chart-card admin-chart-card--flush">
        <div className="admin-loading-state" role="status" aria-live="polite">
          <div className="spinner" />
          <p className="page-section-desc">正在加载治理明细…</p>
        </div>
      </Card>
    )
  }

  if (!detail) {
    return (
      <Card title="预测结果治理明细" className="admin-chart-card admin-chart-card--flush">
        <p className="empty-text">请选择一条预测记录查看详情。</p>
      </Card>
    )
  }

  const presentation = buildAuditDetailPresentation(detail)

  return (
    <Card title={`预测结果治理明细 #${detail.prediction_id}`} className="admin-chart-card admin-chart-card--flush">
      <div className="summary-grid admin-summary-grid">
        <div className="summary-item">
          <span className="summary-label">风险等级</span>
          <span className="summary-value">{formatRiskLevelLabel(detail.risk_level)}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">风险概率</span>
          <span className="summary-value">{formatRiskProbability(detail.risk_probability)}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">置信度</span>
          <span className="summary-value">{formatConfidenceLevelLabel(detail.confidence_level)}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">训练天数</span>
          <span className="summary-value">{detail.data_days_used ?? '—'}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">异常标记</span>
          <span className="summary-value">{formatAnomalyFlagList(detail.anomaly_flags)}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">创建时间</span>
          <span className="summary-value">{detail.created_at ? new Date(detail.created_at).toLocaleString('zh-CN') : '—'}</span>
        </div>
      </div>

      <div className="admin-governance-detail-grid">
        <section className="admin-governance-detail-section">
          <h3 className="page-section-title">输入快照</h3>
          <DetailRowGrid rows={presentation.inputRows} />
        </section>
        <section className="admin-governance-detail-section">
          <h3 className="page-section-title">融合元数据</h3>
          <DetailRowGrid rows={presentation.fusionRows} />
          <ReasonList items={presentation.fusionReasons} emptyText="暂无融合修正原因。" />
        </section>
        <section className="admin-governance-detail-section">
          <h3 className="page-section-title">预测点摘要</h3>
          <DetailRowGrid rows={presentation.forecastRows} />
        </section>
        <section className="admin-governance-detail-section">
          <h3 className="page-section-title">置信度原因</h3>
          <ReasonList items={presentation.confidenceReasons} emptyText="暂无置信度原因。" />
        </section>
        <section className="admin-governance-detail-section admin-governance-detail-section--wide">
          <h3 className="page-section-title">指南型健康建议</h3>
          <RecommendationCards items={presentation.recommendations} />
        </section>
      </div>
    </Card>
  )
}
