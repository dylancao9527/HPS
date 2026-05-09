from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .config import THRESHOLD_MIN_RECALL, THRESHOLD_SEARCH_MODE


def _calculate_scale_pos_weight(y_train):
    pos_count = int(y_train.sum())
    neg_count = int(len(y_train) - pos_count)
    if pos_count == 0:
        return 1.0
    return round(neg_count / pos_count, 4)


def _build_threshold_candidates(y_pred_proba):
    unique_scores = sorted(
        {float(score) for score in np.asarray(y_pred_proba, dtype=float).reshape(-1)}
    )
    candidates = [score for score in unique_scores if 0.0 < score < 1.0]
    return candidates or [0.5]


def summarize_calibration(y_true, y_pred_proba, bin_count=10):
    frame = pd.DataFrame({"y_true": y_true, "y_pred": y_pred_proba})
    frame["bin"] = pd.cut(
        frame["y_pred"],
        bins=bin_count,
        labels=False,
        include_lowest=True,
    )

    bins = []
    total = len(frame)
    ece = 0.0
    for bin_id, bucket in frame.groupby("bin", dropna=True):
        avg_pred = float(bucket["y_pred"].mean())
        avg_true = float(bucket["y_true"].mean())
        weight = len(bucket) / total
        ece += abs(avg_pred - avg_true) * weight
        bins.append(
            {
                "bin": int(bin_id),
                "count": int(len(bucket)),
                "avg_pred": round(avg_pred, 4),
                "avg_true": round(avg_true, 4),
            }
        )
    return {"ece": round(float(ece), 4), "bins": bins}


def evaluate_model(model, X_eval, y_eval, threshold=0.5):
    from sklearn.metrics import (
        accuracy_score,
        average_precision_score,
        brier_score_loss,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    y_pred_proba = np.asarray(model.predict(X_eval), dtype=float).reshape(-1)
    y_pred_label = (y_pred_proba > threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_eval, y_pred_label, labels=[0, 1]).ravel()
    calibration = summarize_calibration(y_eval, y_pred_proba)

    return {
        "threshold": threshold,
        "accuracy": round(float(accuracy_score(y_eval, y_pred_label)), 4),
        "auc": round(float(roc_auc_score(y_eval, y_pred_proba)), 4),
        "precision": round(
            float(precision_score(y_eval, y_pred_label, zero_division=0)), 4
        ),
        "recall": round(float(recall_score(y_eval, y_pred_label, zero_division=0)), 4),
        "f1": round(float(f1_score(y_eval, y_pred_label, zero_division=0)), 4),
        "pr_auc": round(float(average_precision_score(y_eval, y_pred_proba)), 4),
        "brier_score": round(float(brier_score_loss(y_eval, y_pred_proba)), 4),
        "calibration": calibration,
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
    }


def find_best_threshold(
    model,
    X_valid,
    y_valid,
    strategy: str = THRESHOLD_SEARCH_MODE,
    min_recall: float | None = THRESHOLD_MIN_RECALL,
) -> dict[str, Any]:
    from sklearn.metrics import f1_score, precision_score, recall_score

    y_pred_proba = np.asarray(model.predict(X_valid), dtype=float).reshape(-1)
    threshold_candidates = _build_threshold_candidates(y_pred_proba)
    candidate_count = len(threshold_candidates)
    best = {
        "threshold": 0.5,
        "f1": -1.0,
        "precision": 0.0,
        "recall": 0.0,
        "strategy": strategy,
        "min_recall": min_recall,
        "candidate_count": candidate_count,
    }

    for threshold in threshold_candidates:
        y_pred = (y_pred_proba > threshold).astype(int)
        recall = recall_score(y_valid, y_pred, zero_division=0)
        if (
            strategy == "recall_priority"
            and min_recall is not None
            and recall < min_recall
        ):
            continue

        f1 = f1_score(y_valid, y_pred, zero_division=0)
        precision = precision_score(y_valid, y_pred, zero_division=0)
        if strategy == "recall_priority":
            is_better = precision > best["precision"] or (
                precision == best["precision"] and f1 > best["f1"]
            )
        else:
            is_better = f1 > best["f1"] or (
                f1 == best["f1"] and precision > best["precision"]
            )

        if is_better:
            best = {
                "threshold": round(float(threshold), 6),
                "f1": round(float(f1), 4),
                "precision": round(float(precision), 4),
                "recall": round(float(recall), 4),
                "strategy": strategy,
                "min_recall": min_recall,
                "candidate_count": candidate_count,
            }

    if best["f1"] < 0 and strategy == "recall_priority":
        return find_best_threshold(
            model,
            X_valid,
            y_valid,
            strategy="f1",
            min_recall=None,
        )

    return best


def summarize_feature_importance(feature_columns, optimized_model):
    importance = optimized_model.feature_importance(importance_type="gain")
    feature_imp = sorted(
        zip(feature_columns, importance), key=lambda x: x[1], reverse=True
    )
    total_gain = float(sum(importance)) or 1.0
    feature_summary = [
        {
            "feature": feat,
            "gain": round(float(gain), 1),
            "gain_share": round(float(gain) / total_gain, 4),
        }
        for feat, gain in feature_imp
    ]

    gain_map = {item["feature"]: item["gain_share"] for item in feature_summary}
    bp_gain_share = gain_map.get("sysBP", 0.0) + gain_map.get("diaBP", 0.0)
    top3_gain_share = sum(item["gain_share"] for item in feature_summary[:3])
    low_signal_features = [
        item["feature"] for item in feature_summary if item["gain_share"] < 0.01
    ]

    interpretation = []
    if bp_gain_share >= 0.6:
        interpretation.append(
            "当前模型的主要判别信号仍集中在收缩压和舒张压，说明血压水平对分类贡献最强。"
        )
    else:
        interpretation.append(
            "当前模型的增益分布较为分散，血压特征虽重要，但未出现极端单一主导。"
        )

    if gain_map.get("currentSmoker", 0.0) < 0.02 or gain_map.get("diabetes", 0.0) < 0.02:
        interpretation.append(
            '吸烟和糖尿病特征增益偏低，更可能与样本分布、缺失比例或区分度不足有关，不属于单纯的「梯度没调好」。'
        )

    interpretation.append(
            '对树模型而言，通常无需像神经网络那样单独讨论「优化梯度」；更有效的优化方向是特征工程、样本质量、正则化和阈值策略。'
    )

    return {
        "feature_importance": feature_summary,
        "total_gain": round(total_gain, 1),
        "bp_gain_share": round(bp_gain_share, 4),
        "top3_gain_share": round(top3_gain_share, 4),
        "low_signal_features": low_signal_features,
        "interpretation": interpretation,
    }
