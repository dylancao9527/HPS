import { describe, expect, it } from 'vitest'
import profileFormSource from '@/features/profile/components/ProfileForm.tsx?raw'

describe('ProfileForm structure', () => {
  it('keeps section state and actions outside the shell component', () => {
    expect(profileFormSource).toContain('useAccountProfileSection')
    expect(profileFormSource).toContain('useHealthProfileSection')
    expect(profileFormSource).toContain('useProfileFeedbackSection')
    expect(profileFormSource).toContain('usePasswordSettingsSection')
    expect(profileFormSource).not.toContain('const [accountForm, setAccountForm]')
    expect(profileFormSource).not.toContain('const [passwordForm, setPasswordForm]')
  })
})
