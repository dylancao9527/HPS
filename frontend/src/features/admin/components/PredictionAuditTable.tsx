import { Download } from 'lucide-react'
import Card from '@/components/Card'
import Pagination from '@/components/Pagination'
import type { PredictionAuditRecord } from '@/types/admin'
import type { PredictionAuditFilters } from '@/features/admin/api/adminApi'
import {
  ANOMALY_TYPE_FILTER_OPTIONS,
  formatAnomalyFlagList,
} from '@/features/admin/governancePresentation'
import {
  CONFIDENCE_LEVEL_FILTER_OPTIONS,
  RISK_LEVEL_FILTER_OPTIONS,
  formatConfidenceLevelLabel,
  formatRiskLevelLabel,
  formatRiskProbability,
} from '@/features/shared/riskPresentation'

const ANOMALY_OPTIONS = [
  { value: '', label: '全部异常状态' },
  { value: 'true', label: '仅异常' },
  { value: 'false', label: '仅正常' },
] as const

type FilterKey = keyof PredictionAuditFilters

interface PredictionAuditTableProps {
  records: PredictionAuditRecord[]
  page: number
  totalPages: number
  filters: PredictionAuditFilters
  loading?: boolean
  selectedPredictionId: number | string | null
  onPageChange: (page: number) => void
  onFilterChange: (key: FilterKey, value: string) => void
  onSelectPrediction: (predictionId: number | string | null) => void
  onExport: () => void
}

export default function PredictionAuditTable({
  records,
  page,
  totalPages,
  filters,
  loading = false,
  selectedPredictionId,
  onPageChange,
  onFilterChange,
  onSelectPrediction,
  onExport,
}: PredictionAuditTableProps) {
  return (
    <Card title="预测结果治理列表" className="admin-chart-card admin-chart-card--flush">
      <div className="filter-bar">
        <label>
          风险等级
          <select
            value={filters.riskLevel}
            onChange={(event) => onFilterChange('riskLevel', event.target.value)}
          >
            {RISK_LEVEL_FILTER_OPTIONS.map((option) => (
              <option key={option.value || 'all-risk'} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          置信度
          <select
            value={filters.confidenceLevel}
            onChange={(event) => onFilterChange('confidenceLevel', event.target.value)}
          >
            {CONFIDENCE_LEVEL_FILTER_OPTIONS.map((option) => (
              <option key={option.value || 'all-confidence'} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          异常状态
          <select
            value={filters.hasAnomaly}
            onChange={(event) => onFilterChange('hasAnomaly', event.target.value)}
          >
            {ANOMALY_OPTIONS.map((option) => (
              <option key={option.label} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>

        <label>
          异常类型
          <select
            value={filters.anomalyType}
            onChange={(event) => onFilterChange('anomalyType', event.target.value)}
          >
            {ANOMALY_TYPE_FILTER_OPTIONS.map((option) => (
              <option key={option.value || 'all-anomaly-type'} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <button className="btn btn-ghost btn-sm" onClick={onExport}>
          <Download size={14} /> 导出筛选结果
        </button>
      </div>

      {loading ? (
        <div className="admin-loading-state" role="status" aria-live="polite">
          <div className="spinner" />
          <p className="page-section-desc">正在加载治理记录…</p>
        </div>
      ) : records.length === 0 ? (
        <p className="empty-text">暂无符合条件的预测记录。</p>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>预测ID</th>
                <th>风险等级</th>
                <th>风险概率</th>
                <th>置信度</th>
                <th>训练天数</th>
                <th>BPMeds</th>
                <th>异常标记</th>
                <th>时间</th>
              </tr>
            </thead>
            <tbody>
              {records.map((row) => {
                const selected = row.prediction_id === selectedPredictionId
                return (
                  <tr
                    key={row.prediction_id}
                    onClick={() => onSelectPrediction(row.prediction_id ?? null)}
                    style={{ cursor: 'pointer', background: selected ? 'var(--accent-light)' : 'transparent' }}
                    aria-selected={selected}
                  >
                    <td>{row.prediction_id}</td>
                    <td>{formatRiskLevelLabel(row.risk_level)}</td>
                    <td>{formatRiskProbability(row.risk_probability)}</td>
                    <td>{formatConfidenceLevelLabel(row.confidence_level)}</td>
                    <td>{row.data_days_used ?? '—'}</td>
                    <td>{row.input_data?.bp_meds ?? '—'}</td>
                    <td>{formatAnomalyFlagList(row.anomaly_flags)}</td>
                    <td>{row.created_at ? new Date(row.created_at).toLocaleString('zh-CN') : '—'}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} totalPages={totalPages} onChange={onPageChange} />
    </Card>
  )
}
