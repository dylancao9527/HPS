import { useEffect, useMemo, useState } from 'react'
import { UserTable, getUsers, deleteUser, batchDeleteUsers, updateUser } from '@/features/admin'
import Pagination from '@/components/Pagination'
import { useFeedback } from '@/hooks/useFeedback'
import type { AdminUser, AdminUserUpdateInput } from '@/types/admin'

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [admins, setAdmins] = useState<AdminUser[]>([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const { confirm, showToast } = useFeedback()
  const roleCounts = useMemo(() => ({
    users: users.length,
    admins: admins.length,
  }), [admins.length, users.length])

  const fetchUsers = async (targetPage = page) => {
    try {
      const data = await getUsers(targetPage)
      setUsers(data.users)
      setAdmins(data.admins ?? [])
      setTotalPages(data.pages)
    } catch (error) {
      const message = error instanceof Error ? error.message : '获取用户列表失败'
      showToast(message || '获取用户列表失败', 'error')
    }
  }

  useEffect(() => {
    let active = true
    ;(async () => {
      try {
        const data = await getUsers(page)
        if (!active) return
        setUsers(data.users)
        setAdmins(data.admins ?? [])
        setTotalPages(data.pages)
      } catch (error) {
        if (!active) return
        const message = error instanceof Error ? error.message : '获取用户列表失败'
        showToast(message || '获取用户列表失败', 'error')
      }
    })()
    return () => {
      active = false
    }
  }, [page, showToast])

  const handleDelete = async (id: AdminUser['id']) => {
    const ok = await confirm({
      title: '删除用户',
      message: '确定删除此用户？其所有数据将被删除。',
      confirmText: '确认删除',
      danger: true,
    })
    if (!ok) return

    try {
      await deleteUser(id)
      await fetchUsers()
      showToast('删除成功', 'success')
    } catch (error) {
      const message = error instanceof Error ? error.message : '删除失败'
      showToast(message || '删除失败', 'error')
    }
  }

  const handleBatchDelete = async (ids: AdminUser['id'][]) => {
    await batchDeleteUsers(ids)
    await fetchUsers()
  }

  const handleEdit = async (id: AdminUser['id'], data: AdminUserUpdateInput) => {
    await updateUser(id, data)
    await fetchUsers()
  }

  return (
    <div className="page-shell">
      <header className="page-header">
        <div className="page-header-main">
          <span className="page-eyebrow">Admin users</span>
          <h1 className="page-title">用户管理</h1>
          <p className="page-desc">普通用户与管理员账号分开检视，密码维护和危险操作保留清晰的权限层次。</p>
        </div>
        <div className="page-meta-list" aria-label="用户统计摘要">
          <span className="page-meta-chip">当前第 {page} 页</span>
          <span className="page-meta-chip">共 {totalPages} 页</span>
          <span className="page-meta-chip">本页普通用户 {roleCounts.users}</span>
          <span className="page-meta-chip">本页管理员 {roleCounts.admins}</span>
        </div>
      </header>

      <section className="page-section" aria-labelledby="admin-users-list-title">
        <div className="page-toolbar card">
          <div className="page-toolbar-group">
            <h2 id="admin-users-list-title" className="page-section-title">账号列表</h2>
            <span className="page-toolbar-meta">普通用户支持批量删除；管理员账号仅开放密码维护。</span>
          </div>
        </div>
        <UserTable users={users} admins={admins} onDelete={handleDelete} onEdit={handleEdit} onBatchDelete={handleBatchDelete} />
        <Pagination page={page} totalPages={totalPages} onChange={setPage} />
      </section>
    </div>
  )
}
