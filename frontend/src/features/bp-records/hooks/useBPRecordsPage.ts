import { useCallback, useEffect, useState } from 'react'
import {
  batchDeleteBPRecords,
  deleteBPRecord,
  getBPRecords,
} from '@/features/bp-records/api/bpApi'
import useBPRecordWriter from '@/features/bp-records/hooks/useBPRecordWriter'
import type { BPRecord, BPRecordsResponse, CreateBPRecordInput } from '@/features/bp-records/types'

interface ConfirmOptions {
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  danger?: boolean
}

interface UseBPRecordsPageOptions {
  confirm: (options?: ConfirmOptions) => Promise<boolean>
  showToast: (message: string, type?: 'info' | 'success' | 'error', duration?: number) => void
}

function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error && error.message ? error.message : fallback
}

export default function useBPRecordsPage({ confirm, showToast }: UseBPRecordsPageOptions) {
  const [records, setRecords] = useState<BPRecord[]>([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalRecords, setTotalRecords] = useState(0)
  const [perPage, setPerPage] = useState(10)
  const [activeTab, setActiveTab] = useState('entry')

  const applyResponse = useCallback((data: BPRecordsResponse) => {
    setRecords(data.records)
    setTotalPages(data.pages)
    setTotalRecords(data.total)
  }, [])

  const fetchRecords = useCallback(
    async (targetPage: number = page): Promise<void> => {
      try {
        const data = await getBPRecords(targetPage, perPage)
        applyResponse(data)
      } catch (error) {
        showToast(getErrorMessage(error, '获取血压记录失败'), 'error')
      }
    },
    [applyResponse, page, perPage, showToast],
  )

  const writer = useBPRecordWriter({
    fallbackError: '添加失败',
    successMessage: '血压记录已添加',
    showErrorToast: true,
    showToast,
    throwOnError: true,
    onSuccess: async () => {
      await fetchRecords(1)
      setPage(1)
      setActiveTab('list')
    },
  })

  useEffect(() => {
    let active = true

    ;(async () => {
      try {
        const data = await getBPRecords(page, perPage)
        if (!active) return
        applyResponse(data)
      } catch (error) {
        if (!active) return
        showToast(getErrorMessage(error, '获取血压记录失败'), 'error')
      }
    })()

    return () => {
      active = false
    }
  }, [applyResponse, page, perPage, showToast])

  const handleAdd = useCallback(
    async (formData: CreateBPRecordInput): Promise<void> => {
      await writer.submit(formData)
    },
    [writer],
  )

  const handleDelete = useCallback(
    async (id: number): Promise<void> => {
      const ok = await confirm({
        title: '删除血压记录',
        message: '确定删除此记录吗？',
        confirmText: '确认删除',
        danger: true,
      })
      if (!ok) return

      try {
        await deleteBPRecord(id)
        await fetchRecords()
        showToast('删除成功', 'success')
      } catch (error) {
        showToast(getErrorMessage(error, '删除失败'), 'error')
      }
    },
    [confirm, fetchRecords, showToast],
  )

  const handleBatchDelete = useCallback(
    async (ids: number[]): Promise<void> => {
      await batchDeleteBPRecords(ids)
      await fetchRecords()
    },
    [fetchRecords],
  )

  return {
    records,
    loading: writer.loading,
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
  }
}
