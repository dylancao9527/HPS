import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { chartPalette } from '@/features/shared/chartPalette'
import type { WeeklyReportSummary } from '@/features/weekly-report/types'

interface WeeklyBloodPressureChartProps {
  report: WeeklyReportSummary
}

export default function WeeklyBloodPressureChart({ report }: WeeklyBloodPressureChartProps) {
  const { bp_summary: bpSummary } = report
  const chartData = bpSummary.enough_data
    ? [
        {
          name: '收缩压',
          current: bpSummary.current_average_systolic,
          previous: bpSummary.previous_average_systolic,
        },
        {
          name: '舒张压',
          current: bpSummary.current_average_diastolic,
          previous: bpSummary.previous_average_diastolic,
        },
      ]
    : []

  if (!chartData.length) {
    return (
      <div className="weekly-report-empty-chart" role="status">
        <strong>数据不足</strong>
        <span>继续记录血压后，这里会展示最近7天与前7天的平均血压对比。</span>
      </div>
    )
  }

  return (
    <div
      className="weekly-report-chart"
      role="img"
      aria-label="最近7天与前7天平均收缩压和舒张压对比图"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="name" stroke="var(--text-secondary)" fontSize={12} />
          <YAxis stroke="var(--text-secondary)" fontSize={12} domain={['auto', 'auto']} />
          <Tooltip
            contentStyle={{
              background: 'var(--card-bg)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              color: 'var(--text)',
            }}
            formatter={(value, name) => [`${Number(value).toFixed(1)} mmHg`, name]}
          />
          <Legend />
          <Bar dataKey="previous" name="前7天" fill={chartPalette.neutral} radius={[8, 8, 0, 0]} />
          <Bar dataKey="current" name="最近7天" fill={chartPalette.systolic} radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
