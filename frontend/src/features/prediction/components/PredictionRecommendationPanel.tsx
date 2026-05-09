import Card from '@/components/Card'
import type { PredictionResult } from '@/types/prediction'
import RecommendationList from '@/features/prediction/components/RecommendationList'

interface PredictionRecommendationPanelProps {
  result: PredictionResult
  withCard?: boolean
}

export default function PredictionRecommendationPanel({
  result,
  withCard = true,
}: PredictionRecommendationPanelProps) {
  const recommendations = result.recommendations

  const content = (
    <RecommendationList
      recommendations={Array.isArray(recommendations) ? recommendations : undefined}
    />
  )

  if (!withCard) {
    return <div className="prediction-results-panel">{content}</div>
  }

  return (
    <div className="prediction-results-panel">
      <Card title="健康建议" className="prediction-section" titleAs="h2">
        {content}
      </Card>
    </div>
  )
}

