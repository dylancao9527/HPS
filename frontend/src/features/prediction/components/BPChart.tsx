import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { BloodPressureForecastPoint } from '@/types/prediction'
import { chartPalette } from '@/features/shared/chartPalette'

interface BPChartProps {
  data?: BloodPressureForecastPoint[] | null
}

export default function BPChart({ data }: BPChartProps) {
  if (!data?.length) {
    return (
      <div className="prediction-empty-state chart-container prediction-chart-empty-state">
        <p className="prediction-empty-title">暂无趋势数据</p>
        <p className="prediction-empty-desc">完成预测后，这里会展示未来血压变化趋势。</p>
      </div>
    )
  }

  return (
    <div
      className="chart-container"
      role="img"
      aria-label="未来血压趋势图，包含收缩压和舒张压变化趋势"
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis
            dataKey="day"
            stroke="var(--text-secondary)"
            fontSize={12}
            tickFormatter={(day) => `第${day}天`}
          />
          <YAxis stroke="var(--text-secondary)" fontSize={12} domain={['auto', 'auto']} />
          <Tooltip
            contentStyle={{
              background: 'var(--card-bg)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              color: 'var(--text)',
            }}
            formatter={(value, name) => [`${value} mmHg`, name]}
          />
          <Legend />
          <Line type="monotone" dataKey="systolic" stroke={chartPalette.systolic} name="收缩压" strokeWidth={2} dot={{ r: 4 }} />
          <Line
            type="monotone"
            dataKey="diastolic"
            stroke={chartPalette.diastolic}
            strokeDasharray="6 4"
            name="舒张压"
            strokeWidth={2}
            dot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
