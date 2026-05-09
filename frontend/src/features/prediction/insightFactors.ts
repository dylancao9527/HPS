import type { PredictionInsightFactor, PredictionInsightSource } from '@/features/prediction/explanationTypes'
import { formatMetricValue, formatNumber, toBinary, toNumber } from '@/features/prediction/explanationUtils'

export function getPredictionInsightFactors(source: PredictionInsightSource): PredictionInsightFactor[] {
  const input = source.input_data
  const fusionMeta = source.fusion_meta
  const trend = fusionMeta?.trend_summary
  const factors: Array<{ weight: number; factor: PredictionInsightFactor }> = []

  const systolic = toNumber(input?.systolic_bp ?? input?.sysBP)
  const diastolic = toNumber(input?.diastolic_bp ?? input?.diaBP)
  const bmi = toNumber(input?.bmi ?? input?.BMI)
  const cholesterol = toNumber(input?.tot_chol ?? input?.totChol ?? input?.cholesterol)
  const glucose = toNumber(input?.glucose)
  const smoking = toBinary(input?.current_smoker ?? input?.currentSmoker ?? input?.smoking)
  const diabetes = toBinary(input?.diabetes)
  const bpMeds = toBinary(input?.bp_meds ?? input?.BPMeds)

  if (systolic != null && diastolic != null) {
    if (systolic >= 140 || diastolic >= 90) {
      factors.push({
        weight: 100,
        factor: {
          id: 'current-bp-high',
          title: '当前血压已偏高',
          value: `${formatNumber(systolic)}/${formatNumber(diastolic)} mmHg`,
          tone: 'high',
          description: '当前收缩压或舒张压已进入高血压范围，这是本次风险判断中最直接的输入之一。',
        },
      })
    } else if (systolic >= 130 || diastolic >= 85) {
      factors.push({
        weight: 82,
        factor: {
          id: 'current-bp-elevated',
          title: '当前血压处于正常高值',
          value: `${formatNumber(systolic)}/${formatNumber(diastolic)} mmHg`,
          tone: 'medium',
          description: '虽然未必达到高血压诊断标准，但当前血压已经偏高，会推动系统做更谨慎的评估。',
        },
      })
    }
  }

  if (trend && typeof trend === 'object') {
    const highDays = toNumber(trend.high_bp_days) ?? 0
    const elevatedDays = toNumber(trend.elevated_bp_days) ?? 0
    const sysSlope = toNumber(trend.sys_slope) ?? 0
    const diaSlope = toNumber(trend.dia_slope) ?? 0
    const avgSys = formatNumber(toNumber(trend.avg_sys))
    const avgDia = formatNumber(toNumber(trend.avg_dia))

    if (highDays > 0) {
      factors.push({
        weight: 96,
        factor: {
          id: 'trend-high-days',
          title: '预测期内仍有高血压天数',
          value: `${highDays} 天`,
          tone: 'high',
          description: `未来几天平均血压约为 ${avgSys}/${avgDia} mmHg，预测区间中仍有高血压日，说明短期内风险不会快速回落。`,
        },
      })
    } else if (elevatedDays > 0) {
      factors.push({
        weight: 76,
        factor: {
          id: 'trend-elevated-days',
          title: '未来多日仍偏高',
          value: `${elevatedDays} 天`,
          tone: 'medium',
          description: `未来几天平均血压约为 ${avgSys}/${avgDia} mmHg，虽然未明显恶化，但持续偏高会让系统保守上调结果。`,
        },
      })
    }

    if (sysSlope >= 5 || diaSlope >= 3) {
      factors.push({
        weight: 86,
        factor: {
          id: 'trend-upward',
          title: '未来趋势有上升倾向',
          value: `收缩压 ${sysSlope > 0 ? '+' : ''}${formatNumber(sysSlope)} / 舒张压 ${diaSlope > 0 ? '+' : ''}${formatNumber(diaSlope)} mmHg`,
          tone: 'high',
          description: '预测曲线显示未来几天可能继续走高，因此系统会在基础风险上增加趋势修正。',
        },
      })
    } else if (sysSlope <= 0 && diaSlope <= 0 && highDays === 0) {
      factors.push({
        weight: 34,
        factor: {
          id: 'trend-stable',
          title: '未来趋势相对平稳',
          value: `收缩压 ${formatNumber(sysSlope)} / 舒张压 ${formatNumber(diaSlope)} mmHg`,
          tone: 'positive',
          description: '未来几天没有明显上升趋势，这会限制系统对风险的上调幅度。',
        },
      })
    }
  }

  if (bmi != null) {
    if (bmi >= 28) {
      factors.push({
        weight: 70,
        factor: {
          id: 'bmi-obesity',
          title: 'BMI 处于肥胖范围',
          value: formatNumber(bmi),
          tone: 'high',
          description: 'BMI 偏高会增加心血管负担，也是高血压风险的重要背景因素。',
        },
      })
    } else if (bmi >= 24) {
      factors.push({
        weight: 52,
        factor: {
          id: 'bmi-overweight',
          title: 'BMI 处于超重范围',
          value: formatNumber(bmi),
          tone: 'medium',
          description: '体重偏高会持续影响血压控制，因此系统会把它作为风险背景因素纳入判断。',
        },
      })
    }
  }

  if (diabetes === 1) {
    factors.push({
      weight: 68,
      factor: {
        id: 'diabetes',
        title: '存在糖尿病背景',
        value: '已填写',
        tone: 'high',
        description: '糖尿病与高血压常共同增加心脑血管风险，因此会提高系统对结果的警惕程度。',
      },
    })
  }

  if (glucose != null) {
    if (glucose >= 126) {
      factors.push({
        weight: 64,
        factor: {
          id: 'glucose-high',
          title: '血糖已偏高',
          value: `${formatNumber(glucose)} mg/dL`,
          tone: 'high',
          description: '血糖达到糖尿病提示范围时，会显著增加整体心血管风险。',
        },
      })
    } else if (glucose >= 100) {
      factors.push({
        weight: 46,
        factor: {
          id: 'glucose-borderline',
          title: '血糖处于边缘偏高',
          value: `${formatNumber(glucose)} mg/dL`,
          tone: 'medium',
          description: '血糖已有异常趋势，说明代谢风险开始累积，会对结果产生一定影响。',
        },
      })
    }
  }

  if (cholesterol != null) {
    if (cholesterol >= 240) {
      factors.push({
        weight: 58,
        factor: {
          id: 'cholesterol-high',
          title: '总胆固醇偏高',
          value: `${formatNumber(cholesterol)} mg/dL`,
          tone: 'high',
          description: '胆固醇异常会增加动脉粥样硬化和心血管风险，因此也是重要背景因素。',
        },
      })
    } else if (cholesterol >= 200) {
      factors.push({
        weight: 42,
        factor: {
          id: 'cholesterol-borderline',
          title: '总胆固醇边缘偏高',
          value: `${formatNumber(cholesterol)} mg/dL`,
          tone: 'medium',
          description: '胆固醇已偏离理想范围，系统会将其视作长期风险的提示因素。',
        },
      })
    }
  }

  if (smoking === 1) {
    factors.push({
      weight: 44,
      factor: {
        id: 'smoking',
        title: '存在吸烟因素',
        value: formatMetricValue(input?.cigs_per_day ?? input?.cigsPerDay, ' 支/天'),
        tone: 'medium',
        description: '吸烟会增加血管负担并提升心血管事件风险，因此会拉高风险背景值。',
      },
    })
  }

  if (bpMeds === 1) {
    factors.push({
      weight: 30,
      factor: {
        id: 'bp-meds',
        title: '长期服药背景',
        value: '已填写',
        tone: 'neutral',
        description: '系统会把长期按医嘱服药视作健康管理背景信息，而不是单独抬高风险的直接证据。',
      },
    })
  }

  if (factors.length === 0) {
    return [
      {
        id: 'default',
        title: '当前输入整体较平稳',
        value: '无明显异常特征',
        tone: 'positive',
        description: '本次结果主要由整体血压趋势和基础档案共同决定，没有出现特别突出的单一风险因素。',
      },
    ]
  }

  return factors
    .sort((left, right) => right.weight - left.weight)
    .map((item) => item.factor)
    .slice(0, 5)
}
