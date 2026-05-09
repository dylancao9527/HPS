import {
  PredictionGovernanceOverview,
  PredictionAuditTable,
  PredictionAuditDetailCard,
} from '@/features/admin'
import { usePredictionGovernanceData } from '@/features/admin/hooks/usePredictionGovernanceData'
import { useFeedback } from '@/hooks/useFeedback'

export default function AdminPredictionGovernancePage() {
  const { showToast } = useFeedback()
  const {
    detail,
    detailLoading,
    filterChips,
    filters,
    handleExport,
    handleFilterChange,
    page,
    records,
    selectedPredictionId,
    setPage,
    setSelectedPredictionId,
    summary,
    summaryLoading,
    tableLoading,
    totalPages,
  } = usePredictionGovernanceData({ showToast })

  return (
    <div className="page-shell">
      <header className="page-header">
        <div className="page-header-main">
          <span className="page-eyebrow">Admin governance</span>
          <h1 className="page-title">预测结果治理</h1>
          <p className="page-desc">集中查看预测结果治理摘要、异常筛查和单条明细，帮助管理员快速定位需要优先查看的预测记录。</p>
        </div>
        {filterChips.length > 0 && (
          <div className="page-meta-list" aria-label="当前筛选">
            {filterChips.map((chip) => <span key={chip} className="page-meta-chip">{chip}</span>)}
          </div>
        )}
      </header>

      <section className="page-section" aria-labelledby="admin-governance-overview-title">
        <div className="page-section-heading">
          <div>
            <h2 id="admin-governance-overview-title" className="page-section-title">治理摘要</h2>
            <p className="page-section-desc">先看全量分布和异常计数，再进入逐条治理记录。</p>
          </div>
        </div>
        <PredictionGovernanceOverview summary={summary} loading={summaryLoading} />
      </section>

      <section className="page-section" aria-labelledby="admin-governance-audit-title">
        <div className="page-section-heading">
          <div>
            <h2 id="admin-governance-audit-title" className="page-section-title">治理记录</h2>
            <p className="page-section-desc">支持风险、置信度、异常状态和异常类型筛选，并可导出当前筛选结果。</p>
          </div>
        </div>
        <PredictionAuditTable
          records={records}
          page={page}
          totalPages={totalPages}
          filters={filters}
          loading={tableLoading}
          selectedPredictionId={selectedPredictionId}
          onPageChange={setPage}
          onFilterChange={handleFilterChange}
          onSelectPrediction={setSelectedPredictionId}
          onExport={handleExport}
        />
      </section>

      <section className="page-section" aria-labelledby="admin-governance-detail-title">
        <div className="page-section-heading">
          <div>
            <h2 id="admin-governance-detail-title" className="page-section-title">治理明细</h2>
            <p className="page-section-desc">展示输入快照、融合元数据、预测点摘要、置信度原因和建议列表。</p>
          </div>
        </div>
        <PredictionAuditDetailCard detail={selectedPredictionId ? detail : null} loading={detailLoading} />
      </section>
    </div>
  )
}
