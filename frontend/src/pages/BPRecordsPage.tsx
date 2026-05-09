import UserPageTabs from '@/components/UserPageTabs'
import BPRecordEntryPanel from '@/features/bp-records/components/BPRecordEntryPanel'
import BPRecordListPanel from '@/features/bp-records/components/BPRecordListPanel'
import BPRecordSummaryPanel from '@/features/bp-records/components/BPRecordSummaryPanel'
import useBPRecordsPage from '@/features/bp-records/hooks/useBPRecordsPage'
import { useFeedback } from '@/hooks/useFeedback'

const pageTabs = [
  { key: 'entry', label: '快捷录入' },
  { key: 'list', label: '记录列表' },
  { key: 'summary', label: '统计摘要' },
]

const pageTabIdPrefix = 'bp-records-page'

export default function BPRecordsPage() {
  const { confirm, showToast } = useFeedback()
  const {
    records,
    loading,
    page,
    totalPages,
    totalRecords,
    perPage,
    activeTab,
    setPage,
    setPerPage,
    setActiveTab,
    handleAdd,
    handleDelete,
    handleBatchDelete,
  } = useBPRecordsPage({ confirm, showToast })

  return (
    <div className="page-shell">
      <header className="page-header">
        <div className="page-header-main">
          <span className="page-eyebrow">Blood pressure records</span>
          <h1 className="page-title">血压记录</h1>
          <p className="page-desc">将记录录入、浏览和批量处理拆分为清晰层次，便于快速补录与持续追踪。</p>
        </div>
        <div className="page-meta-list" aria-label="记录摘要">
          <span className="page-meta-chip">当前第 {page} 页</span>
          <span className="page-meta-chip">共 {totalRecords} 条记录</span>
        </div>
      </header>

      <section className="card secondary-page-shell" aria-label="记录页面内容">
        <UserPageTabs
          tabs={pageTabs}
          activeKey={activeTab}
          onChange={setActiveTab}
          idPrefix={pageTabIdPrefix}
          focusOnActiveKeyChange
        />

        <div className="secondary-page-panel">
          <div
            id={`${pageTabIdPrefix}-panel-entry`}
            className="secondary-page-stack"
            role="tabpanel"
            aria-labelledby={`${pageTabIdPrefix}-tab-entry`}
            hidden={activeTab !== 'entry'}
          >
            <BPRecordEntryPanel onSubmit={handleAdd} loading={loading} />
          </div>

          <div
            id={`${pageTabIdPrefix}-panel-list`}
            className="secondary-page-stack"
            role="tabpanel"
            aria-labelledby={`${pageTabIdPrefix}-tab-list`}
            hidden={activeTab !== 'list'}
          >
            <BPRecordListPanel
              records={records}
              page={page}
              totalPages={totalPages}
              totalRecords={totalRecords}
              perPage={perPage}
              onDelete={handleDelete}
              onBatchDelete={handleBatchDelete}
              onPageChange={setPage}
              onPerPageChange={(nextPerPage) => {
                setPage(1)
                setPerPage(nextPerPage)
              }}
            />
          </div>

          <div
            id={`${pageTabIdPrefix}-panel-summary`}
            className="secondary-page-stack"
            role="tabpanel"
            aria-labelledby={`${pageTabIdPrefix}-tab-summary`}
            hidden={activeTab !== 'summary'}
          >
            <BPRecordSummaryPanel
              page={page}
              totalRecords={totalRecords}
              perPage={perPage}
              totalPages={totalPages}
            />
          </div>
        </div>
      </section>
    </div>
  )
}
