import type { GuidelineTopicCard, PredictionRecommendation, RecommendationPriority } from '@/types/prediction'

const priorityLabels: Record<RecommendationPriority, string> = {
  high: '重点干预',
  medium: '持续观察',
  low: '日常管理',
}

const topicLabels: Record<string, string> = {
  urgent: '紧急提醒',
  follow_up: '随访建议',
  lifestyle: '生活方式',
  prevention: '预防建议',
  maintenance: '日常管理',
}

interface RecommendationListProps {
  actions?: string[] | null
  recommendations?: PredictionRecommendation[] | GuidelineTopicCard[] | null
}

function isTopicCards(recs: PredictionRecommendation[] | GuidelineTopicCard[]): recs is GuidelineTopicCard[] {
  return recs.length > 0 && 'topic' in recs[0]
}

export default function RecommendationList({ actions, recommendations }: RecommendationListProps) {
  if (actions?.length) {
    return (
      <ul className="prediction-action-list">
        {actions.map((action, index) => (
          <li key={`${index}-${action}`} className="prediction-action-item">
            {action}
          </li>
        ))}
      </ul>
    )
  }

  if (!recommendations?.length) {
    return (
      <div className="prediction-empty-state">
        <p className="prediction-empty-title">暂无健康建议</p>
        <p className="prediction-empty-desc">完成预测后，这里会展示个性化健康建议。</p>
      </div>
    )
  }

  if (isTopicCards(recommendations)) {
    return (
      <div className="rec-list">
        {recommendations.map((card) => (
          <div key={card.topic} className="rec-item follow_up">
            <div className="rec-item-header">
              <span className="rec-priority-badge medium">
                {topicLabels[card.topic] ?? card.topic}
              </span>
              <h4>{card.summary}</h4>
            </div>
            {card.reason && <p>{card.reason}</p>}
            {card.actions?.length > 0 && (
              <ul className="prediction-action-list">
                {card.actions.map((action, i) => (
                  <li key={i} className="prediction-action-item">{action}</li>
                ))}
              </ul>
            )}
            {card.source_label && <p className="rec-basis">{card.source_label}</p>}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="rec-list">
      {(recommendations as PredictionRecommendation[]).map((rec) => {
        const priority = rec.priority || 'low'
        const priorityLabel = priorityLabels[priority] || priorityLabels.low
        return (
          <div
            key={`${priority}-${rec.title}-${rec.content}`}
            className={`rec-item ${priority}`}
          >
            <div className="rec-item-header">
              <span className={`rec-priority-badge ${priority}`}>{priorityLabel}</span>
              <h4>{rec.title}</h4>
            </div>
            <p>{rec.content}</p>
            {rec.basis ? <p className="rec-basis">{rec.basis}</p> : null}
          </div>
        )
      })}
    </div>
  )
}
