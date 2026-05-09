import { useCallback, useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import UserPageTabs from '@/components/UserPageTabs'
import { ProfileForm } from '@/features/profile'
import PredictionTrendChart from '@/features/profile/components/PredictionTrendChart'
import WeeklyReportPanel from '@/features/profile/components/WeeklyReportPanel'
import { getWeeklyReport, type WeeklyReportSummary } from '@/features/weekly-report'

const pageTabs = [
  { key: 'profile', label: '基本资料' },
  { key: 'risk-factors', label: '风险因素档案' },
  { key: 'trend', label: '健康趋势' },
]

const pageTabIdPrefix = 'profile-page'
const defaultProfileTab = 'profile'

function getProfileTabFromSearchParams(searchParams: URLSearchParams) {
  const requestedTab = searchParams.get('tab') || defaultProfileTab
  return pageTabs.some((tab) => tab.key === requestedTab) ? requestedTab : defaultProfileTab
}

export default function ProfilePage() {
  const mountedRef = useRef(true)
  const [searchParams] = useSearchParams()
  const [activeTab, setActiveTab] = useState(() => getProfileTabFromSearchParams(searchParams))
  const [weeklyReportLoading, setWeeklyReportLoading] = useState(false)
  const [weeklyReportError, setWeeklyReportError] = useState('')
  const [weeklyReportData, setWeeklyReportData] = useState<WeeklyReportSummary | null>(null)

  const loadWeeklyReport = useCallback(async (isActive: () => boolean = () => true) => {
    setWeeklyReportLoading(true)
    setWeeklyReportError('')

    try {
      const data = await getWeeklyReport()
      if (!isActive()) return
      setWeeklyReportData(data)
    } catch (error) {
      if (!isActive()) return
      setWeeklyReportError(error instanceof Error ? error.message : '周健康报告加载失败，请稍后重试')
    } finally {
      if (isActive()) {
        setWeeklyReportLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    mountedRef.current = true

    return () => {
      mountedRef.current = false
    }
  }, [])

  useEffect(() => {
    setActiveTab(getProfileTabFromSearchParams(searchParams))
  }, [searchParams])

  useEffect(() => {
    if (activeTab !== 'trend' || weeklyReportData || weeklyReportError) return

    let active = true
    void loadWeeklyReport(() => active && mountedRef.current)

    return () => {
      active = false
    }
  }, [activeTab, weeklyReportData, weeklyReportError, loadWeeklyReport])

  return (
    <div className="page-shell">
      <header className="page-header">
        <div className="page-header-main">
          <span className="page-eyebrow">Profile workspace</span>
          <h1 className="page-title">个人中心</h1>
          <p className="page-desc">统一维护账号、风险因素档案、反馈信息与密码设置，并在同一页面持续观察风险趋势变化。</p>
        </div>
      </header>

      <section className="card secondary-page-shell" aria-label="个人中心页面内容">
        <UserPageTabs
          tabs={pageTabs}
          activeKey={activeTab}
          onChange={setActiveTab}
          idPrefix={pageTabIdPrefix}
        />

        <div className="secondary-page-panel">
          <div
            id={`${pageTabIdPrefix}-panel-profile`}
            className="secondary-page-stack"
            role="tabpanel"
            aria-labelledby={`${pageTabIdPrefix}-tab-profile`}
            hidden={activeTab !== 'profile'}
          >
            <section className="page-section" aria-labelledby="profile-maintenance-title">
              <div className="page-section-heading">
                <div>
                  <h2 id="profile-maintenance-title" className="page-section-title">
                    资料维护
                  </h2>
                  <p className="page-section-desc">
                    账号信息、其他健康信息和密码设置保留独立责任边界，风险因素档案在单独标签页维护。
                  </p>
                </div>
              </div>
              <ProfileForm sections={['account', 'feedback', 'password']} />
            </section>
          </div>

          <div
            id={`${pageTabIdPrefix}-panel-risk-factors`}
            className="secondary-page-stack"
            role="tabpanel"
            aria-labelledby={`${pageTabIdPrefix}-tab-risk-factors`}
            hidden={activeTab !== 'risk-factors'}
          >
            <section className="page-section" aria-labelledby="risk-factors-profile-title">
              <div className="page-section-heading">
                <div>
                  <h2 id="risk-factors-profile-title" className="page-section-title">
                    风险因素档案
                  </h2>
                  <p className="page-section-desc">
                    维护参与 7 天风险预测的个人风险因素，诊断反馈和账号资料不会混在这里。
                  </p>
                </div>
              </div>
              <ProfileForm sections={['riskFactors']} />
            </section>
          </div>

          <div
            id={`${pageTabIdPrefix}-panel-trend`}
            className="secondary-page-stack"
            role="tabpanel"
            aria-labelledby={`${pageTabIdPrefix}-tab-trend`}
            hidden={activeTab !== 'trend'}
          >
            <section className="page-section" aria-labelledby="profile-comparison-title">
              <div className="page-section-heading">
                <div>
                  <h2 id="profile-comparison-title" className="page-section-title">
                    周健康报告
                  </h2>
                  <p className="page-section-desc">
                    固定比较最近7天与前7天，快速回顾血压、记录频率和风险概率变化。
                  </p>
                </div>
              </div>
              <WeeklyReportPanel
                loading={weeklyReportLoading}
                error={weeklyReportError}
                data={weeklyReportData}
                onRetry={() => void loadWeeklyReport(() => mountedRef.current)}
              />
            </section>

            <section className="page-section" aria-labelledby="profile-trend-title">
              <div className="page-section-heading">
                <div>
                  <h2 id="profile-trend-title" className="page-section-title">
                    健康趋势
                  </h2>
                  <p className="page-section-desc">
                    按小时、按天或按月查看历史预测的平均风险变化，帮助判断整体趋势。
                  </p>
                </div>
              </div>
              <PredictionTrendChart />
            </section>
          </div>
        </div>
      </section>
    </div>
  )
}
