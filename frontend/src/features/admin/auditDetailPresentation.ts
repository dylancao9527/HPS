import type { PredictionAuditDetail } from '@/types/admin'
import type { PredictionSnapshot } from '@/types/prediction'
import {
  getConfidenceReasonDetails,
  getFusionReasonDetails,
  getMedicationPolicyText,
} from '@/features/prediction/confidenceExplanation'
import { formatNumber, toBinary, toNumber } from '@/features/prediction/explanationUtils'
import { formatRiskProbability } from '@/features/shared/riskPresentation'

const EMPTY_VALUE = '—'

const topicLabels: Record<string, string> = {
  urgent: '紧急提醒',
  follow_up: '随访建议',
  lifestyle: '生活方式',
  prevention: '预防建议',
  maintenance: '日常管理',
  confidence_notice: '置信度提示',
}

const priorityLabels: Record<string, string> = {
  high: '重点干预',
  medium: '持续观察',
  low: '日常管理',
}

type UnknownRecord = Record<string, unknown>

export interface AuditDetailRow {
  label: string
  value: string
}

export interface AuditDetailReason {
  code: string
  label: string
  description: string
}

export interface AuditDetailRecommendation {
  key: string
  badge: string
  title: string
  summary: string
  reason: string | null
  actions: string[]
  sourceLabel: string | null
}

export interface AuditDetailPresentation {
  inputRows: AuditDetailRow[]
  fusionRows: AuditDetailRow[]
  fusionReasons: AuditDetailReason[]
  forecastRows: AuditDetailRow[]
  confidenceReasons: AuditDetailReason[]
  recommendations: AuditDetailRecommendation[]
}

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function pickValue(source: UnknownRecord | PredictionSnapshot | null | undefined, ...keys: string[]): unknown {
  if (!source) return undefined
  for (const key of keys) {
    const value = source[key]
    if (value !== undefined && value !== null && value !== '') {
      return value
    }
  }
  return undefined
}

function getString(source: UnknownRecord, ...keys: string[]): string | null {
  const value = pickValue(source, ...keys)
  if (typeof value === 'string' && value.trim()) return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  return null
}

function stringifyValue(value: unknown): string {
  if (value === undefined || value === null || value === '') return EMPTY_VALUE
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  try {
    return JSON.stringify(value)
  } catch {
    return String(value)
  }
}

function formatNumeric(value: unknown, unit = '', digits = 1): string {
  const numeric = toNumber(value)
  if (numeric == null) return EMPTY_VALUE
  return `${formatNumber(numeric, digits)}${unit}`
}

function formatInteger(value: unknown, unit = ''): string {
  const numeric = toNumber(value)
  if (numeric == null) return EMPTY_VALUE
  return `${Math.round(numeric)}${unit}`
}

function formatProbabilityValue(value: unknown): string {
  const numeric = toNumber(value)
  return numeric == null ? EMPTY_VALUE : formatRiskProbability(numeric)
}

function formatAdjustment(value: unknown): string {
  const numeric = toNumber(value)
  if (numeric == null) return EMPTY_VALUE
  const sign = numeric > 0 ? '+' : ''
  return `${sign}${(numeric * 100).toFixed(1)} 个百分点`
}

function formatRatio(value: unknown): string {
  const numeric = toNumber(value)
  if (numeric == null) return EMPTY_VALUE
  return `${(numeric * 100).toFixed(1)}%`
}

function formatYesNo(value: unknown): string {
  const binary = toBinary(value)
  if (binary == null) return EMPTY_VALUE
  return binary === 1 ? '是' : '否'
}

function formatGender(input?: PredictionSnapshot | null): string {
  const male = pickValue(input, 'male')
  if (male === 1 || male === '1') return '男'
  if (male === 0 || male === '0') return '女'
  const gender = pickValue(input, 'gender')
  if (gender === 'Male') return '男'
  if (gender === 'Female') return '女'
  return EMPTY_VALUE
}

function buildInputRows(input: PredictionSnapshot | null): AuditDetailRow[] {
  return [
    { label: '年龄', value: formatInteger(pickValue(input, 'age'), ' 岁') },
    { label: '性别', value: formatGender(input) },
    { label: 'BMI', value: formatNumeric(pickValue(input, 'bmi', 'BMI'), '', 1) },
    { label: '收缩压', value: formatNumeric(pickValue(input, 'systolic_bp', 'sysBP'), ' mmHg', 1) },
    { label: '舒张压', value: formatNumeric(pickValue(input, 'diastolic_bp', 'diaBP'), ' mmHg', 1) },
    { label: '心率', value: formatInteger(pickValue(input, 'heart_rate', 'heartRate'), ' 次/分') },
    { label: '当前吸烟', value: formatYesNo(pickValue(input, 'current_smoker', 'currentSmoker', 'smoking')) },
    { label: '日吸烟支数', value: formatInteger(pickValue(input, 'cigs_per_day', 'cigsPerDay'), ' 支') },
    { label: '降压药', value: formatYesNo(pickValue(input, 'bp_meds', 'BPMeds')) },
    { label: '糖尿病', value: formatYesNo(pickValue(input, 'diabetes')) },
    { label: '总胆固醇', value: formatNumeric(pickValue(input, 'tot_chol', 'totChol', 'cholesterol'), '', 1) },
    { label: '血糖', value: formatNumeric(pickValue(input, 'glucose'), '', 1) },
  ]
}

function buildFusionRows(meta: UnknownRecord): AuditDetailRow[] {
  const policyText = getMedicationPolicyText(meta.bp_meds_policy)
  return [
    { label: '模型基础风险', value: formatProbabilityValue(meta.raw_probability) },
    { label: '融合后风险', value: formatProbabilityValue(meta.fused_probability) },
    { label: '总修正', value: formatAdjustment(meta.adjustment) },
    { label: '趋势修正', value: formatAdjustment(meta.trend_adjustment) },
    { label: '服药修正', value: formatAdjustment(meta.medication_adjustment) },
    { label: '服药输入', value: formatYesNo(meta.bp_meds_input) },
    { label: '模型服药值', value: formatYesNo(meta.bp_meds_model_value) },
    { label: '服药策略', value: policyText ?? stringifyValue(meta.bp_meds_policy) },
  ]
}

function buildForecastRows(summary: UnknownRecord): AuditDetailRow[] {
  return [
    { label: '预测天数', value: formatInteger(summary.forecast_days, ' 天') },
    { label: '平均收缩压', value: formatNumeric(summary.avg_sys, ' mmHg', 1) },
    { label: '平均舒张压', value: formatNumeric(summary.avg_dia, ' mmHg', 1) },
    { label: '最高收缩压', value: formatNumeric(summary.max_sys, ' mmHg', 1) },
    { label: '最高舒张压', value: formatNumeric(summary.max_dia, ' mmHg', 1) },
    { label: '高血压范围天数', value: formatInteger(summary.high_bp_days, ' 天') },
    { label: '正常高值天数', value: formatInteger(summary.elevated_bp_days, ' 天') },
    { label: '收缩压变化', value: formatNumeric(summary.sys_slope, ' mmHg', 1) },
    { label: '舒张压变化', value: formatNumeric(summary.dia_slope, ' mmHg', 1) },
    { label: '收缩压波动', value: formatNumeric(summary.sys_volatility, ' mmHg', 1) },
    { label: '舒张压波动', value: formatNumeric(summary.dia_volatility, ' mmHg', 1) },
    { label: '高血压范围占比', value: formatRatio(summary.high_bp_ratio) },
    { label: '正常高值占比', value: formatRatio(summary.elevated_bp_ratio) },
  ]
}

function buildReasonItem(item: unknown, index: number, source: 'confidence' | 'fusion'): AuditDetailReason {
  if (typeof item === 'string') {
    const detail = source === 'confidence'
      ? getConfidenceReasonDetails([item])[0]
      : getFusionReasonDetails([item])[0]
    return detail
  }

  if (isRecord(item)) {
    const code = getString(item, 'code', 'reason_code', 'reason') ?? `reason-${index + 1}`
    const catalogDetail = source === 'confidence'
      ? getConfidenceReasonDetails([code])[0]
      : getFusionReasonDetails([code])[0]
    return {
      code,
      label: getString(item, 'label', 'title') ?? catalogDetail.label,
      description: getString(item, 'description', 'content') ?? catalogDetail.description,
    }
  }

  return {
    code: `reason-${index + 1}`,
    label: stringifyValue(item),
    description: '该规则参与了本次结果的解释，请结合当前输入数据和趋势信息综合理解。',
  }
}

function buildReasonItems(items: unknown, source: 'confidence' | 'fusion'): AuditDetailReason[] {
  if (!Array.isArray(items)) return []
  return items.map((item, index) => buildReasonItem(item, index, source))
}

function buildActions(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value
      .map((item) => stringifyValue(item))
      .filter((item) => item !== EMPTY_VALUE)
  }
  if (typeof value === 'string' && value.trim()) return [value]
  return []
}

function buildRecommendation(item: unknown, index: number): AuditDetailRecommendation {
  if (!isRecord(item)) {
    const summary = stringifyValue(item)
    return {
      key: `${index}-${summary}`,
      badge: '健康建议',
      title: `健康建议 ${index + 1}`,
      summary,
      reason: null,
      actions: [],
      sourceLabel: null,
    }
  }

  const topic = getString(item, 'topic', 'category')
  const priority = getString(item, 'priority')
  const badge = (topic && topicLabels[topic]) || (priority && priorityLabels[priority]) || topic || priority || '健康建议'
  const title = getString(item, 'title') ?? badge
  const summary = getString(item, 'summary', 'content') ?? stringifyValue(item)
  const reason = getString(item, 'reason', 'basis')
  const sourceLabel = getString(item, 'source_label', 'sourceLabel', 'source')

  return {
    key: `${index}-${title}-${summary}`,
    badge,
    title,
    summary,
    reason,
    actions: buildActions(item.actions),
    sourceLabel,
  }
}

export function buildAuditDetailPresentation(detail: PredictionAuditDetail): AuditDetailPresentation {
  const fusionMeta = detail.fusion_meta ?? {}
  const trendSummary = isRecord(fusionMeta.trend_summary) ? fusionMeta.trend_summary : {}
  const forecastSummary = Object.keys(detail.forecast_summary ?? {}).length > 0
    ? detail.forecast_summary
    : trendSummary

  return {
    inputRows: buildInputRows(detail.input_data),
    fusionRows: buildFusionRows(fusionMeta),
    fusionReasons: buildReasonItems(fusionMeta.reasons, 'fusion'),
    forecastRows: buildForecastRows(forecastSummary),
    confidenceReasons: buildReasonItems(detail.confidence_reasons, 'confidence'),
    recommendations: detail.recommendations.map(buildRecommendation),
  }
}
