import type { Profile } from '@/types/profile'

export interface AccountFormState {
  username: string
  email: string
  emailCode: string
  emailDebugCode: string
  nickname: string
  avatar: string
}

export interface ModelProfileFormState {
  age: string
  male: string
  height: string
  weight: string
  current_smoker: string
  cigs_per_day: string
  bp_meds: string
  diabetes: string
  tot_chol: string
  glucose: string
}

export interface ProfileFeedbackFormState {
  diagnosis: string
}

export type HealthFormState = ModelProfileFormState

export interface PasswordFormState {
  oldPassword: string
  newPassword: string
  confirmPassword: string
}

export interface ResetPasswordFormState {
  email: string
  code: string
  newPassword: string
  confirmPassword: string
  debugCode: string
}

export interface BmiStatus {
  label: string
  color: string
}

export type AccountField = keyof AccountFormState
export type HealthField = keyof HealthFormState
export type ProfileFeedbackField = keyof ProfileFeedbackFormState
export type PasswordField = keyof PasswordFormState
export type ResetPasswordField = keyof ResetPasswordFormState

export function getBmiStatus(bmi: number | null): BmiStatus {
  if (!bmi) return { label: '-', color: 'var(--text-secondary)' }
  if (bmi < 18.5) return { label: '偏瘦', color: 'var(--accent)' }
  if (bmi < 24) return { label: '正常', color: 'var(--success)' }
  if (bmi < 28) return { label: '超重', color: 'var(--warning)' }
  return { label: '肥胖', color: 'var(--danger)' }
}

export function stringifyNullable(value: unknown, fallback = ''): string {
  return value == null ? fallback : String(value)
}

export function parseNullableFloat(value: string | null | undefined): number | null {
  return value === '' || value == null ? null : Number(value)
}

export function parseNullableInt(value: string | null | undefined): number | null {
  return value === '' || value == null ? null : Number.parseInt(value, 10)
}

export function getProfileFormKey(profileUser: Profile | null): string {
  if (!profileUser) return 'empty-profile'
  return [
    profileUser.id ?? 'unknown',
    profileUser.username ?? '',
    profileUser.email ?? '',
    profileUser.nickname ?? '',
    profileUser.avatar ?? '',
    profileUser.age ?? '',
    profileUser.height ?? '',
    profileUser.weight ?? '',
    profileUser.current_smoker ?? '',
    profileUser.cigs_per_day ?? '',
    profileUser.bp_meds ?? '',
    profileUser.diabetes ?? '',
    profileUser.tot_chol ?? '',
    profileUser.glucose ?? '',
    profileUser.diagnosis ?? '',
  ].join('|')
}

export function getAccountFormState(profileUser: Profile | null): AccountFormState {
  return {
    username: profileUser?.username || '',
    email: profileUser?.email || '',
    emailCode: '',
    emailDebugCode: '',
    nickname: profileUser?.nickname || '',
    avatar: profileUser?.avatar || '',
  }
}

export function getHealthFormState(profileUser: Profile | null): HealthFormState {
  return {
    age: stringifyNullable(profileUser?.age),
    male: stringifyNullable(profileUser?.male, '1'),
    height: stringifyNullable(profileUser?.height),
    weight: stringifyNullable(profileUser?.weight),
    current_smoker: stringifyNullable(profileUser?.current_smoker, '0'),
    cigs_per_day: stringifyNullable(
      profileUser?.current_smoker === 0 ? 0 : profileUser?.cigs_per_day,
      profileUser?.current_smoker === 0 ? '0' : '',
    ),
    bp_meds: stringifyNullable(profileUser?.bp_meds),
    diabetes: stringifyNullable(profileUser?.diabetes),
    tot_chol: stringifyNullable(profileUser?.tot_chol),
    glucose: stringifyNullable(profileUser?.glucose),
  }
}

export function getProfileFeedbackFormState(profileUser: Profile | null): ProfileFeedbackFormState {
  return {
    diagnosis: profileUser?.diagnosis || '',
  }
}

export function getResetPasswordFormState(profileUser: Profile | null): ResetPasswordFormState {
  return {
    email: profileUser?.email || '',
    code: '',
    newPassword: '',
    confirmPassword: '',
    debugCode: '',
  }
}

export function getBmiValue(healthForm: HealthFormState): string | null {
  const height = Number(healthForm.height)
  const weight = Number(healthForm.weight)
  if (!height || !weight || height <= 0) return null
  return (weight / ((height / 100) ** 2)).toFixed(1)
}

export function isSmokerEnabled(healthForm: HealthFormState): boolean {
  return healthForm.current_smoker === '1'
}

export function updateHealthFormField(
  prev: HealthFormState,
  field: HealthField,
  value: string,
): HealthFormState {
  const next: HealthFormState = { ...prev, [field]: value }
  if (field === 'current_smoker' && value !== '1') {
    next.cigs_per_day = '0'
  }
  return next
}

export function buildModelProfilePayload(healthForm: HealthFormState): Partial<Profile> {
  const smokerEnabled = isSmokerEnabled(healthForm)
  return {
    age: parseNullableFloat(healthForm.age),
    male: parseNullableInt(healthForm.male),
    height: parseNullableFloat(healthForm.height),
    weight: parseNullableFloat(healthForm.weight),
    current_smoker: parseNullableInt(healthForm.current_smoker),
    cigs_per_day: smokerEnabled ? parseNullableFloat(healthForm.cigs_per_day) : 0,
    bp_meds: parseNullableInt(healthForm.bp_meds),
    diabetes: parseNullableInt(healthForm.diabetes),
    tot_chol: parseNullableFloat(healthForm.tot_chol),
    glucose: parseNullableFloat(healthForm.glucose),
  }
}

export function buildProfileFeedbackPayload(feedbackForm: ProfileFeedbackFormState): Partial<Profile> {
  return {
    diagnosis: feedbackForm.diagnosis || null,
  }
}

export function buildHealthProfilePayload(healthForm: HealthFormState): Partial<Profile> {
  return buildModelProfilePayload(healthForm)
}
