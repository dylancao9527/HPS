import {
  formatRiskLevelLabel,
  formatRiskProbability,
  getRiskToneClass,
} from '@/features/shared/riskPresentation'

interface RiskBadgeProps {
  probability?: number | null
  level?: string | null
  color?: string | null
}

export default function RiskBadge({ probability, level, color }: RiskBadgeProps) {
  const pct = formatRiskProbability(probability, '0.0%')
  const displayLevel = formatRiskLevelLabel(level, '风险评估中')
  const toneClass = getRiskToneClass(level, 'risk-overview', 'risk-overview--custom')
  const customStyle = toneClass === 'risk-overview--custom' && color
    ? ({ '--risk-accent': color } as React.CSSProperties)
    : undefined

  return (
    <div className={`risk-overview ${toneClass}`} style={customStyle}>
      <div className="risk-badge">
        <span className="probability">{pct}</span>
        <span className="label">{displayLevel}</span>
      </div>
      <div className="risk-info">
        <p className="risk-kicker">高血压风险等级</p>
        <h3 className="risk-level-heading">{displayLevel}</h3>
        <div className="risk-summary-grid" aria-label="风险摘要指标">
          <div className="risk-summary-item">
            <span className="risk-summary-label">高血压风险概率</span>
            <strong className="risk-summary-value">{pct}</strong>
          </div>
          <div className="risk-summary-item">
            <span className="risk-summary-label">风险等级</span>
            <strong className="risk-summary-value">{displayLevel}</strong>
          </div>
        </div>
        <p>当前结果可作为未来7天血压管理、复测安排和健康建议执行的参考。</p>
      </div>
    </div>
  )
}
