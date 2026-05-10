from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO

import numpy as np

from .config import (
    DEFAULT_CONFIG,
    SEED,
    TrainingConfig,
)
from .data import get_feature_sets, prepare_lgbm_data
from .metrics import find_best_threshold
from .progress import TrainingProgress
from .reporting import generate_report, save_final_model, save_training_meta
from .trainer import (
    BASELINE_PARAMS,
    LightGBMTrainer,
    LightGBMTunerCVStrategy,
    TuningStrategy,
    apply_missing_value_strategy,
    split_train_test,
    tune_lightgbm_with_tuner_cv,
)


def _format_ratio(value) -> str:
    if value is None:
        return "—"
    return f"{float(value):.1%}"


def _run_quietly(callable_obj, *args, **kwargs):
    with redirect_stdout(StringIO()):
        return callable_obj(*args, **kwargs)


def _train_final_cycle(
    params,
    X_train,
    X_test,
    y_train,
    y_test,
    categorical_features,
    random_seed,
    config: TrainingConfig | None = None,
):
    if config is None:
        config = DEFAULT_CONFIG
    trainer = (
        LightGBMTrainer(
            params, categorical_features,
            random_seed=random_seed,
            max_boost_rounds=config.max_boost_rounds,
            early_stopping_rounds=config.early_stopping_rounds,
            validation_size=config.threshold_valid_size,
        )
        .with_threshold_isolation(config.threshold_valid_size)
    )
    data = trainer.build_data(X_train, y_train, X_test, y_test)
    frames, imputation_stats, missing_strategy = apply_missing_value_strategy(
        data.X_fit,
        data.frame_dict(),
        strategy=config.missing_value_strategy,
    )
    result = trainer.train(
        frames["X_fit"], data.y_fit, frames["X_valid"], data.y_valid
    )
    model = trainer.refit(
        frames["X_model_pool"], data.y_model_pool, result.best_iteration
    )
    threshold_info = find_best_threshold(
        model, frames["X_threshold"], data.y_threshold,
        strategy=config.threshold_search_mode,
        min_recall=config.threshold_min_recall,
    )
    metrics = LightGBMTrainer.evaluate(
        model, frames["X_test"], data.y_test, threshold_info["threshold"]
    )
    metrics["threshold"] = threshold_info["threshold"]
    metrics["threshold_selection"] = threshold_info
    metrics["best_iteration"] = result.best_iteration
    metrics["missing_value_strategy"] = missing_strategy
    metrics["imputation_stats"] = imputation_stats
    metrics["split_summary"] = {
        "threshold_valid_rows": int(len(data.X_threshold)),
        "early_stop_fit_rows": int(len(data.X_fit)),
        "early_stop_valid_rows": int(len(data.X_valid)),
        "final_refit_rows": int(len(data.X_model_pool)),
        "threshold_isolation": True,
        "best_iteration_source": "early_stop_valid_refit",
    }
    return model, metrics


def run_feature_ablation(
    X, y, categorical_features, random_seed: int = SEED,
    tuning_strategy: TuningStrategy | None = None,
    config: TrainingConfig | None = None,
):
    if config is None:
        config = DEFAULT_CONFIG
    if tuning_strategy is None:
        tuning_strategy = LightGBMTunerCVStrategy()
    summaries = []
    for feature_set in get_feature_sets():
        columns = feature_set["columns"]
        categorical = [col for col in categorical_features if col in columns]
        X_subset = X[columns].copy()
        X_train, X_test, y_train, y_test = split_train_test(
            X_subset,
            y,
            random_seed=random_seed,
            test_size=config.test_size,
        )
        tuning_summary = tuning_strategy.tune(
            X_train,
            y_train,
            categorical,
            random_seed=random_seed,
            learning_rate=config.learning_rate,
            max_boost_rounds=config.max_boost_rounds,
            early_stopping_rounds=config.early_stopping_rounds,
        )
        _, optimized_metrics = _train_final_cycle(
            tuning_summary.params,
            X_train, X_test, y_train, y_test, categorical, random_seed,
            config=config,
        )
        summaries.append(
            {
                "name": feature_set["name"],
                "columns": columns,
                "auc": optimized_metrics["auc"],
                "pr_auc": optimized_metrics["pr_auc"],
                "brier_score": optimized_metrics["brier_score"],
                "threshold": optimized_metrics["threshold"],
            }
        )
    return summaries


def summarize_multi_seed_runs(seed_runs):
    if not seed_runs:
        raise ValueError("seed_runs must not be empty")

    auc_values = [item["auc"] for item in seed_runs]
    pr_auc_values = [item["pr_auc"] for item in seed_runs]
    brier_values = [item["brier_score"] for item in seed_runs]
    threshold_values = [item["threshold"] for item in seed_runs]
    return {
        "seed_count": len(seed_runs),
        "auc_mean": round(float(np.mean(auc_values)), 4),
        "auc_std": round(float(np.std(auc_values)), 4),
        "pr_auc_mean": round(float(np.mean(pr_auc_values)), 4),
        "pr_auc_std": round(float(np.std(pr_auc_values)), 4),
        "brier_mean": round(float(np.mean(brier_values)), 4),
        "brier_std": round(float(np.std(brier_values)), 4),
        "threshold_min": round(float(min(threshold_values)), 4),
        "threshold_max": round(float(max(threshold_values)), 4),
        "runs": seed_runs,
    }


def run_multi_seed_audit(
    X, y, categorical_features, seeds,
    tuning_strategy: TuningStrategy | None = None,
    config: TrainingConfig | None = None,
):
    if config is None:
        config = DEFAULT_CONFIG
    if tuning_strategy is None:
        tuning_strategy = LightGBMTunerCVStrategy()
    runs = []
    for seed in seeds:
        X_train, X_test, y_train, y_test = split_train_test(
            X,
            y,
            random_seed=seed,
            test_size=config.test_size,
        )
        tuning_summary = tuning_strategy.tune(
            X_train,
            y_train,
            categorical_features,
            random_seed=seed,
            learning_rate=config.learning_rate,
            max_boost_rounds=config.max_boost_rounds,
            early_stopping_rounds=config.early_stopping_rounds,
        )
        _, optimized_metrics = _train_final_cycle(
            tuning_summary.params,
            X_train, X_test, y_train, y_test, categorical_features, seed,
            config=config,
        )
        runs.append(
            {
                "seed": seed,
                "auc": optimized_metrics["auc"],
                "pr_auc": optimized_metrics["pr_auc"],
                "brier_score": optimized_metrics["brier_score"],
                "threshold": optimized_metrics["threshold"],
            }
        )
    return summarize_multi_seed_runs(runs)


def run_training(
    random_seed: int = SEED,
    tuning_strategy: TuningStrategy | None = None,
    config: TrainingConfig | None = None,
):
    if config is None:
        config = DEFAULT_CONFIG
    if tuning_strategy is None:
        tuning_strategy = LightGBMTunerCVStrategy()
    progress = TrainingProgress(total_steps=5)

    progress.start_step("数据准备", detail=f"seed={random_seed}")
    X, y, feature_columns, categorical_features, dataset_summary = _run_quietly(
        prepare_lgbm_data,
        random_seed=random_seed,
        bp_meds_policy=config.bp_meds_policy,
        label_mode=config.label_mode,
    )
    X_train, X_test, y_train, y_test = split_train_test(
        X,
        y,
        random_seed=random_seed,
        test_size=config.test_size,
    )
    progress.finish_step(
        rows=len(X),
        pos=_format_ratio(dataset_summary.get("positive_ratio", np.mean(y))),
    )

    split_summary = {
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }

    progress.start_step("Baseline")
    baseline_params = {**BASELINE_PARAMS, "seed": random_seed, "learning_rate": config.learning_rate}
    baseline_model, baseline_metrics = _train_final_cycle(
        baseline_params,
        X_train, X_test, y_train, y_test,
        categorical_features, random_seed,
        config=config,
    )
    baseline_metrics["params"] = baseline_params
    progress.finish_step(
        auc=baseline_metrics.get("auc"),
        recall=baseline_metrics.get("recall"),
    )

    progress.start_step("官方调优", detail="LightGBMTunerCV")
    tuning_summary = tuning_strategy.tune(
        X_train,
        y_train,
        categorical_features,
        random_seed=random_seed,
        learning_rate=config.learning_rate,
        max_boost_rounds=config.max_boost_rounds,
        early_stopping_rounds=config.early_stopping_rounds,
    )
    progress.finish_step(
        cv_auc=tuning_summary.cv_auc,
        best_iteration=tuning_summary.best_iteration,
    )

    progress.start_step("最终训练")
    # Reuse _train_final_cycle to avoid duplicating the train→refit→threshold→eval flow
    optimized_model, optimized_metrics = _train_final_cycle(
        tuning_summary.params,
        X_train, X_test, y_train, y_test,
        categorical_features, random_seed,
        config=config,
    )
    optimized_metrics["params"] = tuning_summary.params
    split_summary.update(optimized_metrics.get("split_summary", {}))
    progress.finish_step(
        auc=optimized_metrics.get("auc"),
        recall=optimized_metrics.get("recall"),
        f1=optimized_metrics.get("f1"),
        threshold=optimized_metrics.get("threshold"),
    )

    feature_ablation = []
    if config.enable_feature_ablation:
        feature_ablation = run_feature_ablation(
            X,
            y,
            categorical_features,
            random_seed=random_seed,
            tuning_strategy=tuning_strategy,
            config=config,
        )

    multi_seed_summary = None
    if config.multi_seed_audit_seeds:
        multi_seed_summary = run_multi_seed_audit(
            X,
            y,
            categorical_features,
            config.multi_seed_audit_seeds,
            tuning_strategy=tuning_strategy,
            config=config,
        )

    progress.start_step("保存产物")
    save_final_model(
        optimized_model,
        feature_columns,
        categorical_features,
        optimized_metrics["threshold"],
        bp_meds_policy=dataset_summary["bp_meds_policy"],
        label_mode=dataset_summary["label_mode"],
        dataset_hash=dataset_summary["dataset_hash"],
        missing_value_strategy=optimized_metrics.get("missing_value_strategy", "native"),
        threshold_search_mode=config.threshold_search_mode,
        threshold_min_recall=config.threshold_min_recall,
    )
    save_training_meta(
        dataset_summary,
        split_summary,
        baseline_metrics,
        tuning_summary,
        optimized_metrics,
        feature_columns,
        optimized_model,
        feature_ablation=feature_ablation,
        multi_seed_summary=multi_seed_summary,
    )
    generate_report(
        baseline_metrics,
        optimized_metrics,
        feature_columns,
        optimized_model,
        dataset_summary,
        tuning_summary,
        split_summary,
        feature_ablation=feature_ablation,
        multi_seed_summary=multi_seed_summary,
    )
    progress.finish_step(
        artifacts="lgbm_model.txt model_config.json training_meta.json model_report.md"
    )
