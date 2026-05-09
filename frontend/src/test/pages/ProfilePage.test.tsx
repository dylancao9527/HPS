import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import ProfilePage from '@/pages/ProfilePage'

vi.mock('@/features/profile', async () => {
  const React = await import('react')
  return {
    ProfileForm: ({ sections }: { sections: string[] }) => (
      React.createElement('div', null, `ProfileForm:${sections.join(',')}`)
    ),
  }
})

vi.mock('@/features/profile/components/PredictionTrendChart', () => ({
  default: () => null,
}))

vi.mock('@/features/profile/components/WeeklyReportPanel', () => ({
  default: () => null,
}))

vi.mock('@/features/weekly-report', () => ({
  getWeeklyReport: vi.fn(),
}))

describe('ProfilePage tab routing', () => {
  it('opens the risk factor profile tab from the query string', () => {
    render(
      <MemoryRouter initialEntries={['/profile?tab=risk-factors']}>
        <ProfilePage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('tab', { name: '风险因素档案' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByText('ProfileForm:riskFactors')).toBeInTheDocument()
  })
})
