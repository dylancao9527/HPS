import sys
from types import ModuleType
from types import SimpleNamespace
import warnings

import pandas as pd

from training.config import CV_SPLITS
from training.trainer import (
    LightGBMTrainer,
    NoOpTuningStrategy,
    _build_lightgbm_tuner_params,
    _build_official_tuning_summary,
    _run_official_tuner,
)


def test_build_lightgbm_tuner_params_keeps_official_tuner_basics():
    params, scale_pos_weight = _build_lightgbm_tuner_params(
        pd.Series([0, 0, 1]),
        random_seed=7,
    )

    assert params["objective"] == "binary"
    assert params["metric"] == "auc"
    assert params["boosting_type"] == "gbdt"
    assert params["feature_pre_filter"] is False
    assert params["seed"] == 7
    assert params["scale_pos_weight"] == scale_pos_weight


def test_build_official_tuning_summary_uses_lightgbm_tuner_fields():
    params = {"objective": "binary", "metric": "auc", "seed": 7}
    tuner = SimpleNamespace(
        best_params={
            "lambda_l1": 0.1,
            "num_leaves": 16,
            "min_child_samples": 20,
        },
        best_score=0.93841,
    )
    best_booster = SimpleNamespace(best_iteration=312)

    summary = _build_official_tuning_summary(
        params,
        tuner,
        best_booster,
        scale_pos_weight=1.5,
    )

    assert summary.tuner_name == "LightGBMTunerCV"
    assert summary.official_tuning is True
    assert summary.n_splits == CV_SPLITS
    assert summary.scale_pos_weight == 1.5
    assert summary.cv_auc == 0.9384
    assert summary.best_iteration == 312
    assert summary.params["objective"] == "binary"
    assert summary.params["lambda_l1"] == 0.1
    assert summary.tuned_params == {
        "lambda_l1": 0.1,
        "num_leaves": 16,
        "min_child_samples": 20,
    }


def test_run_official_tuner_suppresses_groups_warning_and_restores_optuna(monkeypatch):
    class FakeLogging:
        WARNING = 30

        def __init__(self):
            self._verbosity = 20
            self.history = []

        def get_verbosity(self):
            return self._verbosity

        def set_verbosity(self, value):
            self.history.append(value)
            self._verbosity = value

    fake_logging = FakeLogging()
    fake_optuna = ModuleType("optuna")
    fake_optuna.logging = fake_logging
    monkeypatch.setitem(sys.modules, "optuna", fake_optuna)

    observed = {}

    class FakeTuner:
        def run(self):
            observed["verbosity_during_run"] = fake_logging.get_verbosity()
            warnings.warn(
                "The groups parameter is ignored by StratifiedKFold",
                UserWarning,
            )

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        _run_official_tuner(FakeTuner())

    assert observed["verbosity_during_run"] == fake_logging.WARNING
    assert fake_logging.get_verbosity() == 20
    assert fake_logging.history == [fake_logging.WARNING, 20]
    assert recorded == []


def test_noop_tuning_strategy_accepts_pipeline_learning_rate():
    summary = NoOpTuningStrategy().tune(
        pd.DataFrame({"age": [50, 60, 70, 80]}),
        pd.Series([0, 0, 1, 1]),
        [],
        random_seed=7,
        learning_rate=0.12,
    )

    assert summary.source == "noop"
    assert summary.params["learning_rate"] == 0.12
    assert summary.params["seed"] == 7


def test_threshold_isolation_uses_requested_size():
    X = pd.DataFrame(
        {
            "age": list(range(100)),
            "sysBP": list(range(100, 200)),
        }
    )
    y = pd.Series([0, 1] * 50)
    trainer = (
        LightGBMTrainer({}, [], random_seed=7)
        .with_threshold_isolation(0.25)
    )

    data = trainer.build_data(X, y, X, y)

    assert len(data.X_threshold) == 25
