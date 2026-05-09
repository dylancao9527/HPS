import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import HealthProfileSection from '@/features/profile/components/HealthProfileSection'

const emptyHealthForm = {
  age: '',
  male: '1',
  height: '',
  weight: '',
  current_smoker: '0',
  cigs_per_day: '0',
  bp_meds: '',
  diabetes: '',
  tot_chol: '',
  glucose: '',
}

function renderSection() {
  render(
    <HealthProfileSection
      healthForm={emptyHealthForm}
      bmi={null}
      bmiStatus={{ label: '-', color: 'var(--text-secondary)' }}
      bmiToneClass="bmi-tag--normal"
      smokerEnabled={false}
      savingHealth={false}
      onUpdateField={vi.fn()}
      onSaveHealth={vi.fn()}
    />,
  )
}

describe('HealthProfileSection', () => {
  it('marks only the minimum risk factor profile fields as required', () => {
    renderSection()

    expect(screen.getByLabelText(/年龄/)).toBeRequired()
    expect(screen.getByLabelText(/性别/)).toBeRequired()
    expect(screen.getByLabelText(/身高/)).toBeRequired()
    expect(screen.getByLabelText(/体重/)).toBeRequired()
    expect(screen.getAllByText('必填')).toHaveLength(4)

    expect(screen.getByLabelText(/当前是否吸烟/)).not.toBeRequired()
    expect(screen.getByLabelText(/日吸烟支数/)).not.toBeRequired()
    expect(screen.getByLabelText(/是否长期按医嘱服用降压药/)).not.toBeRequired()
    expect(screen.getByLabelText(/是否患糖尿病/)).not.toBeRequired()
    expect(screen.getByLabelText(/总胆固醇/)).not.toBeRequired()
    expect(screen.getByLabelText(/血糖/)).not.toBeRequired()
  })
})
