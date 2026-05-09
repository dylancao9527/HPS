import { useMemo, useState } from 'react'
import type { ChangeEvent, MouseEvent } from 'react'
import Card from '@/components/Card'
import { Pencil, Trash2, X } from 'lucide-react'
import { useFeedback } from '@/hooks/useFeedback'
import type { AdminUser, AdminUserUpdateInput } from '@/types/admin'

interface UserTableProps {
  users: AdminUser[]
  admins: AdminUser[]
  onDelete: (id: AdminUser['id']) => void | Promise<void>
  onEdit: (id: AdminUser['id'], data: AdminUserUpdateInput) => void | Promise<void>
  onBatchDelete: (ids: AdminUser['id'][]) => void | Promise<void>
}

interface EditingUser {
  id: AdminUser['id']
  username: string
  email: string
  password: string
}

export default function UserTable({ users, admins, onDelete, onEdit, onBatchDelete }: UserTableProps) {
  const [editing, setEditing] = useState<EditingUser | null>(null)
  const [selected, setSelected] = useState<Set<AdminUser['id']>>(new Set())
  const { confirm, showToast } = useFeedback()

  const currentIds = useMemo(
    () => new Set(users.map((user) => user.id)),
    [users],
  )
  const visibleSelected = useMemo(
    () => new Set([...selected].filter((id) => currentIds.has(id))),
    [currentIds, selected],
  )

  if ((!users || users.length === 0) && (!admins || admins.length === 0)) {
    return <Card title="账号管理"><p className="empty-text">暂无账号。</p></Card>
  }

  const allSelected = users.length > 0 && users.every((user) => visibleSelected.has(user.id))

  const toggleAll = () => {
    if (allSelected) {
      setSelected(new Set())
    } else {
      setSelected(new Set(users.map((user) => user.id)))
    }
  }

  const toggle = (id: AdminUser['id']) => {
    const next = new Set(visibleSelected)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelected(next)
  }

  const handleBatchDelete = async () => {
    const ok = await confirm({
      title: '批量删除用户',
      message: `确定删除选中的 ${visibleSelected.size} 个用户？此操作不可恢复。`,
      confirmText: '确认删除',
      danger: true,
    })
    if (!ok) return

    try {
      await onBatchDelete([...visibleSelected])
      setSelected(new Set())
      showToast('批量删除成功', 'success')
    } catch (error) {
      const message = error instanceof Error ? error.message : '批量删除失败'
      showToast(message || '批量删除失败', 'error')
    }
  }

  const handleEditSubmit = async () => {
    if (!editing) return
    try {
      await onEdit(editing.id, { password: editing.password })
      setEditing(null)
      showToast('密码修改成功', 'success')
    } catch (error) {
      const message = error instanceof Error ? error.message : '密码修改失败'
      showToast(message || '密码修改失败', 'error')
    }
  }

  const renderAccountTable = (
    rows: AdminUser[],
    {
      title,
      emptyText,
      selectable,
    }: {
      title: string
      emptyText: string
      selectable: boolean
    },
  ) => (
    <Card title={title} className="admin-account-table-card">
      {selectable && visibleSelected.size > 0 && (
        <div className="batch-bar">
          <span>已选择 <span className="batch-count">{visibleSelected.size}</span> 个用户</span>
          <button className="btn btn-danger btn-sm" onClick={handleBatchDelete}>
            <Trash2 size={14} /> 批量删除
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => setSelected(new Set())}>
            取消选择
          </button>
        </div>
      )}
      {rows.length === 0 ? (
        <p className="empty-text">{emptyText}</p>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                {selectable && <th><input type="checkbox" checked={allSelected} onChange={toggleAll} /></th>}
                <th>ID</th>
                <th>用户名</th>
                <th>邮箱</th>
                <th>角色</th>
                {selectable && <th>年龄</th>}
                {selectable && <th>BMI</th>}
                <th>注册时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((user) => (
                <tr key={user.id}>
                  {selectable && (
                    <td>
                      <input type="checkbox" checked={visibleSelected.has(user.id)} onChange={() => toggle(user.id)} />
                    </td>
                  )}
                  <td>{user.id}</td>
                  <td>{user.username}</td>
                  <td className="user-table-email-cell">{user.email || '-'}</td>
                  <td>
                    <span className={`role-tag ${user.role}`}>
                      {user.role === 'admin' ? '管理员' : '用户'}
                    </span>
                  </td>
                  {selectable && <td>{user.age ?? '-'}</td>}
                  {selectable && <td>{user.bmi ?? '-'}</td>}
                  <td>{user.created_at ? new Date(user.created_at).toLocaleDateString('zh-CN') : '-'}</td>
                  <td>
                    <div className="user-table-actions">
                      <button className="btn btn-ghost btn-sm" onClick={() => setEditing({ id: user.id, username: user.username, email: user.email || '', password: '' })} aria-label={`修改 ${user.username} 的密码`}>
                        <Pencil size={14} />
                      </button>
                      {selectable && (
                        <button className="btn btn-ghost btn-sm user-table-danger-action" onClick={() => onDelete(user.id)} aria-label={`删除 ${user.username}`}>
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  )

  return (
    <>
      <div className="admin-account-table-stack">
        {renderAccountTable(users, {
          title: '普通用户账号',
          emptyText: '当前页暂无普通用户。',
          selectable: true,
        })}
        {renderAccountTable(admins, {
          title: '管理员账号',
          emptyText: '当前页暂无管理员账号。',
          selectable: false,
        })}
      </div>

      {editing && (
        <div className="modal-overlay" onClick={() => setEditing(null)}>
          <div className="modal-content user-table-edit-modal" onClick={(event: MouseEvent<HTMLDivElement>) => event.stopPropagation()}>
            <div className="modal-header">
              <h3>修改用户密码</h3>
              <button className="modal-close" onClick={() => setEditing(null)}><X size={20} /></button>
            </div>
            <div className="form-group">
              <label>用户名</label>
              <input type="text" value={editing.username} disabled />
            </div>
            <div className="form-group">
              <label>邮箱</label>
              <input type="text" value={editing.email} disabled />
            </div>
            <div className="form-group">
              <label>新密码</label>
              <input type="password" value={editing.password} placeholder="输入新密码" onChange={(event: ChangeEvent<HTMLInputElement>) => setEditing({ ...editing, password: event.target.value })} />
              <p className="user-table-password-hint">
                密码需 8~32 位，且至少包含字母、数字、符号中的两种。
              </p>
            </div>
            <button className="btn btn-primary btn-block user-table-submit" onClick={handleEditSubmit}>
              保存
            </button>
          </div>
        </div>
      )}
    </>
  )
}
