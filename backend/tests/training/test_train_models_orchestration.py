from types import SimpleNamespace
import sys

import scripts.train_models as train_models
from training import pipeline
from training.config import SEED, TrainingConfig


def _make_fake_trainer_class(calls):
    class FakeTrainer:
        @staticmethod
        def evaluate(model, X_eval, y_eval, threshold=0.5):
            calls.append(("evaluate", threshold))
            return {
                "auc": 0.93,
                "recall": 0.86,
                "f1": 0.88,
                "threshold": threshold,
            }

        def __init__(
            self, params, categorical_features,
            missing_value_strategy="native", random_seed=SEED,
            max_boost_rounds=2000, early_stopping_rounds=100,
            validation_size=0.1,
        ):
            calls.append(("trainer_init", random_seed))

        def with_threshold_isolation(self, size=0.1):
            calls.append(("threshold_isolation", size))
            return self

        def build_data(self, X_train, y_train, X_test, y_test):
            calls.append(("build_data", len(X_test)))
            return SimpleNamespace(
                X_fit=["f"], y_fit=[1],
                X_valid=["v"], y_valid=[0],
                X_test=["t"], y_test=[0],
                X_threshold=["h"], y_threshold=[0],
                X_model_pool=["m"], y_model_pool=[1],
                frame_dict=lambda: {
                    "X_fit": ["f"], "X_valid": ["v"], "X_test": ["t"],
                    "X_threshold": ["h"], "X_model_pool": ["m"],
                },
            )

        def train(self, X_fit, y_fit, X_valid, y_valid):
            calls.append(("train",))
            return SimpleNamespace(
                model=SimpleNamespace(name="model"),
                best_iteration=312,
                scale_pos_weight=1.0,
            )

        def refit(self, X_pool, y_pool, best_iteration):
            calls.append(("refit", best_iteration))
            return SimpleNamespace(name="optimized")

    return FakeTrainer


def test_run_training_orchestrates_training_without_real_lightgbm(monkeypatch, capsys):
    calls = []
    captured = {}

    def fake_prepare_lgbm_data(
        random_seed,
        bp_meds_policy="neutralized_for_conservative_inference",
        label_mode="diagnosis_plus_rule",
    ):
        calls.append(("prepare", random_seed))
        dataset_summary = {
            "bp_meds_policy": bp_meds_policy,
            "label_mode": label_mode,
            "dataset_hash": "hash-123",
        }
        return ["x1", "x2"], [0, 1], ["age", "bmi"], ["bp_meds"], dataset_summary

    def fake_split_train_test(X, y, random_seed, test_size=0.2):
        calls.append(("split", random_seed, test_size, tuple(X), tuple(y)))
        return ["x-train"], ["x-test"], [1], [0]

    def make_fake_strategy():
        class FakeStrategy:
            def tune(
                self, X_train, y_train, categorical_features,
                random_seed, learning_rate=0.05,
                max_boost_rounds=1000,
                early_stopping_rounds=50,
                cv_splits=5,
            ):
                _ = max_boost_rounds, early_stopping_rounds, cv_splits
                calls.append(("tune", random_seed))
                return SimpleNamespace(
                    params={"objective": "binary"},
                    cv_auc=0.91,
                    best_iteration=12,
                    tuner_name="LightGBMTunerCV",
                    n_splits=5,
                    scale_pos_weight=1.0,
                    official_tuning=True,
                )
        return FakeStrategy()

    def fake_apply_missing_value_strategy(X_fit, named_frames, strategy="native"):
        calls.append(("missing_value",))
        return named_frames.copy(), None, "native"

    def fake_find_best_threshold(model, X_valid, y_valid, **kwargs):
        calls.append(("find_threshold",))
        return {"threshold": 0.42, "precision": 0.89, "recall": 0.85, "f1": 0.87}

    def fake_save_final_model(model, feature_columns, categorical_features, threshold, **kwargs):
        calls.append(("save_model", model.name, tuple(feature_columns), threshold))
        captured["save_model"] = kwargs

    def fake_save_training_meta(
        dataset_summary,
        split_summary,
        baseline_metrics,
        tuning_summary,
        optimized_metrics,
        feature_columns,
        optimized_model,
        **kwargs,
    ):
        calls.append(("save_meta", tuning_summary.tuner_name, optimized_metrics["auc"]))
        captured["split_summary"] = split_summary
        captured["tuning_summary"] = tuning_summary

    def fake_generate_report(*args, **kwargs):
        calls.append(("report", args[5].cv_auc))

    FakeTrainer = _make_fake_trainer_class(calls)

    monkeypatch.setattr(pipeline, "prepare_lgbm_data", fake_prepare_lgbm_data)
    monkeypatch.setattr(pipeline, "split_train_test", fake_split_train_test)
    monkeypatch.setattr(pipeline, "LightGBMTrainer", FakeTrainer)
    monkeypatch.setattr(pipeline, "apply_missing_value_strategy", fake_apply_missing_value_strategy)
    monkeypatch.setattr(pipeline, "find_best_threshold", fake_find_best_threshold)
    monkeypatch.setattr(pipeline, "save_final_model", fake_save_final_model)
    monkeypatch.setattr(pipeline, "save_training_meta", fake_save_training_meta)
    monkeypatch.setattr(pipeline, "generate_report", fake_generate_report)

    fake_strategy = make_fake_strategy()
    pipeline.run_training(random_seed=7, tuning_strategy=fake_strategy)

    assert [call[0] for call in calls] == [
        "prepare",
        "split",
        # Baseline now uses _train_final_cycle (same as Tuned)
        "trainer_init",
        "threshold_isolation",
        "build_data",
        "missing_value",
        "train",
        "refit",
        "find_threshold",
        "evaluate",
        # Tuned
        "tune",
        "trainer_init",
        "threshold_isolation",
        "build_data",
        "missing_value",
        "train",
        "refit",
        "find_threshold",
        "evaluate",
        "save_model",
        "save_meta",
        "report",
    ]
    assert captured["split_summary"]["train_rows"] == 1
    assert captured["split_summary"]["test_rows"] == 1
    assert captured["split_summary"]["final_refit_rows"] == 1
    assert captured["save_model"] == {
        "bp_meds_policy": "neutralized_for_conservative_inference",
        "label_mode": "diagnosis_plus_rule",
        "dataset_hash": "hash-123",
        "missing_value_strategy": "native",
        "threshold_search_mode": "recall_priority",
        "threshold_min_recall": 0.75,
    }
    assert captured["tuning_summary"].tuner_name == "LightGBMTunerCV"
    assert captured["tuning_summary"].official_tuning is True

    output = capsys.readouterr().out
    assert "1/5 数据准备  running  seed=7" in output
    assert "1/5 数据准备  done  rows=2 pos=50.0%" in output
    assert "2/5 Baseline  done  auc=0.9300 recall=0.8600" in output
    assert "3/5 官方调优  running  LightGBMTunerCV" in output
    assert "3/5 官方调优  done  cv_auc=0.9100 best_iteration=12" in output
    assert "4/5 最终训练  done  auc=0.9300 recall=0.8600 f1=0.8800 threshold=0.4200" in output
    assert "5/5 保存产物  done  artifacts=lgbm_model.txt model_config.json training_meta.json model_report.md" in output
    assert "调参范围" not in output
    assert "lambda_l1" not in output


def test_parse_args_uses_project_default_seed():
    args = train_models.parse_args([])

    assert args.seed is None
    assert args.random_seed is False
    assert train_models.resolve_random_seed(args) == SEED


def test_parse_args_accepts_explicit_seed():
    args = train_models.parse_args(["--seed", "7"])

    assert train_models.resolve_random_seed(args) == 7


def test_main_uses_random_seed_when_requested(monkeypatch, capsys):
    calls = []

    monkeypatch.setattr(train_models.secrets, "randbelow", lambda upper: 123456)
    monkeypatch.setattr(train_models, "run_training", lambda random_seed, **kw: calls.append(random_seed))

    train_models.main(["--random-seed"])

    assert calls == [123456]
    output = capsys.readouterr().out
    assert "高血压风险预测系统 — 模型训练" in output
    assert "训练完成。" in output
    assert "本次训练使用 seed: 123456" in output


def test_main_reports_explicit_seed_after_training(monkeypatch, capsys):
    calls = []

    monkeypatch.setattr(train_models, "run_training", lambda random_seed, **kw: calls.append(random_seed))

    train_models.main(["--seed", "7"])

    assert calls == [7]
    output = capsys.readouterr().out
    assert "训练完成。" in output
    assert "本次训练使用 seed: 7" in output


def test_main_keeps_training_export_as_separate_step(monkeypatch):
    calls = []

    export_module = SimpleNamespace(
        run_local_training_export=lambda **kwargs: calls.append(("export", kwargs))
    )
    monkeypatch.setitem(sys.modules, "export_training_data", export_module)
    monkeypatch.setattr(
        train_models,
        "run_training",
        lambda random_seed, **kw: calls.append(("train", random_seed)),
    )

    train_models.main(["--seed", "7"])

    assert calls == [("train", 7)]


def test_main_uses_params_seed_when_cli_seed_is_not_explicit(monkeypatch, tmp_path):
    params_path = tmp_path / "training.json"
    TrainingConfig(seed=99).save(params_path)
    calls = []

    monkeypatch.setattr(
        train_models,
        "run_training",
        lambda random_seed, **kw: calls.append((random_seed, kw["config"].seed)),
    )

    train_models.main(["--params", str(params_path)])

    assert calls == [(99, 99)]


def test_run_training_passes_config_values_through_orchestration(monkeypatch):
    calls = []
    captured = {}

    def fake_prepare_lgbm_data(random_seed, bp_meds_policy, label_mode):
        captured["data_config"] = (bp_meds_policy, label_mode)
        dataset_summary = {
            "bp_meds_policy": bp_meds_policy,
            "label_mode": label_mode,
            "dataset_hash": "hash-456",
        }
        return ["x1", "x2"], [0, 1], ["age", "bmi"], ["bp_meds"], dataset_summary

    def fake_split_train_test(X, y, random_seed, test_size):
        captured["test_size"] = test_size
        return ["x-train"], ["x-test"], [1], [0]

    class FakeStrategy:
        def tune(
            self, X_train, y_train, categorical_features,
            random_seed, learning_rate=0.05,
            max_boost_rounds=1000,
            early_stopping_rounds=50,
            cv_splits=5,
        ):
            _ = max_boost_rounds, early_stopping_rounds
            captured["learning_rate"] = learning_rate
            captured["cv_splits"] = cv_splits
            return SimpleNamespace(
                params={"objective": "binary"},
                cv_auc=0.91,
                best_iteration=12,
                tuner_name="NoOp",
                n_splits=5,
                scale_pos_weight=1.0,
                official_tuning=False,
                to_dict=lambda: {},
            )

    FakeTrainer = _make_fake_trainer_class(calls)

    def fake_apply_missing_value_strategy(X_fit, named_frames, strategy="native"):
        captured.setdefault("missing_strategies", []).append(strategy)
        return named_frames.copy(), {"age": 50}, strategy

    def fake_find_best_threshold(model, X_valid, y_valid, **kwargs):
        captured["threshold_kwargs"] = kwargs
        return {"threshold": 0.42, "precision": 0.89, "recall": 0.85, "f1": 0.87}

    monkeypatch.setattr(pipeline, "prepare_lgbm_data", fake_prepare_lgbm_data)
    monkeypatch.setattr(pipeline, "split_train_test", fake_split_train_test)
    monkeypatch.setattr(pipeline, "LightGBMTrainer", FakeTrainer)
    monkeypatch.setattr(pipeline, "apply_missing_value_strategy", fake_apply_missing_value_strategy)
    monkeypatch.setattr(pipeline, "find_best_threshold", fake_find_best_threshold)
    monkeypatch.setattr(
        pipeline,
        "save_final_model",
        lambda *args, **kwargs: captured.setdefault("save_model_kwargs", kwargs),
    )
    monkeypatch.setattr(pipeline, "save_training_meta", lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline, "generate_report", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        pipeline,
        "run_feature_ablation",
        lambda *args, **kwargs: captured.setdefault("feature_ablation_config", kwargs["config"]) or [],
    )
    monkeypatch.setattr(
        pipeline,
        "run_multi_seed_audit",
        lambda *args, **kwargs: captured.setdefault("multi_seed_args", (args[3], kwargs["config"])) or {"runs": []},
    )

    config = TrainingConfig(
        test_size=0.33,
        threshold_valid_size=0.22,
        cv_splits=3,
        threshold_search_mode="f1",
        threshold_min_recall=0.55,
        missing_value_strategy="median_impute",
        learning_rate=0.12,
        bp_meds_policy="observed",
        label_mode="diagnosis_only",
        enable_feature_ablation=True,
        multi_seed_audit_seeds=(11, 13),
    )

    pipeline.run_training(
        random_seed=7,
        tuning_strategy=FakeStrategy(),
        config=config,
    )

    assert captured["data_config"] == ("observed", "diagnosis_only")
    assert captured["test_size"] == 0.33
    assert captured["learning_rate"] == 0.12
    assert captured["cv_splits"] == 3
    assert captured["missing_strategies"] == ["median_impute", "median_impute"]
    assert captured["threshold_kwargs"] == {"strategy": "f1", "min_recall": 0.55}
    assert ("threshold_isolation", 0.22) in calls
    assert captured["feature_ablation_config"] is config
    assert captured["multi_seed_args"] == ((11, 13), config)
    assert captured["save_model_kwargs"]["threshold_search_mode"] == "f1"
    assert captured["save_model_kwargs"]["threshold_min_recall"] == 0.55


def test_run_training_passes_boosting_window_to_tuning_strategy(monkeypatch):
    calls = []
    captured = {}

    def fake_prepare_lgbm_data(random_seed, bp_meds_policy, label_mode):
        return (
            ["x1", "x2"],
            [0, 1],
            ["age", "bmi"],
            ["bp_meds"],
            {
                "bp_meds_policy": bp_meds_policy,
                "label_mode": label_mode,
                "dataset_hash": "hash-boosting-window",
            },
        )

    class FakeStrategy:
        def tune(
            self,
            X_train,
            y_train,
            categorical_features,
            random_seed,
            learning_rate=0.05,
            max_boost_rounds=1000,
            early_stopping_rounds=50,
            cv_splits=5,
        ):
            captured["tuning_window"] = (
                max_boost_rounds,
                early_stopping_rounds,
                cv_splits,
            )
            return SimpleNamespace(
                params={"objective": "binary"},
                cv_auc=0.91,
                best_iteration=12,
                tuner_name="LightGBMTunerCV",
                n_splits=5,
                scale_pos_weight=1.0,
                official_tuning=True,
                to_dict=lambda: {},
            )

    monkeypatch.setattr(pipeline, "prepare_lgbm_data", fake_prepare_lgbm_data)
    monkeypatch.setattr(
        pipeline,
        "split_train_test",
        lambda X, y, random_seed, test_size: (["x-train"], ["x-test"], [1], [0]),
    )
    monkeypatch.setattr(pipeline, "LightGBMTrainer", _make_fake_trainer_class(calls))
    monkeypatch.setattr(
        pipeline,
        "apply_missing_value_strategy",
        lambda X_fit, named_frames, strategy="native": (
            named_frames.copy(),
            None,
            strategy,
        ),
    )
    monkeypatch.setattr(
        pipeline,
        "find_best_threshold",
        lambda *args, **kwargs: {
            "threshold": 0.42,
            "precision": 0.89,
            "recall": 0.85,
            "f1": 0.87,
        },
    )
    monkeypatch.setattr(pipeline, "save_final_model", lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline, "save_training_meta", lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline, "generate_report", lambda *args, **kwargs: None)

    pipeline.run_training(
        random_seed=7,
        tuning_strategy=FakeStrategy(),
        config=TrainingConfig(max_boost_rounds=345, early_stopping_rounds=23, cv_splits=4),
    )

    assert captured["tuning_window"] == (345, 23, 4)
