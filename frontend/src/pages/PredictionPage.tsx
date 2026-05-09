import {
  PredictionChartPanel,
  PredictionForm,
  PredictionOverviewPanel,
  PredictionRecommendationPanel,
  usePredictionPageSession,
} from '@/features/prediction'
import {
  QuickBPRecordModal,
  TodayHealthTasksPanel,
} from '@/features/health-tasks'

export default function PredictionPage() {
  const session = usePredictionPageSession()
  const {
    handleReset,
    handleResult,
    healthTasks,
    isUsingMedication,
    quickRecord,
    result,
    statusRefreshKey,
    trendText,
  } = session

  return (
    <div className="page-shell page-shell--narrow">
      <header className="page-header prediction-page-header">
        <div className="page-header-main">
          <h1 className="page-title">7天风险预测</h1>
          <p className="page-desc">查看未来7天高血压风险概率、血压趋势和健康建议。结果仅供健康管理参考。</p>
        </div>
        {result && (
          <div className="page-header-actions">
            <button type="button" className="btn btn-ghost" onClick={handleReset}>
              重新预测
            </button>
          </div>
        )}
      </header>

      <TodayHealthTasksPanel
        summary={healthTasks.summary}
        loading={healthTasks.loading}
        error={healthTasks.error}
        onRetry={healthTasks.onRetry}
        onQuickRecord={healthTasks.onQuickRecord}
      />

      <QuickBPRecordModal
        open={quickRecord.open}
        loading={quickRecord.loading}
        error={quickRecord.error}
        onClose={quickRecord.onClose}
        onSubmit={quickRecord.onSubmit}
      />

      <section className="card prediction-page-shell" aria-label="预测操作">
        <PredictionForm onResult={handleResult} statusRefreshKey={statusRefreshKey} />
      </section>

      {result && (
        <section className="prediction-page-panel" aria-label="预测结果">
          <PredictionOverviewPanel
            result={result}
            isUsingMedication={isUsingMedication}
            trendText={trendText}
          />
          <PredictionChartPanel result={result} />
          <PredictionRecommendationPanel result={result} />
        </section>
      )}
    </div>
  )
}
