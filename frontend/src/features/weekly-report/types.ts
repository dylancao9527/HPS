export interface WeeklyBloodPressureSummary {
  current_record_days: number
  previous_record_days: number
  current_average_systolic: number | null
  previous_average_systolic: number | null
  current_average_diastolic: number | null
  previous_average_diastolic: number | null
  enough_data: boolean
}

export interface WeeklyRiskSummary {
  current_record_count: number
  previous_record_count: number
  current_average_risk_probability: number | null
  previous_average_risk_probability: number | null
  enough_data: boolean
}

export interface WeeklyAdherenceSummary {
  current_record_days: number
  previous_record_days: number
  record_change: number
  enough_data: boolean
}

export interface WeeklyHighBloodPressureSummary {
  current_record_days: number
  previous_record_days: number
  current_high_bp_days: number
  previous_high_bp_days: number
  total_high_bp_days: number
  enough_data: boolean
}

export interface WeeklyReportSummary {
  current_period: string
  previous_period: string
  bp_summary: WeeklyBloodPressureSummary
  risk_summary: WeeklyRiskSummary
  adherence_summary: WeeklyAdherenceSummary
  high_bp_summary: WeeklyHighBloodPressureSummary
  overall_trend_text: string
}
