import { useState } from 'react'
import Card from '@/components/Card'
import { Database } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { runAdminExport, trainingDataExportTask } from '@/features/admin/exportDownloads'
import type { AdminStats, AdminTrainingExportStats } from '@/types/admin'
import { chartPalette } from '@/features/shared/chartPalette'

interface ExportPanelProps {
  stats: AdminStats | null
}

interface ExportChartDatum {
  name: string
  value: number
  fill: string
  tone: string
}

function buildSampleDistribution(trainingStats: AdminTrainingExportStats): ExportChartDatum[] {
  return [
    { name: '正样本', value: trainingStats.positive_samples, fill: chartPalette.samplePositive, tone: 'positive' },
    { name: '负样本', value: trainingStats.negative_samples, fill: chartPalette.sampleNegative, tone: 'negative' },
  ]
}

function buildLabelSourceData(trainingStats: AdminTrainingExportStats): ExportChartDatum[] {
  return [
    { name: '自报标签', value: trainingStats.diagnosis_labeled_samples, fill: chartPalette.selfReport, tone: 'self-report' },
    { name: '规则标注', value: trainingStats.rule_labeled_samples, fill: chartPalette.rule, tone: 'rule' },
    { name: '跳过用户', value: trainingStats.skipped_users, fill: chartPalette.skipped, tone: 'skipped' },
  ]
}

export default function ExportPanel({ stats }: ExportPanelProps) {
  const trainingStats = stats?.training_export ?? null
  const sampleDistribution = trainingStats ? buildSampleDistribution(trainingStats) : []
  const labelSourceData = trainingStats ? buildLabelSourceData(trainingStats) : []
  const [downloadError, setDownloadError] = useState<string | null>(null)

  const downloadFile = async (): Promise<void> => {
    try {
      setDownloadError(null)
      await runAdminExport(trainingDataExportTask())
    } catch (caughtError) {
      setDownloadError(caughtError instanceof Error ? caughtError.message : '导出训练数据失败')
    }
  }

  return (
    <Card title="数据导出">
      <div className="admin-chart-header admin-chart-header--compact-top">
        <div>
          <p className="admin-chart-subtitle">
            用于查看当前训练样本的类别分布与标签来源，并导出 LightGBM 再训练所需的结构化 CSV 数据。
          </p>
        </div>
      </div>

      {stats && (
        <>
          <div className="summary-grid admin-summary-grid">
            <div className="summary-item"><span className="summary-label">总用户数</span><span className="summary-value">{stats.total_users}</span></div>
            <div className="summary-item"><span className="summary-label">血压记录数</span><span className="summary-value">{stats.total_bp_records}</span></div>
            <div className="summary-item"><span className="summary-label">预测记录数</span><span className="summary-value">{stats.total_predictions}</span></div>
          </div>

          {trainingStats && (
            <div className="summary-grid admin-summary-grid">
              <div className="summary-item"><span className="summary-label">可导出样本数</span><span className="summary-value">{trainingStats.exportable_samples}</span></div>
              <div className="summary-item"><span className="summary-label">正样本比例</span><span className="summary-value">{(trainingStats.positive_ratio * 100).toFixed(1)}%</span></div>
              <div className="summary-item"><span className="summary-label">自报标签数</span><span className="summary-value">{trainingStats.diagnosis_labeled_samples}</span></div>
              <div className="summary-item"><span className="summary-label">规则标注数</span><span className="summary-value">{trainingStats.rule_labeled_samples}</span></div>
              <div className="summary-item"><span className="summary-label">跳过用户数</span><span className="summary-value">{trainingStats.skipped_users}</span></div>
              <div className="summary-item"><span className="summary-label">BP均值窗口</span><span className="summary-value">最近 {trainingStats.recent_bp_avg_count} 条</span></div>
            </div>
          )}

          {trainingStats && (
            <div className="admin-chart-grid">
              <div className="card admin-chart-card admin-chart-card--flush">
                <div className="admin-chart-header">
                  <div>
                    <div className="card-title">训练样本类别分布</div>
                    <p className="admin-chart-subtitle">直观查看当前可导出训练样本的正负样本占比</p>
                  </div>
                </div>
                <div className="admin-chart-shell">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={sampleDistribution}
                        dataKey="value"
                        nameKey="name"
                        innerRadius={60}
                        outerRadius={92}
                        paddingAngle={3}
                      >
                        {sampleDistribution.map((entry) => (
                          <Cell key={entry.name} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value: number | string) => [value, '样本数']} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="admin-chart-legend">
                  {sampleDistribution.map((item) => (
                    <span key={item.name} className="admin-legend-item">
                      <span className={`admin-legend-dot admin-legend-dot--${item.tone}`} />
                      {item.name}：{item.value}
                    </span>
                  ))}
                </div>
              </div>

              <div className="card admin-chart-card admin-chart-card--flush">
                <div className="admin-chart-header">
                  <div>
                    <div className="card-title">训练标签来源构成</div>
                    <p className="admin-chart-subtitle">区分自报病史、规则标注与被跳过用户的数量</p>
                  </div>
                </div>
                <div className="admin-chart-shell">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={labelSourceData} margin={{ top: 8, right: 12, left: 0, bottom: 8 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip formatter={(value: number | string) => [value, '数量']} />
                      <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                        {labelSourceData.map((entry) => (
                          <Cell key={entry.name} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </>
      )}
      <div className="admin-export-action-wrap">
        <div className="export-card admin-export-card-enhanced">
          <div>
            <div className="card-title admin-export-title">导出训练数据</div>
            <p className="admin-chart-subtitle">每个用户导出一条样本，血压相关特征默认使用最近真实记录均值，适合用于模型迭代与论文实验分析。</p>
          </div>
          <button className="btn btn-primary" onClick={() => void downloadFile()}>
            <Database size={16} /> 导出训练数据
          </button>
          <span className="export-hint"><strong>LightGBM</strong> 再训练数据（每用户一条，血压使用最近真实记录均值）</span>
          {trainingStats && <span className="export-hint admin-export-hint-secondary">当前可导出 {trainingStats.exportable_samples} 条样本，其中正样本 {trainingStats.positive_samples} 条、负样本 {trainingStats.negative_samples} 条。</span>}
          {downloadError && <span className="export-hint admin-export-hint-secondary">{downloadError}</span>}
        </div>
      </div>
    </Card>
  )
}
