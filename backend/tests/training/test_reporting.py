import json
from pathlib import Path
from types import SimpleNamespace

from training import reporting


def _metrics(**overrides):
    base = {
        "accuracy": 0.91,
        "auc": 0.93,
        "precision": 0.89,
        "recall": 0.86,
        "f1": 0.87,
        "pr_auc": 0.92,
        "brier_score": 0.08,
        "threshold": 0.42,
        "best_iteration": 312,
    }
    base.update(overrides)
    return base


def test_generate_report_describes_single_official_tuning_path(monkeypatch):
    report_dir = Path(__file__).resolve().parents[2] / ".pytest-tmp" / "reporting"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "model_report.md"
    if report_file.exists():
        report_file.unlink()

    monkeypatch.setattr(
        reporting,
        "summarize_feature_importance",
        lambda feature_columns, optimized_model: {
            "feature_importance": [
                {
                    "feature": "age",
                    "gain": 12.0,
                    "gain_share": 1.0,
                }
            ],
            "bp_gain_share": 0.2,
            "top3_gain_share": 1.0,
            "low_signal_features": [],
            "interpretation": ["age 是主要风险特征"],
        },
    )

    dataset_summary = {
        "profile_name": "raw_baseline",
        "base_dataset_name": "Hypertension-risk-model-main.csv",
        "base_rows": 100,
        "base_pos_ratio": 0.4,
        "export_rows": 0,
        "export_pos_ratio": None,
        "total_rows": 100,
        "positive_rows": 40,
        "negative_rows": 60,
        "positive_ratio": 0.4,
        "missing_summary": {},
    }
    optimized_metrics = _metrics(
        calibration={
            "ece": 0.03,
            "bins": [{"bin": "0.0-0.1", "count": 5, "avg_pred": 0.05, "avg_true": 0.0}],
        },
        threshold_selection={
            "strategy": "recall_priority",
            "min_recall": 0.8,
            "candidate_count": 20,
            "recall_constraint_satisfied": True,
        },
        split_summary={
            "threshold_isolation": True,
            "threshold_isolation_scope": "before_tuning",
            "best_iteration_source": "early_stop_valid_refit",
        },
        confusion_matrix={"tn": 50, "fp": 10, "fn": 4, "tp": 36},
        params={
            "lambda_l1": 0.1,
            "lambda_l2": 0.2,
            "num_leaves": 16,
        },
    )
    tuning_summary = SimpleNamespace(
        tuner_name="LightGBMTunerCV",
        tuning_notes="LightGBMTunerCV official stepwise parameter tuning",
        n_splits=5,
        cv_auc=0.9384,
        scale_pos_weight=1.5,
        official_tuning=True,
        params={"objective": "binary"},
        best_iteration=312,
    )

    monkeypatch.setattr(reporting, "DOCS_DIR", report_dir)
    report_path = reporting.generate_report(
        _metrics(),
        optimized_metrics,
        ["age"],
        SimpleNamespace(name="optimized"),
        dataset_summary,
        tuning_summary,
        {"train_rows": 80, "test_rows": 20},
    )

    report = report_path.read_text(encoding="utf-8")
    report_path.unlink()
    assert "- 调优器：`LightGBMTunerCV`" in report
    assert "- 参数策略：`LightGBMTunerCV official stepwise parameter tuning`" in report
    assert "- 最优 CV AUC：`0.9384`" in report
    assert "- Recall 约束满足：`True`" in report
    assert "- 阈值集隔离范围：`before_tuning`" in report
    assert "不采用预先持久化模型" not in report
    assert "Prophet 模型持久化" in report
    bucket_row = "| 0.0-0.1 | 5 | 0.0500 | 0.0000 |"
    assert report.index("| Bin | Count | Avg Pred | Avg True |") < report.index(bucket_row)
    assert report.index(bucket_row) < report.index("### 调优方式")
    assert report.index(bucket_row) < report.index("### 最终测试集混淆矩阵")
    assert "第二阶段调优器" not in report
    assert "第一阶段 CV AUC" not in report


def test_save_final_model_writes_runtime_threshold_strategy(monkeypatch, tmp_path):
    class FakeModel:
        best_iteration = 12

        def save_model(self, path):
            Path(path).write_text("model", encoding="utf-8")

        def current_iteration(self):
            return 12

    monkeypatch.setattr(reporting, "MODELS_DIR", tmp_path)

    reporting.save_final_model(
        FakeModel(),
        ["age"],
        [],
        0.42,
        bp_meds_policy="observed",
        label_mode="diagnosis_only",
        dataset_hash="hash-789",
        missing_value_strategy="median_impute",
        threshold_search_mode="f1",
        threshold_min_recall=None,
    )

    config = json.loads((tmp_path / "model_config.json").read_text(encoding="utf-8"))
    assert config["threshold_search_mode"] == "f1"
    assert config["threshold_min_recall"] is None
