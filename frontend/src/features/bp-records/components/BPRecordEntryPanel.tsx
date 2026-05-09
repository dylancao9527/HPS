import type { CreateBPRecordInput } from '@/features/bp-records/types'
import BPRecordForm from '@/features/bp-records/components/BPRecordForm'

interface BPRecordEntryPanelProps {
  loading: boolean
  onSubmit: (data: CreateBPRecordInput) => void | Promise<void>
}

export default function BPRecordEntryPanel({ loading, onSubmit }: BPRecordEntryPanelProps) {
  return (
    <section className="page-section" aria-labelledby="bp-record-entry-title">
      <div className="page-section-heading">
        <div>
          <h2 id="bp-record-entry-title" className="page-section-title">
            新增记录
          </h2>
          <p className="page-section-desc">
            优先完成当天记录补录，再回到下方列表进行筛选或批量处理。
          </p>
        </div>
      </div>
      <BPRecordForm onSubmit={onSubmit} loading={loading} />
    </section>
  )
}
