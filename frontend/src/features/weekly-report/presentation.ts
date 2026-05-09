import type { WeeklyReportSummary } from '@/features/weekly-report/types'

export type WeeklyReportMetricTone = 'good' | 'warning' | 'neutral' | 'insufficient'

export interface WeeklyReportMetricPresentation {
  key: 'blood-pressure' | 'high-bp-days' | 'record-days' | 'risk-probability'
  label: string
  currentLabel: string
  previousLabel: string
  changeLabel: string
  helperText: string
  tone: WeeklyReportMetricTone
  enoughData: boolean
}

const DATA_MISSING_TEXT = '数据不足'
const EPSILON = 0.0001

export const WEEKLY_REPORT_TITLE = '周健康报告'
export const WEEKLY_REPORT_CURRENT_PERIOD_LABEL = '最近7天'
export const WEEKLY_REPORT_PREVIOUS_PERIOD_LABEL = '前7天'
export const WEEKLY_REPORT_SCOPE_TEXT = '固定比较最近7天与前7天'
export const WEEKLY_REPORT_DATA_NOTE = '部分指标数据不足，请继续记录血压，系统会自动补齐对比信息。'

export interface WeeklyReportPeriodPresentation {
  currentLabel: string
  previousLabel: string
}

export function buildWeeklyReportPeriodPresentation(report: WeeklyReportSummary): WeeklyReportPeriodPresentation {
  return {
    currentLabel: `${WEEKLY_REPORT_CURRENT_PERIOD_LABEL} ${report.current_period}`,
    previousLabel: `${WEEKLY_REPORT_PREVIOUS_PERIOD_LABEL} ${report.previous_period}`,
  }
}

function isNumber(value: number | null | undefined): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

function formatNumber(value: number, digits = 1): string {
  return value.toFixed(digits)
}

function formatSignedAbs(value: number, digits = 1): string {
  return formatNumber(Math.abs(value), digits)
}

function formatBloodPressureValue(systolic: number | null, diastolic: number | null): string {
  if (!isNumber(systolic) || !isNumber(diastolic)) return '—'
  return `${formatNumber(systolic)}/${formatNumber(diastolic)} mmHg`
}

function formatDays(value: number | null | undefined): string {
  if (!isNumber(value)) return '—'
  return `${value} 天`
}

function formatRiskProbability(value: number | null): string {
  if (!isNumber(value)) return '—'
  return `${(value * 100).toFixed(1)}%`
}

function getTone(delta: number, improvementDirection: 'up' | 'down'): WeeklyReportMetricTone {
  if (Math.abs(delta) < EPSILON) return 'neutral'
  const improved = improvementDirection === 'up' ? delta > 0 : delta < 0
  return improved ? 'good' : 'warning'
}

function describeDayChange(delta: number): string {
  if (delta === 0) return '基本持平'
  const verb = delta > 0 ? '增加' : '减少'
  return `较前7天${verb} ${Math.abs(delta)} 天`
}

function describeRiskChange(current: number | null, previous: number | null): string {
  if (!isNumber(current) || !isNumber(previous)) return DATA_MISSING_TEXT
  const delta = current - previous
  if (Math.abs(delta) < EPSILON) return '基本持平'
  const verb = delta > 0 ? '上升' : '下降'
  return `较前7天${verb} ${formatSignedAbs(delta * 100)} 个百分点`
}

function describeSingleBloodPressureChange(label: string, delta: number): string {
  if (Math.abs(delta) < EPSILON) return `${label}基本持平`
  return `${label}较前7天${delta > 0 ? '上升' : '下降'} ${formatSignedAbs(delta)} mmHg`
}

function describeBloodPressureChange(report: WeeklyReportSummary): string {
  const {
    current_average_systolic: currentSys,
    previous_average_systolic: previousSys,
    current_average_diastolic: currentDia,
    previous_average_diastolic: previousDia,
  } = report.bp_summary

  if (!isNumber(currentSys) || !isNumber(previousSys) || !isNumber(currentDia) || !isNumber(previousDia)) {
    return DATA_MISSING_TEXT
  }

  const sysDelta = currentSys - previousSys
  const diaDelta = currentDia - previousDia

  if (Math.abs(sysDelta) < EPSILON && Math.abs(diaDelta) < EPSILON) {
    return '基本持平'
  }

  if (sysDelta <= EPSILON && diaDelta <= EPSILON) {
    return `较前7天下降 ${formatSignedAbs(sysDelta)}/${formatSignedAbs(diaDelta)} mmHg`
  }

  if (sysDelta >= -EPSILON && diaDelta >= -EPSILON) {
    return `较前7天上升 ${formatSignedAbs(sysDelta)}/${formatSignedAbs(diaDelta)} mmHg`
  }

  return [
    describeSingleBloodPressureChange('收缩压', sysDelta),
    describeSingleBloodPressureChange('舒张压', diaDelta),
  ].join('，')
}

function getBloodPressureTone(report: WeeklyReportSummary): WeeklyReportMetricTone {
  const {
    current_average_systolic: currentSys,
    previous_average_systolic: previousSys,
    current_average_diastolic: currentDia,
    previous_average_diastolic: previousDia,
  } = report.bp_summary

  if (!isNumber(currentSys) || !isNumber(previousSys) || !isNumber(currentDia) || !isNumber(previousDia)) {
    return 'insufficient'
  }

  const combinedDelta = currentSys - previousSys + currentDia - previousDia
  return getTone(combinedDelta, 'down')
}

export function buildWeeklyReportMetrics(report: WeeklyReportSummary): WeeklyReportMetricPresentation[] {
  const bpEnough = report.bp_summary.enough_data
  const highBpEnough = report.high_bp_summary.enough_data
  const adherenceEnough = report.adherence_summary.enough_data
  const riskEnough = report.risk_summary.enough_data

  const highBpDelta = report.high_bp_summary.current_high_bp_days - report.high_bp_summary.previous_high_bp_days
  const recordDelta = report.adherence_summary.record_change
  const riskDelta =
    isNumber(report.risk_summary.current_average_risk_probability) &&
    isNumber(report.risk_summary.previous_average_risk_probability)
      ? report.risk_summary.current_average_risk_probability - report.risk_summary.previous_average_risk_probability
      : 0

  return [
    {
      key: 'blood-pressure',
      label: '平均血压',
      currentLabel: formatBloodPressureValue(
        report.bp_summary.current_average_systolic,
        report.bp_summary.current_average_diastolic,
      ),
      previousLabel: formatBloodPressureValue(
        report.bp_summary.previous_average_systolic,
        report.bp_summary.previous_average_diastolic,
      ),
      changeLabel: bpEnough ? describeBloodPressureChange(report) : DATA_MISSING_TEXT,
      helperText: '最近7天日均收缩压/舒张压',
      tone: bpEnough ? getBloodPressureTone(report) : 'insufficient',
      enoughData: bpEnough,
    },
    {
      key: 'high-bp-days',
      label: '高血压偏高天数',
      currentLabel: formatDays(report.high_bp_summary.current_high_bp_days),
      previousLabel: formatDays(report.high_bp_summary.previous_high_bp_days),
      changeLabel: highBpEnough ? describeDayChange(highBpDelta) : DATA_MISSING_TEXT,
      helperText: '按日均血压是否偏高统计',
      tone: highBpEnough ? getTone(highBpDelta, 'down') : 'insufficient',
      enoughData: highBpEnough,
    },
    {
      key: 'record-days',
      label: '记录完成天数',
      currentLabel: formatDays(report.adherence_summary.current_record_days),
      previousLabel: formatDays(report.adherence_summary.previous_record_days),
      changeLabel: adherenceEnough ? describeDayChange(recordDelta) : DATA_MISSING_TEXT,
      helperText: '最近7天内有血压记录的天数',
      tone: adherenceEnough ? getTone(recordDelta, 'up') : 'insufficient',
      enoughData: adherenceEnough,
    },
    {
      key: 'risk-probability',
      label: '高血压风险概率',
      currentLabel: formatRiskProbability(report.risk_summary.current_average_risk_probability),
      previousLabel: formatRiskProbability(report.risk_summary.previous_average_risk_probability),
      changeLabel: riskEnough
        ? describeRiskChange(
            report.risk_summary.current_average_risk_probability,
            report.risk_summary.previous_average_risk_probability,
          )
        : DATA_MISSING_TEXT,
      helperText: '最近7天预测记录的平均风险概率',
      tone: riskEnough ? getTone(riskDelta, 'down') : 'insufficient',
      enoughData: riskEnough,
    },
  ]
}

export function hasInsufficientWeeklyReportData(report: WeeklyReportSummary): boolean {
  return buildWeeklyReportMetrics(report).some((metric) => !metric.enoughData)
}
