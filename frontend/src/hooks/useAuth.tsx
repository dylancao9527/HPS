/* eslint-disable react-refresh/only-export-components */
import { useState, useEffect, useCallback, createContext, useContext } from 'react'
import type { ReactNode } from 'react'
import { request } from '@/config/api'
import { normalizeProfileUser } from '@/features/shared/normalizers'
import type {
  AuthContextValue,
  AuthMeResponse,
  AuthResponse,
  AuthUser,
  LoginOptions,
} from '@/types/auth'

interface AuthProviderProps {
  children: ReactNode
}

const AuthContext = createContext<AuthContextValue | null>(null)

function normalizeAuthResponseUser<T extends { user: AuthUser }>(payload: T): T {
  return {
    ...payload,
    user: normalizeProfileUser(payload.user) as AuthUser,
  }
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true

    const bootstrapUser = async () => {
      if (!token) {
        if (active) setLoading(false)
        return
      }

      try {
        const data = normalizeAuthResponseUser(await request<AuthMeResponse>('/auth/me'))
        if (active) setUser(data.user)
      } catch {
        localStorage.removeItem('token')
        if (active) setToken(null)
      } finally {
        if (active) setLoading(false)
      }
    }

    void bootstrapUser()

    return () => {
      active = false
    }
  }, [token])

  const login = useCallback(async (
    username: string,
    password: string,
    options: LoginOptions = {},
  ): Promise<AuthResponse> => {
    const loginRole = options.loginRole ?? 'user'
    const path = loginRole === 'admin' ? '/auth/login/admin' : '/auth/login/user'
    const data = normalizeAuthResponseUser(await request<AuthResponse>(path, {
      method: 'POST',
      body: JSON.stringify({
        username,
        password,
      }),
    }))
    localStorage.setItem('token', data.token)
    setToken(data.token)
    setUser(data.user)
    return data
  }, [])

  const register = useCallback(async (
    username: string,
    password: string,
    email: string,
    code: string,
  ): Promise<AuthResponse> => {
    const data = normalizeAuthResponseUser(await request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password, email, code }),
    }))
    localStorage.setItem('token', data.token)
    setToken(data.token)
    setUser(data.user)
    return data
  }, [])

  const logout = useCallback((): void => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }, [])

  const refreshUser = useCallback(async (): Promise<void> => {
    try {
      const data = normalizeAuthResponseUser(await request<AuthMeResponse>('/auth/me'))
      setUser(data.user)
    } catch {
      // ignore
    }
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
