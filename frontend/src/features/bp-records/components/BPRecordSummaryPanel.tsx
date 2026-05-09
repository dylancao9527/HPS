interface BPRecordSummaryPanelProps {
  page: number
  totalRecords: number
  perPage: number
  totalPages: number
}

export default function BPRecordSummaryPanel({
  page,
  totalRecords,
  perPage,
  totalPages,
}: BPRecordSummaryPanelProps) {
  return (
    <section className="page-section" aria-labelledby="bp-record-summary-title">
      <div className="page-section-heading">
        <div>
          <h2 id="bp-record-summary-title" className="page-section-title">
            统计摘要
          </h2>
          <p className="page-section-desc">
            快速查看当前分页规模与整理节奏，决定是继续录入还是回到列表处理历史记录。
          </p>
        </div>
      </div>

      <div className="secondary-page-summary-grid">
        <article className="secondary-page-summary-card">
          <span className="secondary-page-summary-label">当前页码</span>
          <strong className="secondary-page-summary-value">{page}</strong>
          <p className="secondary-page-summary-note">适合继续补录当天或最近几天的数据。</p>
        </article>
        <article className="secondary-page-summary-card">
          <span className="secondary-page-summary-label">总记录数</span>
          <strong className="secondary-page-summary-value">{totalRecords}</strong>
          <p className="secondary-page-summary-note">回到记录列表可继续筛选、删除或检查缺失项。</p>
        </article>
        <article className="secondary-page-summary-card">
          <span className="secondary-page-summary-label">每页展示</span>
          <strong className="secondary-page-summary-value">{perPage}</strong>
          <p className="secondary-page-summary-note">调整分页大小，平衡浏览密度与批量操作效率。</p>
        </article>
        <article className="secondary-page-summary-card">
          <span className="secondary-page-summary-label">总页数</span>
          <strong className="secondary-page-summary-value">{totalPages}</strong>
          <p className="secondary-page-summary-note">记录规模增大时，优先在列表页进行集中整理。</p>
        </article>
      </div>
    </section>
  )
}
