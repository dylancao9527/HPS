import { useMemo, useState } from 'react'
import { getLatestMockEmail, shouldExposeLocalMockEmailCode } from '@/config/api'
import type { ToastType } from '@/hooks/useFeedback'
import type { Profile } from '@/types/profile'
import {
  getEmailValidationError,
  getPasswordValidationError,
} from '@/features/auth/validation'
import {
  buildModelProfilePayload,
  buildProfileFeedbackPayload,
  getAccountFormState,
  getBmiStatus,
  getBmiValue,
  getHealthFormState,
  getProfileFeedbackFormState,
  getResetPasswordFormState,
  isSmokerEnabled,
  updateHealthFormField,
} from '@/features/profile/profileFormState'
import type {
  AccountField,
  AccountFormState,
  HealthField,
  HealthFormState,
  PasswordField,
  PasswordFormState,
  ProfileFeedbackField,
  ProfileFeedbackFormState,
  ResetPasswordField,
  ResetPasswordFormState,
} from '@/features/profile/profileFormState'
import {
  changePassword,
  resetPasswordByEmail,
  sendChangeEmailCode,
  sendPasswordResetCode,
  updateAccount,
  updateProfile,
} from '@/features/profile/api/profileApi'

type ShowToast = (message: string, type?: ToastType, duration?: number) => void

interface ProfileSectionHookOptions {
  profileUser: Profile | null
  refreshUser: () => Promise<void>
  showToast: ShowToast
}

function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback
}

export function useAccountProfileSection({
  profileUser,
  refreshUser,
  showToast,
}: ProfileSectionHookOptions) {
  const [accountForm, setAccountForm] = useState<AccountFormState>(() =>
    getAccountFormState(profileUser),
  )
  const [savingAccount, setSavingAccount] = useState(false)
  const [sendingEmailCode, setSendingEmailCode] = useState(false)
  const emailChanged = accountForm.email.trim() !== (profileUser?.email || '')

  const updateAccountField = (field: AccountField, value: string) => {
    setAccountForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSendChangeEmailCode = async () => {
    const emailError = getEmailValidationError(accountForm.email)
    if (emailError) {
      showToast(emailError, 'error')
      return
    }
    if (!emailChanged) {
      showToast('请输入新的邮箱地址', 'error')
      return
    }

    setSendingEmailCode(true)
    try {
      const data = await sendChangeEmailCode(accountForm.email.trim())
      const mockEmail = data.mock_service === 'local_email' && shouldExposeLocalMockEmailCode()
        ? await getLatestMockEmail(accountForm.email.trim(), 'change_email')
        : null
      setAccountForm((prev) => ({
        ...prev,
        emailCode: '',
        emailDebugCode: mockEmail?.code || '',
      }))
      showToast('邮箱验证码已发送', 'success')
    } catch (err) {
      showToast(getErrorMessage(err, '验证码发送失败'), 'error')
    } finally {
      setSendingEmailCode(false)
    }
  }

  const handleSaveAccount = async () => {
    const username = accountForm.username.trim()
    const email = accountForm.email.trim()

    if (!username) {
      showToast('用户名不能为空', 'error')
      return
    }

    const emailError = getEmailValidationError(email)
    if (emailError) {
      showToast(emailError, 'error')
      return
    }

    if (emailChanged && !accountForm.emailCode.trim()) {
      showToast('修改邮箱需要填写新邮箱验证码', 'error')
      return
    }

    setSavingAccount(true)
    try {
      await updateAccount(username, email, accountForm.emailCode.trim())
      await updateProfile({
        nickname: accountForm.nickname || null,
        avatar: accountForm.avatar || null,
      })
      await refreshUser()
      setAccountForm((prev) => ({ ...prev, emailCode: '', emailDebugCode: '' }))
      showToast('账号与展示信息已保存', 'success')
    } catch (err) {
      showToast(getErrorMessage(err, '保存失败'), 'error')
    } finally {
      setSavingAccount(false)
    }
  }

  return {
    accountForm,
    emailChanged,
    handleSaveAccount,
    handleSendChangeEmailCode,
    savingAccount,
    sendingEmailCode,
    updateAccountField,
  }
}

export function useHealthProfileSection({
  profileUser,
  refreshUser,
  showToast,
}: ProfileSectionHookOptions) {
  const [healthForm, setHealthForm] = useState<HealthFormState>(() =>
    getHealthFormState(profileUser),
  )
  const [savingHealth, setSavingHealth] = useState(false)
  const bmi = useMemo(() => getBmiValue(healthForm), [healthForm])
  const bmiStatus = getBmiStatus(bmi ? Number(bmi) : null)
  const smokerEnabled = isSmokerEnabled(healthForm)
  const bmiToneClass = bmi
    ? `bmi-tag bmi-tag--${bmiStatus.label === '偏瘦' ? 'lean' : bmiStatus.label === '正常' ? 'normal' : bmiStatus.label === '超重' ? 'warning' : 'danger'}`
    : 'bmi-tag'

  const updateHealthField = (field: HealthField, value: string) => {
    setHealthForm((prev) => updateHealthFormField(prev, field, value))
  }

  const handleSaveHealth = async () => {
    setSavingHealth(true)
    try {
      await updateProfile({
        ...buildModelProfilePayload(healthForm),
      })
      await refreshUser()
      showToast('风险因素档案已保存', 'success')
    } catch (err) {
      showToast(getErrorMessage(err, '保存失败'), 'error')
    } finally {
      setSavingHealth(false)
    }
  }

  return {
    bmi,
    bmiStatus,
    bmiToneClass,
    handleSaveHealth,
    healthForm,
    savingHealth,
    smokerEnabled,
    updateHealthField,
  }
}

export function useProfileFeedbackSection({
  profileUser,
  refreshUser,
  showToast,
}: ProfileSectionHookOptions) {
  const [feedbackForm, setFeedbackForm] = useState<ProfileFeedbackFormState>(() =>
    getProfileFeedbackFormState(profileUser),
  )
  const [savingFeedback, setSavingFeedback] = useState(false)

  const updateFeedbackField = (field: ProfileFeedbackField, value: string) => {
    setFeedbackForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSaveFeedback = async () => {
    setSavingFeedback(true)
    try {
      await updateProfile({
        ...buildProfileFeedbackPayload(feedbackForm),
      })
      await refreshUser()
      showToast('反馈信息已保存', 'success')
    } catch (err) {
      showToast(getErrorMessage(err, '保存失败'), 'error')
    } finally {
      setSavingFeedback(false)
    }
  }

  return {
    feedbackForm,
    handleSaveFeedback,
    savingFeedback,
    updateFeedbackField,
  }
}

export function usePasswordSettingsSection({
  profileUser,
  showToast,
}: Pick<ProfileSectionHookOptions, 'profileUser' | 'showToast'>) {
  const [passwordMode, setPasswordMode] = useState<'old_password' | 'email_code'>('old_password')
  const [passwordForm, setPasswordForm] = useState<PasswordFormState>({
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
  })
  const [resetPasswordForm, setResetPasswordForm] = useState<ResetPasswordFormState>(() =>
    getResetPasswordFormState(profileUser),
  )
  const [savingPassword, setSavingPassword] = useState(false)
  const [sendingResetCode, setSendingResetCode] = useState(false)

  const updatePasswordField = (field: PasswordField, value: string) => {
    setPasswordForm((prev) => ({ ...prev, [field]: value }))
  }

  const updateResetPasswordField = (field: ResetPasswordField, value: string) => {
    setResetPasswordForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleChangePassword = async () => {
    const { oldPassword, newPassword, confirmPassword } = passwordForm
    if (!oldPassword || !newPassword || !confirmPassword) {
      showToast('请填写完整密码信息', 'error')
      return
    }

    const validationError = getPasswordValidationError(newPassword)
    if (validationError) {
      showToast(validationError, 'error')
      return
    }

    if (newPassword !== confirmPassword) {
      showToast('两次输入的新密码不一致', 'error')
      return
    }

    setSavingPassword(true)
    try {
      await changePassword(oldPassword, newPassword)
      setPasswordForm({ oldPassword: '', newPassword: '', confirmPassword: '' })
      showToast('密码修改成功', 'success')
    } catch (err) {
      showToast(getErrorMessage(err, '密码修改失败'), 'error')
    } finally {
      setSavingPassword(false)
    }
  }

  const handleSendResetCode = async () => {
    const email = resetPasswordForm.email.trim()
    const emailError = getEmailValidationError(email)
    if (emailError) {
      showToast(emailError, 'error')
      return
    }

    setSendingResetCode(true)
    try {
      const data = await sendPasswordResetCode(email)
      const mockEmail = data.mock_service === 'local_email' && shouldExposeLocalMockEmailCode()
        ? await getLatestMockEmail(email, 'reset_password')
        : null
      setResetPasswordForm((prev) => ({ ...prev, code: '', debugCode: mockEmail?.code || '' }))
      showToast('密码验证码已发送', 'success')
      if (mockEmail?.code) {
        showToast(`本地模拟邮箱验证码：${mockEmail.code}`, 'info', 4500)
      }
    } catch (err) {
      showToast(getErrorMessage(err, '验证码发送失败'), 'error')
    } finally {
      setSendingResetCode(false)
    }
  }

  const handleResetPasswordByEmail = async () => {
    const { email, code, newPassword, confirmPassword } = resetPasswordForm
    const emailError = getEmailValidationError(email)
    if (emailError) {
      showToast(emailError, 'error')
      return
    }
    if (!code.trim()) {
      showToast('请输入验证码', 'error')
      return
    }

    const validationError = getPasswordValidationError(newPassword)
    if (validationError) {
      showToast(validationError, 'error')
      return
    }
    if (newPassword !== confirmPassword) {
      showToast('两次输入的新密码不一致', 'error')
      return
    }

    setSavingPassword(true)
    try {
      await resetPasswordByEmail(email.trim(), code.trim(), newPassword)
      setResetPasswordForm((prev) => ({
        ...prev,
        code: '',
        newPassword: '',
        confirmPassword: '',
        debugCode: '',
      }))
      showToast('密码已通过邮箱验证码重置', 'success')
    } catch (err) {
      showToast(getErrorMessage(err, '密码重置失败'), 'error')
    } finally {
      setSavingPassword(false)
    }
  }

  return {
    handleChangePassword,
    handleResetPasswordByEmail,
    handleSendResetCode,
    passwordForm,
    passwordMode,
    resetPasswordForm,
    savingPassword,
    sendingResetCode,
    setPasswordMode,
    updatePasswordField,
    updateResetPasswordField,
  }
}
