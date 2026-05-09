import type { WeeklyReportSummary } from '@/features/weekly-report/types'

export interface RawProfile {
  id?: number | string
  username?: string
  email?: string
  role?: string
  nickname?: string | null
  avatar?: string | null
  diagnosis?: string | null
  age?: number | string | null
  male?: number | string | null
  height?: number | string | null
  weight?: number | string | null
  diabetes?: number | string | null
  glucose?: number | string | null
  BMI?: number | string | null
  bmi?: number | string | null
  currentSmoker?: number | string | null
  current_smoker?: number | string | null
  smoking?: number | string | null
  cigsPerDay?: number | string | null
  cigs_per_day?: number | string | null
  BPMeds?: number | string | null
  bp_meds?: number | string | null
  totChol?: number | string | null
  tot_chol?: number | string | null
  cholesterol?: number | string | null
  [key: string]: unknown
}

export interface Profile extends RawProfile {
  nickname?: string | null
  avatar?: string | null
  diagnosis?: string | null
  age?: number | string | null
  male?: number | string | null
  height?: number | string | null
  weight?: number | string | null
  diabetes?: number | string | null
  glucose?: number | string | null
  bmi?: number | string | null
  current_smoker?: number | string | null
  cigs_per_day?: number | string | null
  bp_meds?: number | string | null
  tot_chol?: number | string | null
}

export interface RawProfilePredictionTrendRecord {
  id?: number | string | null
  created_at?: string | null
  risk_probability?: number | null
  risk_level?: string | null
  [key: string]: unknown
}

export interface ProfilePredictionTrendResponse {
  records: RawProfilePredictionTrendRecord[]
}

export type TrendGranularity = 'hour' | 'day' | 'month'

export interface AggregatedTrendPoint {
  bucket: string
  label: string
  risk: number
  samples: number
}

export type ProfileWeeklyReportSummary = WeeklyReportSummary
