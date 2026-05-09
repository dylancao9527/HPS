import type { PredictionSnapshot, RawPredictionSnapshot } from '@/types/prediction'
import type { Profile, RawProfile } from '@/types/profile'

function getCanonicalValue<TSource extends Record<string, unknown>, TValue = unknown>(source: TSource, ...keys: string[]): TValue | undefined {
  for (const key of keys) {
    const value = source[key]
    if (value !== undefined && value !== null) {
      return value as TValue
    }
  }
  return undefined
}

export function normalizePredictionInputData(inputData?: RawPredictionSnapshot | null): PredictionSnapshot | null | undefined {
  if (!inputData || typeof inputData !== 'object') return inputData

  return {
    ...inputData,
    bp_meds: getCanonicalValue<RawPredictionSnapshot, PredictionSnapshot['bp_meds']>(inputData, 'bp_meds', 'BPMeds'),
    bmi: getCanonicalValue<RawPredictionSnapshot, PredictionSnapshot['bmi']>(inputData, 'bmi', 'BMI'),
    systolic_bp: getCanonicalValue<RawPredictionSnapshot, PredictionSnapshot['systolic_bp']>(inputData, 'systolic_bp', 'sysBP'),
    diastolic_bp: getCanonicalValue<RawPredictionSnapshot, PredictionSnapshot['diastolic_bp']>(inputData, 'diastolic_bp', 'diaBP'),
    current_smoker: getCanonicalValue<RawPredictionSnapshot, PredictionSnapshot['current_smoker']>(inputData, 'current_smoker', 'currentSmoker', 'smoking'),
    tot_chol: getCanonicalValue<RawPredictionSnapshot, PredictionSnapshot['tot_chol']>(inputData, 'tot_chol', 'totChol', 'cholesterol'),
    cigs_per_day: getCanonicalValue<RawPredictionSnapshot, PredictionSnapshot['cigs_per_day']>(inputData, 'cigs_per_day', 'cigsPerDay'),
  }
}

export function normalizeProfileUser(user?: RawProfile | null): Profile | null | undefined {
  if (!user || typeof user !== 'object') return user

  return {
    ...user,
    bmi: getCanonicalValue<RawProfile, Profile['bmi']>(user, 'bmi', 'BMI'),
    current_smoker: getCanonicalValue<RawProfile, Profile['current_smoker']>(user, 'current_smoker', 'currentSmoker', 'smoking'),
    cigs_per_day: getCanonicalValue<RawProfile, Profile['cigs_per_day']>(user, 'cigs_per_day', 'cigsPerDay'),
    bp_meds: getCanonicalValue<RawProfile, Profile['bp_meds']>(user, 'bp_meds', 'BPMeds'),
    tot_chol: getCanonicalValue<RawProfile, Profile['tot_chol']>(user, 'tot_chol', 'totChol', 'cholesterol'),
  }
}
