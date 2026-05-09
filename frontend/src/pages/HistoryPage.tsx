import { useEffect, useState } from 'react'
import {
  batchDeletePredictions,
  deletePrediction,
  getPredictions,
} from '@/features/history'
import HistoryDetailPanel from '@/features/history/components/HistoryDetailPanel'
import HistoryFilters from '@/features/history/components/HistoryFilters'
import HistoryRecordList from '@/features/history/components/HistoryRecordList'
import { useFeedback } from '@/hooks/useFeedback'
import type { HistoryDetail, HistoryRecord } from '@/types/history'

export default function HistoryPage() {
  const [records, setRecords] = useState<HistoryRecord[]>([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [detail, setDetail] = useState<HistoryDetail | null>(null)
  const [selected, setSelected] = useState<Set<number | string>>(new Set())
  const { confirm, showToast } = useFeedback()

  const load = async (targetPage = page, targetStart = startDate, targetEnd = endDate) => {
    const data = await getPredictions(targetPage, targetStart, targetEnd)
    setRecords(data.records ?? [])
    setTotalPages(data.pages ?? 1)
  }

  useEffect(() => {
    let active = true
    void (async () => {
      try {
        const data = await getPredictions(page, startDate, endDate)
        if (!active) return
        setRecords(data.records ?? [])
        setTotalPages(data.pages ?? 1)
      } catch (e) {
        if (!active) return
        showToast(e instanceof Error ? e.message : '获取预测历史失败', 'error')
      }
    })()

    return () => { active = false }
  }, [page, startDate, endDate, showToast])

  const handleDelete = async (id: number | string) => {
    const ok = await confirm({
      title: '删除预测记录',
      message: '确定删除此条预测记录？',
      confirmText: '确认删除',
      danger: true,
    })
    if (!ok) return

    try {
      await deletePrediction(id)
      if (detail?.id === id) setDetail(null)
      await load()
      showToast('删除成功', 'success')
    } catch (e) {
      showToast(e instanceof Error ? e.message : '删除失败', 'error')
    }
  }

  const toggle = (id: number | string) => {
    const next = new Set(selected)
    if (next.has(id)) {
      next.delete(id)
    } else {
      next.add(id)
    }
    setSelected(next)
  }

  const allSelected = records.length > 0 && records.every((record) => selected.has(record.id ?? ''))
  const hasDateFilter = Boolean(startDate || endDate)

  const toggleAll = () => {
    if (allSelected) {
      setSelected(new Set())
    } else {
      setSelected(new Set(records.map((record) => record.id!).filter(Boolean)))
    }
  }

  const clearFilters = () => {
    setStartDate('')
    setEndDate('')
    setPage(1)
  }

  const handleBatchDelete = async () => {
    const ok = await confirm({
      title: '批量删除预测记录',
      message: `确定删除选中的 ${selected.size} 条记录？`,
      confirmText: '确认删除',
      danger: true,
    })
    if (!ok) return

    try {
      await batchDeletePredictions([...selected])
      if (detail?.id !== undefined && selected.has(detail.id)) setDetail(null)
      setSelected(new Set())
      await load()
      showToast('批量删除成功', 'success')
    } catch (e) {
      showToast(e instanceof Error ? e.message : '批量删除失败', 'error')
    }
  }

  return (
    <div className="page-shell">
      <header className="page-header">
        <div className="page-header-main">
          <span className="page-eyebrow">Prediction history</span>
          <h1 className="page-title">7天风险预测历史</h1>
          <p className="page-desc">按时间回看历史预测结果，详情面板展示用户端预测摘要、未来7天趋势和健康建议。</p>
        </div>
        <div className="page-meta-list" aria-label="历史摘要">
          <span className="page-meta-chip">当前第 {page} 页</span>
          <span className="page-meta-chip">本页 {records.length} 条记录</span>
          {hasDateFilter && <span className="page-meta-chip">已启用日期筛选</span>}
        </div>
      </header>

      <HistoryFilters
        startDate={startDate}
        endDate={endDate}
        hasDateFilter={hasDateFilter}
        allSelected={allSelected}
        selectedCount={selected.size}
        onStartDateChange={(value) => { setStartDate(value); setPage(1) }}
        onEndDateChange={(value) => { setEndDate(value); setPage(1) }}
        onClearFilters={clearFilters}
        onToggleAll={toggleAll}
        onBatchDelete={handleBatchDelete}
        onClearSelection={() => setSelected(new Set())}
      />

      <HistoryRecordList
        records={records}
        page={page}
        totalPages={totalPages}
        selected={selected}
        onToggle={toggle}
        onOpenDetail={setDetail}
        onDelete={handleDelete}
        onPageChange={setPage}
      />
      {detail && <HistoryDetailPanel detail={detail} onClose={() => setDetail(null)} />}
    </div>
  )
}
