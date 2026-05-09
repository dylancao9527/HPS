import Card from '@/components/Card'
import type { HistoryRecord } from '@/types/history'
import {
  formatRiskLevelLabel,
  formatRiskProbability,
  getRiskToneKey,
} from '@/features/shared/riskPresentation'

interface HistoryListProps {
  records?: HistoryRecord[] | null
}

export default function HistoryList({ records }: HistoryListProps) {
  if (!records || records.length === 0) {
    return <Card title="7天风险预测历史"><p className="empty-text">暂无预测记录。</p></Card>
  }

  return (
    <div className="history-list">
      {records.map((r) => (
        <Card key={r.id} title={null}>
          <div className="history-item">
            <div className="history-header">
              <span className="history-date">
                {r.created_at ? new Date(r.created_at).toLocaleString('zh-CN') : '-'}
              </span>
              <span
                className="history-badge"
                style={{ color: riskToneColor(r.risk_level) }}
              >
                {formatRiskLevelLabel(r.risk_level)} ({formatRiskProbability(r.risk_probability, '0.0%')})
              </span>
            </div>
            <div className="history-details">
              <div className="history-tags">
                <span>7天风险预测</span>
              </div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

function riskToneColor(riskLevel?: string | null): string {
  const tone = getRiskToneKey(riskLevel)
  if (tone === 'high') return '#ef4444'
  if (tone === 'medium') return '#f59e0b'
  if (tone === 'low') return '#22c55e'
  return 'var(--text-muted)'
}
