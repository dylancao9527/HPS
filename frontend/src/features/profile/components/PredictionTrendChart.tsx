import { useEffect, useMemo, useState } from 'react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { NameType, ValueType } from 'recharts/types/component/DefaultTooltipContent'
import type { AggregatedTrendPoint, ProfilePredictionTrendResponse, RawProfilePredictionTrendRecord, TrendGranularity } from '@/types/profile'
import Card from '@/components/Card'
import { getPredictionTrend } from '@/features/profile/api/profilePredictionApi'
import { chartPalette } from '@/features/shared/chartPalette'

function getUtcParts(date: Date): { y: number; m: string; d: string; h: string } {
  return {
    y: date.getUTCFullYear(),
    m: `${date.getUTCMonth() + 1}`.padStart(2, '0'),
    d: `${date.getUTCDate()}`.padStart(2, '0'),
    h: `${date.getUTCHours()}`.padStart(2, '0'),
  }
}

function formatBucket(date: Date, granularity: TrendGranularity): string {
  const { y, m, d, h } = getUtcParts(date)

  if (granularity === 'hour') return `${y}-${m}-${d} ${h}:00 UTC`
  if (granularity === 'month') return `${y}-${m}`
  return `${y}-${m}-${d}`
}

function formatLabel(bucket: string, granularity: TrendGranularity): string {
  if (granularity === 'hour') return bucket.slice(5)
  if (granularity === 'month') return bucket
  return bucket.slice(5)
}

function aggregateRisk(records: RawProfilePredictionTrendRecord[], granularity: TrendGranularity): AggregatedTrendPoint[] {
  const grouped = new Map<string, { total: number; count: number }>()

  for (const record of records) {
    if (record.risk_probability == null || !record.created_at) continue
    const date = new Date(record.created_at)
    if (Number.isNaN(date.getTime())) continue

    const bucket = formatBucket(date, granularity)
    const current = grouped.get(bucket) || { total: 0, count: 0 }
    current.total += record.risk_probability * 100
    current.count += 1
    grouped.set(bucket, current)
  }

  return [...grouped.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([bucket, value]) => ({
      bucket,
      label: formatLabel(bucket, granularity),
      risk: Number((value.total / value.count).toFixed(1)),
      samples: value.count,
    }))
}

export default function PredictionTrendChart() {
  const [records, setRecords] = useState<RawProfilePredictionTrendRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [granularity, setGranularity] = useState<TrendGranularity>('day')

  useEffect(() => {
    let active = true

    ;(async () => {
      try {
        const data: ProfilePredictionTrendResponse = await getPredictionTrend(120)
        if (!active) return
        setError(null)
        setRecords(data.records || [])
      } catch (caughtError) {
        if (!active) return
        setError(caughtError instanceof Error ? caughtError.message : '预测趋势加载失败')
      } finally {
        if (active) setLoading(false)
      }
    })()

    return () => {
      active = false
    }
  }, [])

  const trendData = useMemo<AggregatedTrendPoint[]>(() => aggregateRisk(records, granularity), [records, granularity])

  if (loading) {
    return (
      <Card title="预测趋势">
        <div className="prediction-trend-state prediction-trend-state--loading" role="status"><div className="spinner" /></div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card title="预测趋势">
        <div className="prediction-trend-state prediction-trend-state--empty">
          <p>{error}</p>
          <p className="prediction-trend-empty-hint">请稍后重试；若持续失败，请检查预测趋势接口状态。</p>
        </div>
      </Card>
    )
  }

  if (trendData.length === 0) {
    return (
      <Card title="预测趋势">
        <div className="prediction-trend-state prediction-trend-state--empty">
          <p>暂无可展示的预测趋势</p>
          <p className="prediction-trend-empty-hint">前往「风险预测」页面进行预测后再查看</p>
        </div>
      </Card>
    )
  }

  return (
    <Card title="风险概率趋势图">
      <div className="prediction-trend-toolbar">
        {([
          ['hour', '按小时'],
          ['day', '按天'],
          ['month', '按月'],
        ] as const).map(([value, label]) => (
          <button
            key={value}
            className={`btn ${granularity === value ? 'btn-primary' : 'btn-ghost'} btn-sm`}
            onClick={() => setGranularity(value)}
            type="button"
          >
            {label}
          </button>
        ))}
      </div>

      <div className="chart-container prediction-trend-chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={trendData}>
            <defs>
              <linearGradient id="profileRiskGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={chartPalette.risk} stopOpacity={0.28} />
                <stop offset="95%" stopColor={chartPalette.risk} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="label" stroke="var(--text-secondary)" fontSize={12} />
            <YAxis
              stroke="var(--text-secondary)"
              fontSize={12}
              domain={[0, 100]}
              tickFormatter={(value: number) => `${value}%`}
            />
            <Tooltip
              contentStyle={{
                background: 'var(--card-bg)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                color: 'var(--text)',
              }}
              formatter={(value: ValueType, name: NameType, item) => {
                if (name === 'risk') return [`${value}%`, '平均风险']
                return [value, item?.payload?.samples ? `${item.payload.samples} 次预测` : '样本数']
              }}
              labelFormatter={(label, payload) => {
                const bucket = payload?.[0]?.payload?.bucket as string | undefined
                return bucket || String(label)
              }}
            />
            <Area
              type="monotone"
              dataKey="risk"
              stroke={chartPalette.risk}
              strokeWidth={2}
              fill="url(#profileRiskGradient)"
              dot={{ r: 3, fill: chartPalette.risk }}
              activeDot={{ r: 5 }}
              name="risk"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <p className="prediction-trend-footnote">
        提示：图中数值为同一时间粒度下的风险概率平均值，可用于观察整体变化趋势。
      </p>
    </Card>
  )
}
