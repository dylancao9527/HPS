"""
==============================================================================
数据导出服务 (export_service.py)
==============================================================================
仅保留 LightGBM 再训练数据导出。

导出规则：
  1. 每个用户一条样本
  2. sysBP / diaBP / heartRate 使用最近 N 条真实 BP 记录均值
  3. 标签优先使用用户 diagnosis 诊断反馈，其次使用 BP 自动标注

标签来源：
  - 优先级1：诊断反馈 diagnosis='Yes' -> Risk=1, 'No' -> Risk=0
  - 优先级2：BP自动标注 >=3次 SBP>=140 或 DBP>=90 -> label=1
  - 优先级3：诊断反馈未知且有足够 BP 数据但不满足高压条件 -> label=0

空值处理：
  - totChol / glucose / BPMeds / diabetes 允许缺失
==============================================================================
"""

import csv
import io
from flask import current_app, has_app_context
from training.ml_schema import TRAINING_EXPORT_COLUMNS
from training.export_samples import load_training_export_batch

DEFAULT_RECENT_BP_AVG_COUNT = 5


def _get_recent_bp_avg_count():
    """获取导出时的最近 BP 均值窗口大小（默认 5）。"""
    recent_count = DEFAULT_RECENT_BP_AVG_COUNT

    if has_app_context():
        recent_count = current_app.config.get(
            "EXPORT_RECENT_BP_COUNT", DEFAULT_RECENT_BP_AVG_COUNT
        )

    try:
        recent_count = int(recent_count)
    except (TypeError, ValueError):
        recent_count = DEFAULT_RECENT_BP_AVG_COUNT

    return max(1, recent_count)


def export_training_csv():
    """
    导出 LightGBM 训练数据 CSV。

    标签判定逻辑：
      1. 诊断反馈 diagnosis='Yes' -> Risk=1
      2. 诊断反馈 diagnosis='No'  -> Risk=0
      3. diagnosis=None -> 看 BP 记录：
         a. >=3 条 SBP>=140 或 DBP>=90 -> label=1
         b. 否则 -> label=0（有足够 BP 数据但不满足高压条件）

    空值处理：
      - totChol/glucose/BPMeds/diabetes 缺失 → 允许留空
      - currentSmoker=0 → cigsPerDay 固定导出为 0
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(TRAINING_EXPORT_COLUMNS)

    recent_bp_avg_count = _get_recent_bp_avg_count()
    batch = load_training_export_batch(recent_bp_avg_count)
    exportable_samples = batch.samples

    for sample in exportable_samples:
        row = sample.row
        writer.writerow([row.get(col) for col in TRAINING_EXPORT_COLUMNS])

    exported = len(exportable_samples)
    skipped = batch.total_users - exported
    pos_count = sum(1 for sample in exportable_samples if sample.label == 1)
    neg_count = exported - pos_count
    print(
        f"[export_training_csv] exported={exported}, skipped={skipped}, "
        f"recent_bp_avg_count={recent_bp_avg_count}"
    )
    print(f"  正样本(Risk=1): {pos_count}, 负样本(Risk=0): {neg_count}")
    if exported > 0:
        print(f"  正样本比例: {pos_count / exported:.1%}")
    return output.getvalue()


def get_training_export_stats():
    """统计训练数据导出的样本构成，供管理员页面展示。"""
    recent_bp_avg_count = _get_recent_bp_avg_count()
    batch = load_training_export_batch(recent_bp_avg_count)
    exportable_samples = batch.samples

    exported = len(exportable_samples)
    skipped = batch.total_users - exported
    pos_count = sum(1 for sample in exportable_samples if sample.label == 1)
    diagnosis_labeled = sum(
        1 for sample in exportable_samples if sample.label_source == "diagnosis"
    )
    rule_labeled = sum(
        1 for sample in exportable_samples if sample.label_source == "rule"
    )
    neg_count = exported - pos_count
    return {
        "recent_bp_avg_count": recent_bp_avg_count,
        "exportable_samples": exported,
        "skipped_users": skipped,
        "positive_samples": pos_count,
        "negative_samples": neg_count,
        "positive_ratio": round(pos_count / exported, 4) if exported else 0,
        "diagnosis_labeled_samples": diagnosis_labeled,
        "rule_labeled_samples": rule_labeled,
    }
