import { render, screen, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import UserTable from '@/features/admin/components/UserTable'

vi.mock('@/hooks/useFeedback', () => ({
  useFeedback: () => ({
    confirm: vi.fn(),
    showToast: vi.fn(),
  }),
}))

describe('UserTable', () => {
  it('keeps admin rows account-only while user rows can show health profile fields', () => {
    render(
      <UserTable
        users={[
          {
            id: 1,
            username: 'alice',
            email: 'alice@example.com',
            role: 'user',
            age: 56,
            bmi: 24.2,
            created_at: '2026-05-07T09:30:00',
          },
        ]}
        admins={[
          {
            id: 'admin:1',
            username: 'root',
            email: 'root@example.com',
            role: 'admin',
            created_at: '2026-05-07T09:30:00',
          },
        ]}
        onDelete={vi.fn()}
        onEdit={vi.fn()}
        onBatchDelete={vi.fn()}
      />,
    )

    const userCard = screen.getByText('普通用户账号').closest('.card')
    const adminCard = screen.getByText('管理员账号').closest('.card')
    expect(userCard).not.toBeNull()
    expect(adminCard).not.toBeNull()

    expect(within(userCard as HTMLElement).getByText('年龄')).toBeInTheDocument()
    expect(within(userCard as HTMLElement).getByText('BMI')).toBeInTheDocument()
    expect(within(userCard as HTMLElement).getByText('56')).toBeInTheDocument()
    expect(within(adminCard as HTMLElement).queryByText('年龄')).not.toBeInTheDocument()
    expect(within(adminCard as HTMLElement).queryByText('BMI')).not.toBeInTheDocument()
    expect(within(adminCard as HTMLElement).getByText('管理员')).toBeInTheDocument()
  })
})
