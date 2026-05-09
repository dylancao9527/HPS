export type HealthTaskAlertLevel = 'none' | 'warning' | 'danger'
export type HealthTaskStreakStatus = 'active' | 'pending_today' | 'reset'
export type HealthTaskSuggestedAction = 'record_now' | 'keep_tracking' | 'monitor_alert'

export interface HealthTaskLatestRecord {
  recorded_at: string
  systolic_bp: number
  diastolic_bp: number
  heart_rate: number | null
}

export interface HealthTaskSummary {
  has_record_today: boolean
  today_status_text: string
  current_streak_days: number
  streak_status: HealthTaskStreakStatus
  alert_level: HealthTaskAlertLevel
  alert_message: string
  alert_basis_days: number
  latest_record: HealthTaskLatestRecord | null
  suggested_action: HealthTaskSuggestedAction
}
