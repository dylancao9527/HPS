import {
  downloadPredictionGovernanceExport,
  downloadTrainingExport,
  type PredictionAuditFilters,
} from '@/features/admin/api/adminApi'

interface AdminExportTask {
  filename: string
  load: () => Promise<Blob>
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

export async function runAdminExport(task: AdminExportTask): Promise<void> {
  const blob = await task.load()
  downloadBlob(blob, task.filename)
}

export function trainingDataExportTask(): AdminExportTask {
  return {
    filename: 'training_data_export.csv',
    load: downloadTrainingExport,
  }
}

export function predictionGovernanceExportTask(
  filters: Partial<PredictionAuditFilters>,
): AdminExportTask {
  return {
    filename: 'prediction_governance_export.csv',
    load: () => downloadPredictionGovernanceExport(filters),
  }
}
