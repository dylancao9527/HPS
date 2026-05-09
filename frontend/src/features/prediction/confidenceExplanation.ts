import type { PredictionFusionMeta } from '@/types/prediction'
import type { ExplanationReason } from '@/features/prediction/explanationTypes'
import { buildReasonList, formatNumber, toNumber } from '@/features/prediction/explanationUtils'

const confidenceReasonCatalog: Record<string, Omit<ExplanationReason, 'code'>> = {
  insufficient_days: {
    label: '历史记录天数偏少',
    description: '当前可用于趋势建模的天数还不够多，本次结果更适合作为近期参考而不是长期判断。',
  },
  window_capped: {
    label: '训练窗口已截断',
    description: '系统为了保证响应速度和模型稳定性，只使用了最近一段时间的血压记录进行训练。',
  },
  sparse_measurements: {
    label: '单日测量次数偏少',
    description: '部分日期的测量频次较低，会削弱趋势判断对真实日常波动的刻画能力。',
  },
  high_volatility: {
    label: '近期波动较大',
    description: '最近血压波动和变化幅度都较大，说明短期状态不够稳定，模型的趋势结果需要结合连续观察来理解。',
  },
}

const fusionReasonCatalog: Record<string, Omit<ExplanationReason, 'code'>> = {
  high_bp_days: {
    label: '预测期内出现高血压天数',
    description: '未来预测区间内存在达到高血压范围的日期，因此系统提高了最终风险判断。',
  },
  elevated_bp_days: {
    label: '多日处于正常高值',
    description: '虽然未必都达到高血压诊断标准，但连续多日偏高会让系统更谨慎地评估风险。',
  },
  peak_bp: {
    label: '存在较高峰值血压',
    description: '预测结果中出现了较高的收缩压或舒张压峰值，因此系统对最终风险进行了上调。',
  },
  upward_trend: {
    label: '趋势整体上行',
    description: '预测曲线显示未来几天血压有上升趋势，系统因此提高了风险结果。',
  },
  stable_low_trend: {
    label: '趋势平稳且偏低',
    description: '预测区间内血压整体平稳、偏低，因此系统适度下调了最终风险结果。',
  },
  meds_uncontrolled_high_bp: {
    label: '服药背景下仍偏高',
    description: '已填写长期服药背景，但预测期内仍出现偏高血压，系统因此保持更谨慎的风险判断。',
  },
}

const medicationPolicyCatalog: Record<string, string> = {
  neutralized_for_conservative_inference:
    '服药信息在模型推断阶段采用保守处理，不会单独把低风险用户直接抬高；只有趋势仍偏高时才会体现到最终结果中。',
}

export function getConfidenceReasonDetails(codes: unknown): ExplanationReason[] {
  return buildReasonList(codes, confidenceReasonCatalog)
}

export function getFusionReasonDetails(codes: unknown): ExplanationReason[] {
  return buildReasonList(codes, fusionReasonCatalog)
}

export function getMedicationPolicyText(policy: unknown): string | null {
  if (typeof policy !== 'string' || !policy.trim()) return null
  return medicationPolicyCatalog[policy] || '服药字段在模型推断中采用了保守修正策略，用于避免单一特征造成过度放大。'
}

export function summarizeTrendExplanation(fusionMeta?: PredictionFusionMeta | null): string {
  const trend = fusionMeta?.trend_summary
  if (!trend || typeof trend !== 'object') {
    return '系统会先根据档案与血压趋势得到基础风险，再结合未来几天的趋势变化做保守修正。'
  }

  const avgSys = formatNumber(toNumber(trend.avg_sys))
  const avgDia = formatNumber(toNumber(trend.avg_dia))
  const highDays = toNumber(trend.high_bp_days) ?? 0
  const slopeSys = toNumber(trend.sys_slope) ?? 0
  const slopeDia = toNumber(trend.dia_slope) ?? 0

  if (highDays > 0) {
    return `未来 ${trend.forecast_days ?? '-'} 天平均血压约为 ${avgSys}/${avgDia} mmHg，且有 ${highDays} 天处于高血压范围，因此系统对最终风险做了上调。`
  }

  if (slopeSys >= 5 || slopeDia >= 3) {
    return `未来 ${trend.forecast_days ?? '-'} 天平均血压约为 ${avgSys}/${avgDia} mmHg，趋势整体上行，因此最终风险高于模型基础风险。`
  }

  if (slopeSys <= 0 && slopeDia <= 0) {
    return `未来 ${trend.forecast_days ?? '-'} 天平均血压约为 ${avgSys}/${avgDia} mmHg，趋势相对平稳，因此风险修正较为温和。`
  }

  return `未来 ${trend.forecast_days ?? '-'} 天平均血压约为 ${avgSys}/${avgDia} mmHg，系统根据整体趋势对结果进行了保守修正。`
}
