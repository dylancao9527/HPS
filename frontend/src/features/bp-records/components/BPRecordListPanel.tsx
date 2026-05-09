import Pagination from '@/components/Pagination'
import type { BPRecord } from '@/features/bp-records/types'
import BPRecordTable from '@/features/bp-records/components/BPRecordTable'

interface BPRecordListPanelProps {
  records: BPRecord[]
  page: number
  totalPages: number
  totalRecords: number
  perPage: number
  onDelete: (id: number) => void | Promise<void>
  onBatchDelete: (ids: number[]) => Promise<void>
  onPageChange: (page: number) => void
  onPerPageChange: (perPage: number) => void
}

export default function BPRecordListPanel({
  records,
  page,
  totalPages,
  totalRecords,
  perPage,
  onDelete,
  onBatchDelete,
  onPageChange,
  onPerPageChange,
}: BPRecordListPanelProps) {
  return (
    <section className="page-section" aria-labelledby="bp-record-list-title">
      <div className="page-toolbar card records-toolbar">
        <div className="page-toolbar-group">
          <h2 id="bp-record-list-title" className="page-section-title">
            记录列表
          </h2>
          <span className="page-toolbar-meta">分页与批量删除在同一操作带完成</span>
        </div>
        <div className="records-toolbar-group">
          <span className="records-toolbar-label">每页</span>
          <select
            value={perPage}
            onChange={(event) => onPerPageChange(Number(event.target.value))}
          >
            <option value={5}>5 条</option>
            <option value={10}>10 条</option>
            <option value={20}>20 条</option>
            <option value={50}>50 条</option>
          </select>
          <span className="records-toolbar-meta">共 {totalRecords} 条</span>
        </div>
      </div>

      <BPRecordTable records={records} onDelete={onDelete} onBatchDelete={onBatchDelete} />
      <Pagination page={page} totalPages={totalPages} onChange={onPageChange} />
    </section>
  )
}
