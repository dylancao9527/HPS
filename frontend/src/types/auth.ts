import type { Profile } from '@/types/profile'

export type UserRole = 'admin' | 'user'

export interface AuthUser extends Profile {
  id: number | string
  username: string
  email: string
  role: UserRole
}

export interface AuthResponse {
  token: string
  user: AuthUser
}

export interface LoginOptions {
  loginRole?: UserRole
}

export interface EmailCodeResponse {
  mock_service?: string
  message?: string
  expires_in_seconds?: number
  resend_after_seconds?: number
  retry_after_seconds?: number
}

export interface AuthMeResponse {
  user: AuthUser
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterCredentials extends LoginCredentials {
  email: string
  code: string
}

export interface AuthContextValue {
  user: AuthUser | null
  token: string | null
  loading: boolean
  login: (username: string, password: string, options?: LoginOptions) => Promise<AuthResponse>
  register: (username: string, password: string, email: string, code: string) => Promise<AuthResponse>
  logout: () => void
  refreshUser: () => Promise<void>
}
