import Card from '@/components/Card'
import type { HistoryDetail } from '@/types/history'
import type { PredictionResult } from '@/types/prediction'
import {
  getPredictionInsightFactors,
  summarizeTrendExplanation,
} from '@/features/prediction/explanation'
import type { PredictionComparison } from '@/features/prediction/explanation'

interface PredictionInsightPanelProps {
  result: PredictionResult | HistoryDetail
  comparison?: PredictionComparison | null
  comparisonLoading?: boolean
  showComparison?: boolean
}

function formatDateTime(value?: string | null): string {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}

export default function PredictionInsightPanel({
  result,
  comparison = null,
  comparisonLoading = false,
  showComparison = true,
}: PredictionInsightPanelProps) {
  const insightFactors = getPredictionInsightFactors(result)
  const trendExplanation = summarizeTrendExplanation(result.fusion_meta)

  return (
    <div className="prediction-insight-stack">
      <Card title="关键解读" className="prediction-insight-card prediction-insight-card--primary" titleAs="h2">
        <div className="prediction-insight-brief">
          <span>{trendExplanation}</span>
        </div>

        <div className="prediction-factor-list prediction-factor-list--compact">
          {insightFactors.map((factor) => (
            <article key={factor.id} className={`prediction-factor-card prediction-factor-card--${factor.tone}`}>
              <div className="prediction-factor-head">
                <h3>{factor.title}</h3>
                <span className="prediction-factor-value">{factor.value}</span>
              </div>
              <p>{factor.description}</p>
            </article>
          ))}
        </div>
      </Card>

      {showComparison && (
        <Card title="与上一次预测对比" className="prediction-insight-card" titleAs="h2">
          {comparisonLoading ? (
            <div className="prediction-empty-state prediction-empty-state--left">
              <div className="prediction-empty-title">正在读取上一条记录</div>
              <p className="prediction-empty-desc">系统正在生成本次结果和上一次预测之间的变化对比。</p>
            </div>
          ) : comparison ? (
            <>
              <div className="prediction-compare-meta">
                <span className="page-meta-chip">上一条记录时间：{formatDateTime(comparison.previousCreatedAt)}</span>
                {comparison.previousRiskLevel && (
                  <span className="page-meta-chip">上一条风险等级：{comparison.previousRiskLevel}</span>
                )}
              </div>
              <p className="prediction-insight-copy prediction-insight-copy--spaced">{comparison.summary}</p>

              <div className="prediction-compare-grid">
                {comparison.metrics.map((metric) => (
                  <article key={metric.label} className="prediction-compare-card">
                    <span className="prediction-compare-label">{metric.label}</span>
                    <div className="prediction-compare-values">
                      <span>当前：{metric.current}</span>
                      <span>上次：{metric.previous}</span>
                    </div>
                    <strong className={`prediction-compare-delta prediction-compare-delta--${metric.tone}`}>
                      {metric.delta}
                    </strong>
                  </article>
                ))}
              </div>
            </>
          ) : (
            <div className="prediction-empty-state prediction-empty-state--left">
              <div className="prediction-empty-title">暂无可对比的历史预测</div>
              <p className="prediction-empty-desc">至少完成两次预测后，系统才可以展示本次结果和上一次预测之间的变化。</p>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
