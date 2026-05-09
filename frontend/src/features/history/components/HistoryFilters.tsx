import { Search, Trash2 } from 'lucide-react'

interface HistoryFiltersProps {
  startDate: string
  endDate: string
  hasDateFilter: boolean
  allSelected: boolean
  selectedCount: number
  onStartDateChange: (value: string) => void
  onEndDateChange: (value: string) => void
  onClearFilters: () => void
  onToggleAll: () => void
  onBatchDelete: () => void
  onClearSelection: () => void
}

export default function HistoryFilters({
  startDate,
  endDate,
  hasDateFilter,
  allSelected,
  selectedCount,
  onStartDateChange,
  onEndDateChange,
  onClearFilters,
  onToggleAll,
  onBatchDelete,
  onClearSelection,
}: HistoryFiltersProps) {
  return (
    <section className="page-section" aria-labelledby="history-filter-title">
      <div className="page-toolbar card history-toolbar">
        <div className="page-toolbar-group">
          <div>
            <h2 id="history-filter-title" className="page-section-title">筛选与批量操作</h2>
            <p className="page-section-desc">按日期缩小范围，再选择记录查看详情或执行批量删除。</p>
          </div>
        </div>
        <div className="history-toolbar-actions">
          <div className="history-filter-controls" role="group" aria-label="历史日期筛选">
            <span className="history-filter-icon" aria-hidden="true"><Search size={16} /></span>
            <label className="history-filter-field">
              <span>从</span>
              <input type="date" value={startDate} onChange={(event) => onStartDateChange(event.target.value)} />
            </label>
            <label className="history-filter-field">
              <span>至</span>
              <input type="date" value={endDate} onChange={(event) => onEndDateChange(event.target.value)} />
            </label>
            {hasDateFilter && (
              <button type="button" className="btn btn-sm btn-ghost" onClick={onClearFilters}>
                清除筛选
              </button>
            )}
          </div>
          <label className="history-select-toggle">
            <input type="checkbox" checked={allSelected} onChange={onToggleAll} />
            <span>全选本页</span>
          </label>
        </div>
      </div>

      {selectedCount > 0 && (
        <div className="batch-bar" role="status" aria-live="polite">
          <span>已选择 <span className="batch-count">{selectedCount}</span> 条记录</span>
          <button type="button" className="btn btn-danger btn-sm" onClick={onBatchDelete}>
            <Trash2 size={14} /> 批量删除
          </button>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClearSelection}>
            取消选择
          </button>
        </div>
      )}
    </section>
  )
}