import { describe, expect, it } from 'vitest'
import {
  countPasswordTypes,
  getEmailValidationError,
  getPasswordErrors,
  getPasswordValidationError,
  validateEmail,
} from '@/features/auth/validation'

describe('auth validation contract', () => {
  it('counts password classes the same way as the backend', () => {
    expect(countPasswordTypes('abcdefgh')).toBe(1)
    expect(countPasswordTypes('Password')).toBe(1)
    expect(countPasswordTypes('Password1')).toBe(2)
    expect(countPasswordTypes('Password1!')).toBe(3)
  })

  it('returns backend-aligned password validation messages', () => {
    expect(getPasswordValidationError('')).toBe('密码不能为空')
    expect(getPasswordValidationError('short1!')).toBe('密码长度需在 8~32 位之间')
    expect(getPasswordValidationError('abcdefgh')).toBe('密码需至少包含字母、数字、符号中的两种')
    expect(getPasswordValidationError('Password1')).toBe('')
    expect(getPasswordErrors('abcdefgh')).toContain('需包含字母、数字、符号中至少两种')
  })

  it('returns backend-aligned email validation messages', () => {
    expect(getEmailValidationError('')).toBe('请输入邮箱')
    expect(getEmailValidationError('bad-email')).toBe('邮箱格式不正确')
    expect(getEmailValidationError('user@example.com')).toBe('')
    expect(validateEmail('user@example.com')).toBe(true)
  })
})
