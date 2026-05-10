import type { ApiErrorResponse, ApiRequestOptions, MockEmailMessage, MockEmailResponse } from '@/types/api'

/**
 * API 基础配置
 *
 * 开发模式：Vite proxy 把 /api 转发到 http://localhost:5000
 * 生产模式：前后端同域，直接请求 /api
 * 因此 API_BASE 统一使用相对路径 '/api'
 */
const API_BASE: string = import.meta.env.VITE_API_BASE || '/api'

function shouldExposeLocalMockEmailCode(): boolean {
  return (
    String(import.meta.env.DEV) === 'true'
    || import.meta.env.VITE_ENABLE_LOCAL_MOCK_EMAIL_UI === 'true'
  )
}

function parseResponseBody<T>(bodyText: string, contentType: string | null): T | string | Record<string, never> {
  if (!bodyText) return {}

  const shouldParseJson = contentType?.includes('application/json') || contentType?.includes('+json')
  if (shouldParseJson) {
    return JSON.parse(bodyText) as T
  }

  return bodyText
}

/**
 * 通用请求函数 — 自动附加 JWT token
 */
async function request<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const token = localStorage.getItem('token')
  const headers = new Headers({ 'Content-Type': 'application/json', ...options.headers })
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  const bodyText = await res.text()
  const parsed = parseResponseBody<T & ApiErrorResponse>(bodyText, res.headers.get('content-type'))

  if (!res.ok) {
    const errorMessage =
      typeof parsed === 'object' && parsed !== null && 'error' in parsed
        ? parsed.error || res.statusText || 'Request failed'
        : typeof parsed === 'string' && parsed
          ? parsed
          : res.statusText || 'Request failed'
    throw new Error(errorMessage)
  }

  return parsed as T
}

async function getLatestMockEmail(email: string, scene: string): Promise<MockEmailMessage> {
  const query = new URLSearchParams({ email, scene })
  const data = await request<MockEmailResponse>(`/dev/mock-emails/latest?${query.toString()}`, {
    method: 'GET',
    headers: {},
  })
  return data.message
}

export {
  API_BASE,
  getLatestMockEmail,
  parseResponseBody,
  request,
  shouldExposeLocalMockEmailCode,
}
