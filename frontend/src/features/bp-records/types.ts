export interface BPRecord {
  id: number
  systolic_bp: number
  diastolic_bp: number
  heart_rate: number | null
  recorded_at: string
}

export interface BPRecordsResponse {
  records: BPRecord[]
  pages: number
  total: number
}

export interface CreateBPRecordInput {
  systolic_bp: number
  diastolic_bp: number
  heart_rate: number | null
  recorded_at: string
}

export interface BPRecordFormState {
  systolic_bp: string
  diastolic_bp: string
  heart_rate: string
  recorded_at: string
}
