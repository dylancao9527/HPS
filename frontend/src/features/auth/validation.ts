export interface PasswordStrength {
  score: 0 | 1 | 2 | 3
  label: string
  color: string
}

export function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const PASSWORD_MIN_LENGTH = 8
const PASSWORD_MAX_LENGTH = 32

export function countPasswordTypes(password: string): number {
  let types = 0
  if (/[a-zA-Z]/.test(password)) types += 1
  if (/[0-9]/.test(password)) types += 1
  if (/[^a-zA-Z0-9]/.test(password)) types += 1
  return types
}

export function getPasswordStrength(password: string): PasswordStrength {
  if (!password) return { score: 0, label: '', color: 'var(--border)' }

  const types = countPasswordTypes(password)
  const lenOk = password.length >= PASSWORD_MIN_LENGTH && password.length <= PASSWORD_MAX_LENGTH
  if (!lenOk || types < 2) return { score: 1, label: '弱', color: 'var(--danger)' }
  if (types === 2 && password.length < 12) return { score: 2, label: '中', color: 'var(--warning)' }
  if (types >= 3 || password.length >= 12) return { score: 3, label: '强', color: 'var(--success)' }
  return { score: 2, label: '中', color: 'var(--warning)' }
}

export function getPasswordErrors(password: string): string[] {
  const errors: string[] = []
  if (password.length < PASSWORD_MIN_LENGTH) errors.push('至少 8 位')
  if (password.length > PASSWORD_MAX_LENGTH) errors.push('不超过 32 位')
  if (countPasswordTypes(password) < 2) errors.push('需包含字母、数字、符号中至少两种')
  return errors
}

export function getPasswordValidationError(password: string): string {
  if (!password) return '密码不能为空'
  if (password.length < PASSWORD_MIN_LENGTH || password.length > PASSWORD_MAX_LENGTH) {
    return '密码长度需在 8~32 位之间'
  }
  if (countPasswordTypes(password) < 2) {
    return '密码需至少包含字母、数字、符号中的两种'
  }
  return ''
}

export function getPasswordError(password: string): string {
  return getPasswordValidationError(password)
}

export function getEmailValidationError(email: string): string {
  if (!email.trim()) return '请输入邮箱'
  if (!EMAIL_PATTERN.test(email.trim())) return '邮箱格式不正确'
  return ''
}

export function validateEmail(email: string): boolean {
  return getEmailValidationError(email) === ''
}
