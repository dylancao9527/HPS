import { useMemo, useState } from 'react'
import Card from '@/components/Card'
import { Trash2 } from 'lucide-react'
import { useFeedback } from '@/hooks/useFeedback'
import type { BPRecord } from '@/features/bp-records/types'

interface BPRecordTableProps {
  records: BPRecord[]
  onDelete: (id: number) => void | Promise<void>
  onBatchDelete: (ids: number[]) => Promise<void>
}

function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof Error && error.message ? error.message : fallback
}

export default function BPRecordTable({ records, onDelete, onBatchDelete }: BPRecordTableProps) {
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const { confirm, showToast } = useFeedback()

  const currentIds = useMemo(() => new Set(records.map((record) => record.id)), [records])
  const visibleSelected = useMemo(
    () => new Set([...selected].filter((id) => currentIds.has(id))),
    [currentIds, selected],
  )

  if (!records || records.length === 0) {
    return <Card title="血压记录"><p className="empty-text">暂无记录，请添加您的第一条血压数据。</p></Card>
  }

  const allSelected = records.length > 0 && records.every((record) => visibleSelected.has(record.id))

  const toggleAll = () => {
    if (allSelected) {
      setSelected(new Set())
    } else {
      setSelected(new Set(records.map((record) => record.id)))
    }
  }

  const toggle = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const handleBatchDelete = async () => {
    const ok = await confirm({
      title: '批量删除血压记录',
      message: `确定删除选中的 ${visibleSelected.size} 条记录？`,
      confirmText: '确认删除',
      danger: true,
    })
    if (!ok) return

    try {
      await onBatchDelete([...visibleSelected])
      setSelected(new Set())
      showToast('批量删除成功', 'success')
    } catch (error) {
      showToast(getErrorMessage(error, '批量删除失败'), 'error')
    }
  }

  return (
    <Card title="历史血压记录">
      {visibleSelected.size > 0 && (
        <div className="batch-bar">
          <span>已选择 <span className="batch-count">{visibleSelected.size}</span> 条记录</span>
          <button className="btn btn-danger btn-sm" onClick={handleBatchDelete}>
            <Trash2 size={14} /> 批量删除
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => setSelected(new Set())}>
            取消选择
          </button>
        </div>
      )}
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th><input type="checkbox" checked={allSelected} onChange={toggleAll} /></th>
              <th>测量时间</th>
              <th>收缩压</th>
              <th>舒张压</th>
              <th>心率</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record) => (
              <tr key={record.id}>
                <td><input type="checkbox" checked={visibleSelected.has(record.id)} onChange={() => toggle(record.id)} /></td>
                <td>{new Date(record.recorded_at).toLocaleString('zh-CN')}</td>
                <td className={record.systolic_bp >= 140 ? 'text-danger' : ''}>{record.systolic_bp}</td>
                <td className={record.diastolic_bp >= 90 ? 'text-danger' : ''}>{record.diastolic_bp}</td>
                <td>{record.heart_rate || '-'}</td>
                <td>
                  <button className="btn btn-ghost btn-sm" onClick={() => onDelete(record.id)}>
                    删除
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
