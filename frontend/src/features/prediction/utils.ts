import type { BloodPressureForecastPoint } from '@/types/prediction'
import {
  confidenceLabels,
  getBloodPressureTrendText,
} from '@/features/shared/riskPresentation'

export { confidenceLabels }

export function getPredictionTrendText(bpForecast?: BloodPressureForecastPoint[] | null): string {
  return getBloodPressureTrendText(bpForecast, 'prediction')
}
