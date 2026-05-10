import { afterEach, describe, expect, it, vi } from 'vitest'
import { shouldExposeLocalMockEmailCode } from '@/config/api'

describe('local mock email code UI policy', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
  })

  it('hides mock email codes by default outside dev mode', () => {
    vi.stubEnv('DEV', false)
    vi.stubEnv('VITE_ENABLE_LOCAL_MOCK_EMAIL_UI', '')

    expect(shouldExposeLocalMockEmailCode()).toBe(false)
  })

  it('allows mock email codes when the UI flag is explicitly enabled', () => {
    vi.stubEnv('DEV', false)
    vi.stubEnv('VITE_ENABLE_LOCAL_MOCK_EMAIL_UI', 'true')

    expect(shouldExposeLocalMockEmailCode()).toBe(true)
  })
})
