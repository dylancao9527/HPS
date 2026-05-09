import { describe, expect, it } from 'vitest'
import {
  buildWeeklyReportPeriodPresentation,
  buildWeeklyReportMetrics,
  hasInsufficientWeeklyReportData,
} from '@/features/weekly-report/presentation'
import type { WeeklyReportSummary } from '@/features/weekly-report/types'

function buildReport(overrides: Partial<WeeklyReportSummary> = {}): WeeklyReportSummary {
  return {
    current_period: '2026-04-19 ~ 2026-04-25',
    previous_period: '2026-04-12 ~ 2026-04-18',
    bp_summary: {
      current_record_days: 3,
      previous_record_days: 3,
      current_average_systolic: 135,
      previous_average_systolic: 140,
      current_average_diastolic: 85,
      previous_average_diastolic: 90,
      enough_data: true,
    },
    high_bp_summary: {
      current_record_days: 3,
      previous_record_days: 3,
      current_high_bp_days: 1,
      previous_high_bp_days: 3,
      total_high_bp_days: 4,
      enough_data: true,
    },
    adherence_summary: {
      current_record_days: 3,
      previous_record_days: 3,
      record_change: 0,
      enough_data: true,
    },
    risk_summary: {
      current_record_count: 2,
      previous_record_count: 1,
      current_average_risk_probability: 0.25,
      previous_average_risk_probability: 0.4,
      enough_data: true,
    },
    overall_trend_text: '与前7天相比，最近7天平均血压下降，风险较前7天下降，记录完成天数基本持平。',
    ...overrides,
  }
}

describe('weekly report presentation', () => {
  it('builds the four fixed weekly report metrics', () => {
    const report = buildReport()
    const metrics = buildWeeklyReportMetrics(report)

    expect(buildWeeklyReportPeriodPresentation(report)).toEqual({
      currentLabel: '最近7天 2026-04-19 ~ 2026-04-25',
      previousLabel: '前7天 2026-04-12 ~ 2026-04-18',
    })
    expect(metrics.map((metric) => metric.label)).toEqual([
      '平均血压',
      '高血压偏高天数',
      '记录完成天数',
      '高血压风险概率',
    ])
    expect(metrics[0]).toMatchObject({
      currentLabel: '135.0/85.0 mmHg',
      previousLabel: '140.0/90.0 mmHg',
      changeLabel: '较前7天下降 5.0/5.0 mmHg',
      tone: 'good',
    })
    expect(metrics[1]).toMatchObject({
      changeLabel: '较前7天减少 2 天',
      tone: 'good',
    })
    expect(metrics[2]).toMatchObject({
      changeLabel: '基本持平',
      tone: 'neutral',
    })
    expect(metrics[3]).toMatchObject({
      currentLabel: '25.0%',
      previousLabel: '40.0%',
      changeLabel: '较前7天下降 15.0 个百分点',
      tone: 'good',
    })
    expect(hasInsufficientWeeklyReportData(buildReport())).toBe(false)
  })

  it('keeps the report frame visible when data is insufficient', () => {
    const report = buildReport({
      bp_summary: {
        current_record_days: 2,
        previous_record_days: 0,
        current_average_systolic: 132.5,
        previous_average_systolic: null,
        current_average_diastolic: 82.5,
        previous_average_diastolic: null,
        enough_data: false,
      },
      high_bp_summary: {
        current_record_days: 2,
        previous_record_days: 0,
        current_high_bp_days: 0,
        previous_high_bp_days: 0,
        total_high_bp_days: 0,
        enough_data: false,
      },
      adherence_summary: {
        current_record_days: 2,
        previous_record_days: 0,
        record_change: 2,
        enough_data: false,
      },
      risk_summary: {
        current_record_count: 0,
        previous_record_count: 0,
        current_average_risk_probability: null,
        previous_average_risk_probability: null,
        enough_data: false,
      },
    })

    const metrics = buildWeeklyReportMetrics(report)

    expect(metrics).toHaveLength(4)
    expect(metrics.every((metric) => metric.changeLabel === '数据不足')).toBe(true)
    expect(metrics.every((metric) => metric.tone === 'insufficient')).toBe(true)
    expect(hasInsufficientWeeklyReportData(report)).toBe(true)
  })
})
