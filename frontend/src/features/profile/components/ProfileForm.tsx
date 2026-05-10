import { useMemo } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useFeedback } from '@/hooks/useFeedback'
import type { Profile } from '@/types/profile'
import AccountProfileSection from '@/features/profile/components/AccountProfileSection'
import HealthProfileSection from '@/features/profile/components/HealthProfileSection'
import PasswordSettingsSection from '@/features/profile/components/PasswordSettingsSection'
import ProfileFeedbackSection from '@/features/profile/components/ProfileFeedbackSection'
import { getProfileFormKey } from '@/features/profile/profileFormState'
import {
  useAccountProfileSection,
  useHealthProfileSection,
  usePasswordSettingsSection,
  useProfileFeedbackSection,
} from '@/features/profile/hooks/useProfileFormSections'

type ProfileFormSection = 'account' | 'riskFactors' | 'feedback' | 'password'

interface ProfileFormProps {
  sections?: ProfileFormSection[]
}

const defaultSections: ProfileFormSection[] = ['account', 'riskFactors', 'feedback', 'password']

export default function ProfileForm({ sections = defaultSections }: ProfileFormProps) {
  const { user } = useAuth()

  return <ProfileFormContent key={getProfileFormKey(user)} profileUser={user} sections={sections} />
}

interface ProfileFormContentProps {
  profileUser: Profile | null
  sections: ProfileFormSection[]
}

function ProfileFormContent({ profileUser, sections }: ProfileFormContentProps) {
  const { refreshUser } = useAuth()
  const { showToast } = useFeedback()
  const visibleSections = useMemo(() => new Set(sections), [sections])
  const accountSection = useAccountProfileSection({
    profileUser,
    refreshUser,
    showToast,
  })
  const healthSection = useHealthProfileSection({
    profileUser,
    refreshUser,
    showToast,
  })
  const feedbackSection = useProfileFeedbackSection({
    profileUser,
    refreshUser,
    showToast,
  })
  const passwordSection = usePasswordSettingsSection({
    profileUser,
    showToast,
  })

  return (
    <div>
      {visibleSections.has('account') && (
        <AccountProfileSection
          accountForm={accountSection.accountForm}
          emailChanged={accountSection.emailChanged}
          savingAccount={accountSection.savingAccount}
          sendingEmailCode={accountSection.sendingEmailCode}
          onUpdateField={accountSection.updateAccountField}
          onSendChangeEmailCode={accountSection.handleSendChangeEmailCode}
          onSaveAccount={accountSection.handleSaveAccount}
        />
      )}
      {visibleSections.has('riskFactors') && (
        <HealthProfileSection
          healthForm={healthSection.healthForm}
          bmi={healthSection.bmi}
          bmiStatus={healthSection.bmiStatus}
          bmiToneClass={healthSection.bmiToneClass}
          smokerEnabled={healthSection.smokerEnabled}
          savingHealth={healthSection.savingHealth}
          onUpdateField={healthSection.updateHealthField}
          onSaveHealth={healthSection.handleSaveHealth}
        />
      )}
      {visibleSections.has('feedback') && (
        <ProfileFeedbackSection
          feedbackForm={feedbackSection.feedbackForm}
          savingFeedback={feedbackSection.savingFeedback}
          onUpdateField={feedbackSection.updateFeedbackField}
          onSaveFeedback={feedbackSection.handleSaveFeedback}
        />
      )}
      {visibleSections.has('password') && (
        <PasswordSettingsSection
          passwordMode={passwordSection.passwordMode}
          passwordForm={passwordSection.passwordForm}
          resetPasswordForm={passwordSection.resetPasswordForm}
          savingPassword={passwordSection.savingPassword}
          sendingResetCode={passwordSection.sendingResetCode}
          onChangeMode={passwordSection.setPasswordMode}
          onUpdatePasswordField={passwordSection.updatePasswordField}
          onUpdateResetPasswordField={passwordSection.updateResetPasswordField}
          onChangePassword={passwordSection.handleChangePassword}
          onSendResetCode={passwordSection.handleSendResetCode}
          onResetPasswordByEmail={passwordSection.handleResetPasswordByEmail}
        />
      )}
    </div>
  )
}
