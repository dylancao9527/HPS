from __future__ import annotations

import warnings
from collections import namedtuple
from dataclasses import dataclass
from typing import Optional, Protocol

import pandas as pd
import lightgbm as lgb

from .config import (
    CV_SPLITS,
    EARLY_STOPPING_ROUNDS,
    MAX_BOOST_ROUNDS,
    SEED,
    TEST_SIZE,
    THRESHOLD_MIN_RECALL,
    THRESHOLD_SEARCH_MODE,
    THRESHOLD_VALID_SIZE,
    TRAINING_MISSING_VALUE_STRATEGY,
)
from .metrics import _calculate_scale_pos_weight, evaluate_model, find_best_threshold


OFFICIAL_TUNED_PARAM_KEYS = (
    "lambda_l1",
    "lambda_l2",
    "num_leaves",
    "feature_fraction",
    "bagging_fraction",
    "bagging_freq",
    "min_child_samples",
)

TrainResult = namedtuple("TrainResult", ["model", "best_iteration", "scale_pos_weight"])


@dataclass(frozen=True)
class TrainingData:
    X_fit: pd.DataFrame
    y_fit: pd.Series
    X_valid: pd.DataFrame
    y_valid: pd.Series
    X_test: pd.DataFrame
    y_test: pd.Series
    X_threshold: Optional[pd.DataFrame] = None
    y_threshold: Optional[pd.Series] = None
    X_model_pool: Optional[pd.DataFrame] = None
    y_model_pool: Optional[pd.Series] = None

    @property
    def has_threshold_holdout(self) -> bool:
        return self.X_threshold is not None

    def frame_dict(self) -> dict:
        result = {
            "X_fit": self.X_fit,
            "X_valid": self.X_valid,
            "X_test": self.X_test,
        }
        if self.X_threshold is not None:
            result["X_threshold"] = self.X_threshold
        if self.X_model_pool is not None:
            result["X_model_pool"] = self.X_model_pool
        return result


@dataclass(frozen=True)
class ParameterSet:
    params: dict
    source: str = "baseline"
    cv_auc: float | None = None
    best_iteration: int | None = None
    scale_pos_weight: float | None = None
    tuner_name: str | None = None
    tuning_notes: str | None = None
    n_splits: int | None = None
    official_tuning: bool = False

    @property
    def tuned_params(self) -> dict:
        return {
            k: v
            for k, v in self.params.items()
            if k in OFFICIAL_TUNED_PARAM_KEYS
        }

    def to_dict(self) -> dict:
        return {
            "best_params": self.params,
            "source": self.source,
            "cv_auc": self.cv_auc,
            "best_iteration": self.best_iteration,
            "scale_pos_weight": self.scale_pos_weight,
            "tuner_name": self.tuner_name,
            "tuning_notes": self.tuning_notes,
            "n_splits": self.n_splits,
            "official_tuning": self.official_tuning,
            "tuned_params": self.tuned_params,
        }


class TuningStrategy(Protocol):
    def tune(
        self,
        X_train,
        y_train,
        categorical_features: list,
        random_seed: int,
        learning_rate: float = 0.05,
        max_boost_rounds: int = MAX_BOOST_ROUNDS,
        early_stopping_rounds: int = EARLY_STOPPING_ROUNDS,
        cv_splits: int = CV_SPLITS,
    ) -> ParameterSet: ...


class LightGBMTunerCVStrategy:
    def tune(
        self,
        X_train,
        y_train,
        categorical_features,
        random_seed: int = SEED,
        learning_rate: float = 0.05,
        max_boost_rounds: int = MAX_BOOST_ROUNDS,
        early_stopping_rounds: int = EARLY_STOPPING_ROUNDS,
        cv_splits: int = CV_SPLITS,
        verbose: bool = True,
    ) -> ParameterSet:
        return tune_lightgbm_with_tuner_cv(
            X_train, y_train, categorical_features,
            random_seed=random_seed, learning_rate=learning_rate,
            max_boost_rounds=max_boost_rounds,
            early_stopping_rounds=early_stopping_rounds,
            cv_splits=cv_splits,
            verbose=verbose,
        )


class NoOpTuningStrategy:
    def tune(
        self,
        X_train,
        y_train,
        categorical_features,
        random_seed: int,
        learning_rate: float = 0.05,
        max_boost_rounds: int = MAX_BOOST_ROUNDS,
        early_stopping_rounds: int = EARLY_STOPPING_ROUNDS,
        cv_splits: int = CV_SPLITS,
    ) -> ParameterSet:
        _ = max_boost_rounds, early_stopping_rounds, cv_splits
        scale_pos_weight = _calculate_scale_pos_weight(y_train)
        params = {
            "objective": "binary",
            "metric": "auc",
            "boosting_type": "gbdt",
            "learning_rate": learning_rate,
            "scale_pos_weight": scale_pos_weight,
            "seed": random_seed,
        }
        return ParameterSet(
            params=params,
            source="noop",
            scale_pos_weight=scale_pos_weight,
        )


def _log(verbose: bool, message: str = "") -> None:
    if verbose:
        print(message)


def split_train_test(X, y, random_seed: int = SEED, test_size=TEST_SIZE):
    from sklearn.model_selection import train_test_split

    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_seed,
        stratify=y,
    )


def _split_fit_valid(
    X_train,
    y_train,
    test_size=THRESHOLD_VALID_SIZE,
    random_seed: int = SEED,
):
    from sklearn.model_selection import train_test_split

    return train_test_split(
        X_train,
        y_train,
        test_size=test_size,
        random_state=random_seed,
        stratify=y_train,
    )


def _split_threshold_valid(
    X_train,
    y_train,
    random_seed: int = SEED,
    test_size=THRESHOLD_VALID_SIZE,
):
    return _split_fit_valid(
        X_train,
        y_train,
        test_size=test_size,
        random_seed=random_seed,
    )


def apply_missing_value_strategy(
    X_fit,
    named_frames,
    strategy=TRAINING_MISSING_VALUE_STRATEGY,
):
    prepared_frames = {name: frame.copy() for name, frame in named_frames.items()}
    if strategy == "native":
        return prepared_frames, None, "native"

    if strategy == "median_impute":
        numeric_columns = X_fit.select_dtypes(include="number").columns
        medians = X_fit[numeric_columns].median().to_dict()

        for frame in prepared_frames.values():
            for column, median in medians.items():
                if pd.notna(median) and column in frame.columns:
                    frame[column] = frame[column].fillna(median)

        return prepared_frames, medians, "median_impute"

    raise ValueError(
        f"Unsupported TRAINING_MISSING_VALUE_STRATEGY: {strategy}"
    )


BASELINE_PARAMS = {
    "objective": "binary",
    "metric": "auc",
    "boosting_type": "gbdt",
    "num_leaves": 31,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "feature_pre_filter": False,
    "verbosity": -1,
}


class LightGBMTrainer:
    def __init__(
        self,
        params: dict,
        categorical_features: list,
        missing_value_strategy: str = TRAINING_MISSING_VALUE_STRATEGY,
        random_seed: int = SEED,
        max_boost_rounds: int = MAX_BOOST_ROUNDS,
        early_stopping_rounds: int = EARLY_STOPPING_ROUNDS,
        validation_size: float = THRESHOLD_VALID_SIZE,
    ):
        self._params = params
        self._categorical_features = categorical_features
        self._missing_value_strategy = missing_value_strategy
        self._random_seed = random_seed
        self._max_boost_rounds = max_boost_rounds
        self._early_stopping_rounds = early_stopping_rounds
        self._validation_size = validation_size
        self._threshold_isolation_size: float | None = None

    def with_threshold_isolation(
        self, size: float = THRESHOLD_VALID_SIZE
    ) -> "LightGBMTrainer":
        self._threshold_isolation_size = size
        return self

    def build_data(
        self, X_train, y_train, X_test, y_test
    ) -> TrainingData:
        if self._threshold_isolation_size is not None:
            X_model_pool, X_threshold, y_model_pool, y_threshold = (
                _split_threshold_valid(
                    X_train,
                    y_train,
                    random_seed=self._random_seed,
                    test_size=self._threshold_isolation_size,
                )
            )
            X_fit, X_valid, y_fit, y_valid = _split_fit_valid(
                X_model_pool,
                y_model_pool,
                test_size=self._validation_size,
                random_seed=self._random_seed,
            )
            return TrainingData(
                X_fit=X_fit,
                y_fit=y_fit,
                X_valid=X_valid,
                y_valid=y_valid,
                X_test=X_test,
                y_test=y_test,
                X_threshold=X_threshold,
                y_threshold=y_threshold,
                X_model_pool=X_model_pool,
                y_model_pool=y_model_pool,
            )
        X_fit, X_valid, y_fit, y_valid = _split_fit_valid(
            X_train,
            y_train,
            test_size=self._validation_size,
            random_seed=self._random_seed,
        )
        return TrainingData(
            X_fit=X_fit,
            y_fit=y_fit,
            X_valid=X_valid,
            y_valid=y_valid,
            X_test=X_test,
            y_test=y_test,
        )

    def train(self, X_fit, y_fit, X_valid, y_valid) -> TrainResult:
        scale_pos_weight = _calculate_scale_pos_weight(y_fit)
        params = {**self._params, "scale_pos_weight": scale_pos_weight}
        train_data = lgb.Dataset(
            X_fit,
            label=y_fit,
            categorical_feature=self._categorical_features,
            free_raw_data=False,
        )
        valid_data = lgb.Dataset(
            X_valid,
            label=y_valid,
            reference=train_data,
            categorical_feature=self._categorical_features,
            free_raw_data=False,
        )
        model = lgb.train(
            params,
            train_data,
            num_boost_round=self._max_boost_rounds,
            valid_sets=[valid_data],
            valid_names=["valid"],
            callbacks=[
                lgb.early_stopping(stopping_rounds=self._early_stopping_rounds, verbose=False),
                lgb.log_evaluation(period=0),
            ],
        )
        best_iteration = model.best_iteration or self._max_boost_rounds
        return TrainResult(
            model=model,
            best_iteration=best_iteration,
            scale_pos_weight=scale_pos_weight,
        )

    def refit(self, X_model_pool, y_model_pool, best_iteration: int):
        scale_pos_weight = _calculate_scale_pos_weight(y_model_pool)
        params = {**self._params, "scale_pos_weight": scale_pos_weight}
        final_train_data = lgb.Dataset(
            X_model_pool,
            label=y_model_pool,
            categorical_feature=self._categorical_features,
            free_raw_data=False,
        )
        return lgb.train(
            params,
            final_train_data,
            num_boost_round=best_iteration,
            callbacks=[lgb.log_evaluation(period=0)],
        )

    @staticmethod
    def evaluate(model, X_eval, y_eval, threshold=0.5):
        return evaluate_model(model, X_eval, y_eval, threshold)


def _build_lightgbm_tuner_params(y_train, random_seed: int = SEED, learning_rate: float = 0.05):
    scale_pos_weight = _calculate_scale_pos_weight(y_train)
    return {
        "objective": "binary",
        "metric": "auc",
        "boosting_type": "gbdt",
        "learning_rate": learning_rate,
        "feature_pre_filter": False,
        "scale_pos_weight": scale_pos_weight,
        "seed": random_seed,
        "verbosity": -1,
    }, scale_pos_weight


def _build_official_tuning_summary(
    params, tuner, best_booster, scale_pos_weight, n_splits: int = CV_SPLITS
) -> ParameterSet:
    best_params = {
        **params,
        **tuner.best_params,
    }
    return ParameterSet(
        params=best_params,
        source="LightGBMTunerCV",
        cv_auc=round(float(tuner.best_score), 4),
        best_iteration=getattr(best_booster, "best_iteration", None),
        tuner_name="LightGBMTunerCV",
        n_splits=n_splits,
        scale_pos_weight=scale_pos_weight,
        official_tuning=True,
        tuning_notes="LightGBMTunerCV official stepwise parameter tuning",
    )


def _run_official_tuner(tuner):
    import optuna

    previous_verbosity = optuna.logging.get_verbosity()
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="The groups parameter is ignored by StratifiedKFold",
            category=UserWarning,
        )
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        try:
            tuner.run()
        finally:
            optuna.logging.set_verbosity(previous_verbosity)


def tune_lightgbm_with_tuner_cv(
    X_train,
    y_train,
    categorical_features,
    random_seed: int = SEED,
    learning_rate: float = 0.05,
    max_boost_rounds: int = MAX_BOOST_ROUNDS,
    early_stopping_rounds: int = EARLY_STOPPING_ROUNDS,
    cv_splits: int = CV_SPLITS,
    verbose: bool = True,
):
    from optuna_integration.lightgbm import LightGBMTunerCV
    from sklearn.model_selection import StratifiedKFold

    _log(verbose, "\n\n[3/4] LightGBMTunerCV 调参...")
    _log(verbose, "-" * 40)

    _log(
        verbose,
        f"  调参输入：rows={len(X_train)}，cv={cv_splits} 折，"
        f"categorical={categorical_features}",
    )
    _log(
        verbose,
        "  调参范围：lambda_l1 / lambda_l2 / num_leaves / "
        "feature_fraction / bagging_fraction / bagging_freq / min_child_samples",
    )
    params, scale_pos_weight = _build_lightgbm_tuner_params(
        y_train,
        random_seed=random_seed,
        learning_rate=learning_rate,
    )
    train_data = lgb.Dataset(
        X_train,
        label=y_train,
        categorical_feature=categorical_features,
        free_raw_data=False,
    )
    folds = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=random_seed)
    tuner = LightGBMTunerCV(
        params=params,
        train_set=train_data,
        folds=folds,
        num_boost_round=max_boost_rounds,
        callbacks=[
            lgb.early_stopping(stopping_rounds=early_stopping_rounds, verbose=False),
            lgb.log_evaluation(period=0),
        ],
        seed=random_seed,
        optuna_seed=random_seed,
        return_cvbooster=True,
        show_progress_bar=True,
    )
    _log(verbose, "  正在运行官方 LightGBMTunerCV，这一步耗时相对最长...")
    _run_official_tuner(tuner)
    best_booster = tuner.get_best_booster()
    summary = _build_official_tuning_summary(
        params,
        tuner,
        best_booster,
        scale_pos_weight,
        n_splits=cv_splits,
    )

    _log(verbose, f"\n  最优 CV AUC: {summary.cv_auc:.4f}")
    _log(verbose, "  关键参数：")
    for key, value in summary.tuned_params.items():
        _log(verbose, f"    {key}: {value}")

    return summary
