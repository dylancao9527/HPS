import { describe, expect, it } from 'vitest'
import {
  buildModelProfilePayload,
  buildProfileFeedbackPayload,
  getBmiStatus,
  getBmiValue,
  getHealthFormState,
  getProfileFeedbackFormState,
  getProfileFormKey,
  updateHealthFormField,
} from '@/features/profile/profileFormState'

describe('profileFormState', () => {
  it('builds health form state from canonical profile fields', () => {
    const state = getHealthFormState({
      id: 42,
      current_smoker: 0,
      cigs_per_day: 8,
      age: 56,
      male: 1,
      height: 170,
      weight: 70,
      diagnosis: null,
    })

    expect(state.current_smoker).toBe('0')
    expect(state.cigs_per_day).toBe('0')
    expect(state.age).toBe('56')
    expect(state.male).toBe('1')
    expect(getProfileFeedbackFormState({ diagnosis: null }).diagnosis).toBe('')
  })

  it('keeps smoking-dependent cigs state and model payload explicit', () => {
    const smokingState = updateHealthFormField(getHealthFormState(null), 'current_smoker', '1')
    const nonSmokingState = updateHealthFormField(
      { ...smokingState, cigs_per_day: '12' },
      'current_smoker',
      '0',
    )

    expect(smokingState.current_smoker).toBe('1')
    expect(nonSmokingState.cigs_per_day).toBe('0')
    expect(
      buildModelProfilePayload({
        ...nonSmokingState,
        age: '56',
        male: '1',
        height: '170',
        weight: '70',
        bp_meds: '',
        diabetes: '0',
        tot_chol: '',
        glucose: '96',
      }),
    ).toEqual({
      age: 56,
      male: 1,
      height: 170,
      weight: 70,
      current_smoker: 0,
      cigs_per_day: 0,
      bp_meds: null,
      diabetes: 0,
      tot_chol: null,
      glucose: 96,
    })
  })

  it('keeps diagnosis feedback out of the model profile payload', () => {
    expect(buildProfileFeedbackPayload({ diagnosis: 'Yes' })).toEqual({ diagnosis: 'Yes' })
    expect(buildProfileFeedbackPayload({ diagnosis: '' })).toEqual({ diagnosis: null })
    expect(buildModelProfilePayload(getHealthFormState({ diagnosis: 'Yes' }))).not.toHaveProperty('diagnosis')
  })

  it('derives bmi presentation and stable reset key', () => {
    const healthState = {
      ...getHealthFormState(null),
      height: '170',
      weight: '70',
    }

    expect(getBmiValue(healthState)).toBe('24.2')
    expect(getBmiStatus(24.2).label).toBe('超重')
    expect(
      getProfileFormKey({
        id: 42,
        username: 'alice',
        email: 'alice@example.com',
        current_smoker: 0,
      }),
    ).toContain('alice@example.com')
  })
})
