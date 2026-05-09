import { X } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import type { HistoryDetail } from '@/types/history'
import { PredictionRecommendationPanel } from '@/features/prediction'
import { chartPalette } from '@/features/shared/chartPalette'
import {
  formatDateTime,
  formatRiskLevelLabel,
  formatRiskProbability,
  getHistoryTrendText,
  getRiskToneClass,
} from '@/features/history/utils'

interface HistoryDetailPanelProps {
  detail: HistoryDetail
  onClose: () => void
}

function hasRecommendationContent(recommendations: HistoryDetail['recommendations']): boolean {
  if (!recommendations) {
    return false
  }

  if (Array.isArray(recommendations)) {
    return recommendations.length > 0
  }

  return true
}

export default function HistoryDetailPanel({ detail, onClose }: HistoryDetailPanelProps) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content history-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="history-detail-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <h3 id="history-detail-title">用户端预测摘要</h3>
            <p className="history-detail-meta">{formatDateTime(detail.created_at)}</p>
          </div>
          <button type="button" className="modal-close" onClick={onClose} aria-label="关闭详情">
            <X size={20} />
          </button>
        </div>

        <div className="history-detail-stack">
          <section className="card history-detail-overview-card">
            <div className="history-detail-hero">
              <div className={`history-detail-risk ${getRiskToneClass(detail.risk_level)}`}>
                <span className="history-detail-risk-probability">{formatRiskProbability(detail.risk_probability, '0.0%')}</span>
                <span className="history-detail-risk-label">{formatRiskLevelLabel(detail.risk_level)}</span>
              </div>
              <div className="history-detail-summary">
                <h4>{formatRiskLevelLabel(detail.risk_level)}</h4>
                <div className="page-meta-list" aria-label="详情摘要">
                  <span className="page-meta-chip">7天风险预测</span>
                  <span className="page-meta-chip">{getHistoryTrendText(detail.bp_forecast)}</span>
                </div>
              </div>
            </div>
            <p className="history-detail-copy">历史预测结果仅作健康管理参考，不作为医学诊断依据。若多次预测结果偏高或近期血压持续异常，请及时到正规医院进一步检查。</p>
          </section>

          {detail.bp_forecast && detail.bp_forecast.length > 0 && (
            <section className="card">
              <div className="card-title">未来7天血压趋势</div>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={detail.bp_forecast}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="day" tick={{ fontSize: 12 }} label={{ value: '天', position: 'right' }} />
                    <YAxis tick={{ fontSize: 12 }} domain={['auto', 'auto']} />
                    <Tooltip />
                    <Line type="monotone" dataKey="systolic" stroke={chartPalette.systolic} name="收缩压" strokeWidth={2} dot={{ r: 3 }} />
                    <Line type="monotone" dataKey="diastolic" stroke={chartPalette.diastolic} name="舒张压" strokeWidth={2} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>
          )}

          {hasRecommendationContent(detail.recommendations) && (
            <section className="card">
              <div className="card-title">健康建议</div>
              <PredictionRecommendationPanel result={detail} withCard={false} />
            </section>
          )}
        </div>
      </div>
    </div>
  )
}
