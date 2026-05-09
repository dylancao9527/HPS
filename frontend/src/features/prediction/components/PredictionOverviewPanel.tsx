import Card from '@/components/Card'
import type { PredictionResult } from '@/types/prediction'
import RiskBadge from '@/features/prediction/components/RiskBadge'

interface PredictionOverviewPanelProps {
  result: PredictionResult
  isUsingMedication: boolean
  trendText: string
}

export default function PredictionOverviewPanel({
  result,
  isUsingMedication,
  trendText,
}: PredictionOverviewPanelProps) {
  const clinicalNotices = [
    {
      show: true,
      title: '仅作健康管理参考',
      text: '本结果用于高血压风险筛查，不作为医学诊断依据；如血压持续异常或身体不适，请及时就医。',
      tone: 'warning',
    },
    {
      show: isUsingMedication,
      title: '已纳入服药背景',
      text: '长期按医嘱服用降压药会作为健康管理背景参考，仍需结合近期血压与趋势综合判断。',
      tone: 'success',
    },
  ]

  return (
    <div className="prediction-results-panel">
      <Card title="风险评估结果" className="prediction-section prediction-overview-card" titleAs="h2">
        <div className="prediction-overview-primary">
          <RiskBadge
            probability={result.risk_probability}
            level={result.risk_level}
            color={result.risk_color}
          />

          <div className="prediction-next-step" aria-label="下一步建议">
            <span className="prediction-next-step-label">下一步</span>
            <strong>先看趋势，再按建议记录血压</strong>
            <span>{trendText}</span>
          </div>
        </div>

        <div className="prediction-clinical-notices" aria-label="结果说明">
          {clinicalNotices
            .filter((notice) => notice.show)
            .map((notice) => (
              <div
                key={notice.title}
                className={`prediction-note prediction-note--${notice.tone} prediction-note--compact prediction-clinical-notice`}
              >
                <p className="prediction-note-title">{notice.title}</p>
                <p className="prediction-note-text">{notice.text}</p>
              </div>
            ))}
        </div>
      </Card>
    </div>
  )
}
