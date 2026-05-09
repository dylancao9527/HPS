import { AlertTriangle, CheckCircle2, CircleAlert, LoaderCircle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Card from '@/components/Card'
import { useAuth } from '@/hooks/useAuth'
import type { BPDataStatus, PredictionResult } from '@/types/prediction'
import { getBPDataStatus, predictRisk, USER_FORECAST_DAYS } from '@/features/prediction/api/predictApi'

const RISK_FACTOR_PROFILE_PATH = '/profile?tab=risk-factors'
const RISK_FACTOR_PROFILE_BLOCK_MESSAGE = '请先完善风险因素档案'

interface PredictionFormProps {
  onResult: (result: PredictionResult) => void
  statusRefreshKey?: number
}

function getStatusPresentation(bpStatus: BPDataStatus | null) {
  switch (bpStatus?.status) {
    case 'no_data':
      return { text: '暂无血压记录', tone: 'danger', icon: CircleAlert }
    case 'insufficient':
      return {
        text: `仅 ${bpStatus?.total_days} 天数据，至少需要 ${bpStatus?.minimum_days || 3} 天`,
        tone: 'danger',
        icon: AlertTriangle,
      }
    case 'warning':
      return {
        text: `${bpStatus?.total_days} 天数据，可预测但建议达到 ${bpStatus?.recommended_days_min}~${bpStatus?.recommended_days_max} 天`,
        tone: 'warning',
        icon: AlertTriangle,
      }
    case 'recommended':
      return {
        text: `${bpStatus?.total_days} 天数据，满足 ${bpStatus?.forecast_days} 天预测建议`,
        tone: 'success',
        icon: CheckCircle2,
      }
    default:
      return { text: '检查中...', tone: 'neutral', icon: LoaderCircle }
  }
}

function isRiskFactorProfileBlock(error: string) {
  return error.includes(RISK_FACTOR_PROFILE_BLOCK_MESSAGE)
}

interface PredictionReadinessCardProps {
  profileReady: boolean
  bpReady: boolean
  bpStatus: BPDataStatus | null
  statusPresentation: ReturnType<typeof getStatusPresentation>
  onProfileClick: () => void
  onRecordsClick: () => void
}

function PredictionReadinessCard({
  profileReady,
  bpReady,
  bpStatus,
  statusPresentation,
  onProfileClick,
  onRecordsClick,
}: PredictionReadinessCardProps) {
  const StatusIcon = statusPresentation.icon

  return (
    <Card title="预测准备" className="prediction-section prediction-readiness-card" titleAs="h2">
      <div className="summary-grid prediction-readiness-grid">
        <div className={`summary-item prediction-readiness-item prediction-readiness-item--${profileReady ? 'success' : 'danger'}`}>
          <span className="summary-label">风险因素档案</span>
          <span className="summary-value">{profileReady ? '已完成' : '待完善'}</span>
          {!profileReady && (
            <button type="button" className="btn btn-primary btn-sm" onClick={onProfileClick}>
              前往填写
            </button>
          )}
        </div>

        <div className={`summary-item prediction-readiness-item prediction-readiness-item--${statusPresentation.tone}`}>
          <span className="summary-label">血压记录</span>
          <span className="prediction-status-inline">
            <StatusIcon className={`prediction-status-icon ${statusPresentation.tone === 'neutral' ? 'is-spinning' : ''}`} aria-hidden="true" />
            <span className="summary-value">{statusPresentation.text}</span>
          </span>
          {bpStatus && <span className="prediction-status-meta">共 {bpStatus.total_records} 条记录</span>}
          {!bpReady && bpStatus?.status !== undefined && (
            <button type="button" className="btn btn-primary btn-sm" onClick={onRecordsClick}>
              补充记录
            </button>
          )}
        </div>

        <div className="summary-item prediction-readiness-item prediction-readiness-item--success">
          <span className="summary-label">预测能力</span>
          <span className="summary-value">未来 {USER_FORECAST_DAYS} 天风险预测</span>
          <span className="prediction-status-meta">无需选择周期</span>
        </div>
      </div>

      {bpStatus?.meets_minimum && !bpStatus.meets_recommended && (
        <p className="prediction-supporting-text prediction-supporting-text--warning">
          当前可预测；继续补充 {bpStatus.recommended_days_min}~{bpStatus.recommended_days_max} 天记录后，趋势会更稳定。
        </p>
      )}

      <p className="prediction-supporting-text">
        系统会基于历史血压与风险因素档案生成未来7天风险摘要，帮助您安排记录和复测。
      </p>
    </Card>
  )
}

function PredictionProfileBlockNotice({
  message,
  onProfileClick,
}: {
  message: string
  onProfileClick: () => void
}) {
  return (
    <div className="prediction-block-notice" role="alert">
      <AlertTriangle className="prediction-block-icon" aria-hidden="true" />
      <div className="prediction-block-copy">
        <strong>{message}</strong>
        <p>完善后再回到这里生成 7 天风险预测。</p>
      </div>
      <button type="button" className="btn btn-primary btn-sm" onClick={onProfileClick}>
        前往风险因素档案
      </button>
    </div>
  )
}

export default function PredictionForm({ onResult, statusRefreshKey = 0 }: PredictionFormProps) {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [bpStatus, setBpStatus] = useState<BPDataStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    ;(async () => {
      try {
        const data = await getBPDataStatus()
        if (!active) return
        setBpStatus(data)
      } catch {
        if (!active) return
      }
    })()

    return () => {
      active = false
    }
  }, [statusRefreshKey])

  const profileReady = user?.profile_complete
  const bpReady = bpStatus?.meets_minimum
  const statusPresentation = getStatusPresentation(bpStatus)
  const goToRiskFactorProfile = () => navigate(RISK_FACTOR_PROFILE_PATH)

  const handlePredict = async () => {
    setLoading(true)
    setError('')

    try {
      const data = await predictRisk()
      onResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '预测失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="prediction-page">
      <PredictionReadinessCard
        profileReady={Boolean(profileReady)}
        bpReady={Boolean(bpReady)}
        bpStatus={bpStatus}
        statusPresentation={statusPresentation}
        onProfileClick={goToRiskFactorProfile}
        onRecordsClick={() => navigate('/bp-records')}
      />

      {error && (
        isRiskFactorProfileBlock(error)
          ? <PredictionProfileBlockNotice message={error} onProfileClick={goToRiskFactorProfile} />
          : <div className="error-msg" role="alert">{error}</div>
      )}

      <div className="prediction-actions">
        <button
          type="button"
          className="btn btn-primary btn-block btn-lg"
          onClick={handlePredict}
          disabled={loading || !profileReady || !bpReady}
        >
          {loading ? '正在获取预测结果...' : '开始预测'}
        </button>

        {loading && (
          <p className="prediction-loading-text">
            系统正在生成未来7天风险预测，请稍候。
          </p>
        )}
      </div>
    </div>
  )
}
