import { Eye, Trash2 } from 'lucide-react'
import Pagination from '@/components/Pagination'
import type { HistoryRecord } from '@/types/history'
import {
  formatDateTime,
  formatRiskLevelLabel,
  formatRiskProbability,
  getHistoryTrendText,
  getRiskToneClass,
} from '@/features/history/utils'

interface HistoryRecordListProps {
  records: HistoryRecord[]
  page: number
  totalPages: number
  selected: Set<number | string>
  onToggle: (id: number | string) => void
  onOpenDetail: (record: HistoryRecord) => void
  onDelete: (id: number | string) => void
  onPageChange: (page: number) => void
}

export default function HistoryRecordList({
  records,
  page,
  totalPages,
  selected,
  onToggle,
  onOpenDetail,
  onDelete,
  onPageChange,
}: HistoryRecordListProps) {
  return (
    <section className="page-section" aria-labelledby="history-record-list-title">
      <div className="page-section-heading">
        <div>
          <h2 id="history-record-list-title" className="page-section-title">历史记录列表</h2>
          <p className="page-section-desc">每条记录回顾一次7天风险预测，详情只展示用户端预测摘要。</p>
        </div>
      </div>

      {records.length === 0 ? (
        <div className="card state-card history-empty-state">
          <div className="card-title">暂无预测记录</div>
          <p className="page-section-desc">可以先返回预测页生成新结果，或调整日期范围后重新查看。</p>
        </div>
      ) : (
        <>
          <div className="history-list">
            {records.map((record) => (
              <article key={record.id} className={`card history-record-card${record.id !== undefined && selected.has(record.id) ? ' checked' : ''}`}>
                <input
                  type="checkbox"
                  className="history-checkbox"
                  checked={record.id !== undefined ? selected.has(record.id) : false}
                  aria-label={`选择 ${formatDateTime(record.created_at)} 的预测记录`}
                  onChange={() => record.id !== undefined && onToggle(record.id)}
                />
                <div className="history-item">
                  <div className="history-record-top">
                    <div className="history-header">
                      <span className="history-date">{formatDateTime(record.created_at)}</span>
                      <span className={`history-risk-badge ${getRiskToneClass(record.risk_level)}`}>
                        {formatRiskLevelLabel(record.risk_level)} ({formatRiskProbability(record.risk_probability, '0.0%')})
                      </span>
                    </div>
                    <div className="history-tags">
                      <span>7天风险预测</span>
                      <span>{getHistoryTrendText(record.bp_forecast)}</span>
                    </div>
                  </div>
                  <div className="history-record-actions">
                    <button type="button" className="btn btn-sm btn-ghost" onClick={() => onOpenDetail(record)}>
                      <Eye size={14} /> 详情
                    </button>
                    <button type="button" className="btn btn-sm btn-ghost history-delete-btn" onClick={() => record.id !== undefined && onDelete(record.id)}>
                      <Trash2 size={14} /> 删除
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
          <Pagination page={page} totalPages={totalPages} onChange={onPageChange} />
        </>
      )}
    </section>
  )
}
