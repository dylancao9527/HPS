import { useEffect, useMemo, useState } from 'react'
import type { ToastType } from '@/hooks/useFeedback'
import type {
  PredictionAuditDetail,
  PredictionAuditRecord,
  PredictionGovernanceSummary,
} from '@/types/admin'
import {
  getPredictionAuditDetail,
  getPredictionGovernanceSummary,
  listPredictionAudits,
} from '@/features/admin/api/adminApi'
import {
  predictionGovernanceExportTask,
  runAdminExport,
} from '@/features/admin/exportDownloads'
import {
  DEFAULT_PREDICTION_AUDIT_FILTERS,
  buildPredictionAuditFilterChips,
  normalizePredictionAuditFilters,
  resolveSelectedPredictionId,
} from '@/features/admin/governanceSession'
import type { PredictionAuditFilters } from '@/features/admin/governanceSession'

interface UsePredictionGovernanceDataOptions {
  showToast: (message: string, type?: ToastType, duration?: number) => void
}

export function usePredictionGovernanceData({ showToast }: UsePredictionGovernanceDataOptions) {
  const [summary, setSummary] = useState<PredictionGovernanceSummary | null>(null)
  const [summaryLoading, setSummaryLoading] = useState(true)

  const [filters, setFilters] = useState<PredictionAuditFilters>(DEFAULT_PREDICTION_AUDIT_FILTERS)

  const [page, setPage] = useState(1)
  const [records, setRecords] = useState<PredictionAuditRecord[]>([])
  const [totalPages, setTotalPages] = useState(1)
  const [tableLoading, setTableLoading] = useState(true)

  const [selectedPredictionId, setSelectedPredictionId] = useState<number | string | null>(null)
  const [detail, setDetail] = useState<PredictionAuditDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)

  useEffect(() => {
    let active = true

    ;(async () => {
      setSummaryLoading(true)
      try {
        const data = await getPredictionGovernanceSummary()
        if (!active) return
        setSummary(data)
      } catch (error) {
        if (!active) return
        const message = error instanceof Error ? error.message : '获取治理摘要失败'
        showToast(message || '获取治理摘要失败', 'error')
      } finally {
        if (active) setSummaryLoading(false)
      }
    })()

    return () => {
      active = false
    }
  }, [showToast])

  useEffect(() => {
    let active = true

    ;(async () => {
      setTableLoading(true)
      try {
        const data = await listPredictionAudits({
          page,
          perPage: 20,
          filters: normalizePredictionAuditFilters(filters),
        })
        if (!active) return

        const nextRecords = data.records
        setRecords(nextRecords)
        setTotalPages(data.pages)

        setSelectedPredictionId((prev) => resolveSelectedPredictionId(nextRecords, prev))
      } catch (error) {
        if (!active) return
        setRecords([])
        setTotalPages(1)
        setSelectedPredictionId(null)
        const message = error instanceof Error ? error.message : '获取治理记录失败'
        showToast(message || '获取治理记录失败', 'error')
      } finally {
        if (active) setTableLoading(false)
      }
    })()

    return () => {
      active = false
    }
  }, [filters, page, showToast])

  useEffect(() => {
    if (!selectedPredictionId) {
      return
    }

    let active = true

    ;(async () => {
      setDetailLoading(true)
      try {
        const data = await getPredictionAuditDetail(selectedPredictionId)
        if (!active) return
        setDetail(data)
      } catch (error) {
        if (!active) return
        setDetail(null)
        const message = error instanceof Error ? error.message : '获取治理明细失败'
        showToast(message || '获取治理明细失败', 'error')
      } finally {
        if (active) setDetailLoading(false)
      }
    })()

    return () => {
      active = false
    }
  }, [selectedPredictionId, showToast])

  const filterChips = useMemo(() => buildPredictionAuditFilterChips(filters), [filters])

  const handleFilterChange = (key: keyof PredictionAuditFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
    setPage(1)
  }

  const handleExport = async () => {
    try {
      await runAdminExport(predictionGovernanceExportTask(normalizePredictionAuditFilters(filters)))
      showToast('预测结果治理导出成功', 'success')
    } catch (error) {
      const message = error instanceof Error ? error.message : '导出失败'
      showToast(message || '导出失败', 'error')
    }
  }

  return {
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
  }
}
