import { request } from '@/config/api'
import { normalizeProfileUser } from '@/features/shared/normalizers'
import type { Profile, RawProfile } from '@/types/profile'

interface ProfileMutationResponse extends RawProfile {
  [key: string]: unknown
}

interface AuthMockServiceResponse {
  mock_service?: string
  [key: string]: unknown
}

type SendChangeEmailCodeResponse = AuthMockServiceResponse
type SendPasswordResetCodeResponse = AuthMockServiceResponse
type UpdateAccountResponse = Record<string, unknown>
type ChangePasswordResponse = Record<string, unknown>
type ResetPasswordByEmailResponse = Record<string, unknown>

export async function getProfile(): Promise<Profile | null | undefined> {
  const data = await request<RawProfile>('/profile')
  return normalizeProfileUser(data)
}

export async function updateProfile(data: Partial<Profile>): Promise<Profile | null | undefined> {
  const response = await request<ProfileMutationResponse>('/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  })

  return normalizeProfileUser(response)
}

export async function sendChangeEmailCode(email: string): Promise<SendChangeEmailCodeResponse> {
  return request<SendChangeEmailCodeResponse>('/auth/send-change-email-code', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

export async function updateAccount(username: string, email: string, emailCode: string): Promise<UpdateAccountResponse> {
  return request<UpdateAccountResponse>('/auth/update-account', {
    method: 'POST',
    body: JSON.stringify({
      username,
      email,
      email_code: emailCode,
    }),
  })
}

export async function changePassword(oldPassword: string, newPassword: string): Promise<ChangePasswordResponse> {
  return request<ChangePasswordResponse>('/auth/change-password', {
    method: 'POST',
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword,
    }),
  })
}

export async function sendPasswordResetCode(email: string): Promise<SendPasswordResetCodeResponse> {
  return request<SendPasswordResetCodeResponse>('/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

export async function resetPasswordByEmail(email: string, code: string, newPassword: string): Promise<ResetPasswordByEmailResponse> {
  return request<ResetPasswordByEmailResponse>('/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({
      email,
      code,
      new_password: newPassword,
    }),
  })
}
