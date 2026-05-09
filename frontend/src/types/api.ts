export type ApiPrimitive = string | number | boolean | null | undefined

export type ApiHeaderValue = string

export interface ApiRequestOptions extends Omit<RequestInit, 'headers'> {
  headers?: HeadersInit
}

export interface ApiErrorResponse {
  error?: string
}

export interface MockEmailMessage {
  code: string
  email: string
  scene: string
  subject?: string
  text?: string
  html?: string
  created_at?: string
}

export interface MockEmailResponse {
  message: MockEmailMessage
}
