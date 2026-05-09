import Card from '@/components/Card'
import type { PredictionResult } from '@/types/prediction'
import BPChart from '@/features/prediction/components/BPChart'

interface PredictionChartPanelProps {
  result: PredictionResult
}

export default function PredictionChartPanel({ result }: PredictionChartPanelProps) {
  return (
    <div className="prediction-results-panel">
      <Card
        title={`未来${result.forecast_days || 7}天血压趋势预测`}
        className="prediction-section prediction-chart-card"
        titleAs="h2"
      >
        <BPChart data={result.bp_forecast} />
      </Card>
    </div>
  )
}
