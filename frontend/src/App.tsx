import type * as React from 'react'
import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/hooks/useAuth'
import { ThemeProvider } from '@/hooks/useTheme'
import { FeedbackProvider } from '@/hooks/useFeedback'

const Layout = lazy(() => import('@/components/Layout'))
const AdminLayout = lazy(() => import('@/components/AdminLayout'))
const LoginPage = lazy(() => import('@/pages/LoginPage'))
const RegisterPage = lazy(() => import('@/pages/RegisterPage'))
const HomePage = lazy(() => import('@/pages/HomePage'))
const PredictionPage = lazy(() => import('@/pages/PredictionPage'))
const BPRecordsPage = lazy(() => import('@/pages/BPRecordsPage'))
const ProfilePage = lazy(() => import('@/pages/ProfilePage'))
const HistoryPage = lazy(() => import('@/pages/HistoryPage'))
const WeeklyReportPage = lazy(() => import('@/pages/WeeklyReportPage'))
const AdminOverviewPage = lazy(() => import('@/pages/AdminOverviewPage'))
const AdminUsersPage = lazy(() => import('@/pages/AdminUsersPage'))
const AdminExportPage = lazy(() => import('@/pages/AdminExportPage'))
const AdminPredictionGovernancePage = lazy(
  () => import('@/pages/AdminPredictionGovernancePage'),
)

function RouteLoadingState({ label = '正在加载页面…' }: { label?: string }) {
  return (
    <div className="route-loading-state" role="status" aria-live="polite">
      <div className="spinner" />
      <span className="route-loading-text">{label}</span>
    </div>
  )
}

function withRouteLoading(element: React.ReactNode) {
  return <Suspense fallback={<RouteLoadingState />}>{element}</Suspense>
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <RouteLoadingState label="正在加载页面权限…" />
  if (!user) return <Navigate to="/login" replace />
  // 管理员登录后直接跳转到 /admin，不能使用普通用户功能
  if (user.role === 'admin') return <Navigate to="/admin" replace />
  return children
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <RouteLoadingState label="正在加载页面权限…" />
  if (!user) return <Navigate to="/admin/login" replace />
  if (user.role !== 'admin') return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <FeedbackProvider>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={withRouteLoading(<LoginPage role="user" />)} />
              <Route path="/register" element={withRouteLoading(<RegisterPage />)} />
              <Route path="/admin/login" element={withRouteLoading(<LoginPage role="admin" />)} />
              {/* 普通用户布局（admin 不能访问） */}
              <Route path="/" element={
                <ProtectedRoute>{withRouteLoading(<Layout />)}</ProtectedRoute>
              }>
                <Route index element={withRouteLoading(<HomePage />)} />
                <Route path="predict" element={withRouteLoading(<PredictionPage />)} />
                <Route path="bp-records" element={withRouteLoading(<BPRecordsPage />)} />
                <Route path="weekly-report" element={withRouteLoading(<WeeklyReportPage />)} />
                <Route path="profile" element={withRouteLoading(<ProfilePage />)} />
                <Route path="history" element={withRouteLoading(<HistoryPage />)} />
              </Route>
              {/* 管理员专属布局 */}
              <Route path="/admin" element={
                <AdminRoute>{withRouteLoading(<AdminLayout />)}</AdminRoute>
              }>
                <Route index element={withRouteLoading(<AdminOverviewPage />)} />
                <Route path="users" element={withRouteLoading(<AdminUsersPage />)} />
                <Route path="governance" element={withRouteLoading(<AdminPredictionGovernancePage />)} />
                <Route path="export" element={withRouteLoading(<AdminExportPage />)} />
              </Route>
            </Routes>
          </AuthProvider>
        </FeedbackProvider>
      </ThemeProvider>
    </BrowserRouter>
  )
}
