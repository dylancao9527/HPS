import json
from pathlib import Path

import lightgbm as lgb

from training.ml_schema import (
    MODEL_CATEGORICAL_FEATURES,
    MODEL_FEATURE_COLUMNS,
    MODEL_SCHEMA_VERSION,
    build_feature_contract_hash,
)
from prediction.domain.risk_policy import INFERENCE_BP_MEDS_POLICY


ML_MODELS_DIR = Path(__file__).resolve().parents[2] / "ml_models"
REQUIRED_MODEL_CONFIG_KEYS = {
    "feature_columns",
    "categorical_features",
    "best_iteration",
    "classification_threshold",
    "threshold_search_mode",
    "threshold_min_recall",
    "base_dataset",
    "schema_version",
    "feature_contract_hash",
    "bp_meds_policy",
    "label_mode",
    "dataset_hash",
    "training_code_version",
}


def _validate_model_config(config):
    missing = REQUIRED_MODEL_CONFIG_KEYS - set(config)
    if missing:
        raise RuntimeError(f"model_config.json 缺少必要字段: {sorted(missing)}")
    if config["schema_version"] != MODEL_SCHEMA_VERSION:
        raise RuntimeError(
            f"model_config schema_version={config['schema_version']} 与代码期望 {MODEL_SCHEMA_VERSION} 不一致"
        )
    expected_hash = build_feature_contract_hash(
        config.get("feature_columns", MODEL_FEATURE_COLUMNS),
        config.get("categorical_features", MODEL_CATEGORICAL_FEATURES),
    )
    if config["feature_contract_hash"] != expected_hash:
        raise RuntimeError("model_config feature_contract_hash 与当前代码不一致")
    if config["bp_meds_policy"] != INFERENCE_BP_MEDS_POLICY:
        raise RuntimeError(
            f"model_config bp_meds_policy={config['bp_meds_policy']} 与线上推理策略 {INFERENCE_BP_MEDS_POLICY} 不一致"
        )
    return config


class ModelRegistry:
    """LightGBM 模型注册表。

    封装模型文件加载、配置验证和懒初始化。
    支持依赖注入（测试传入 models_dir）和模块级单例（生产直接调用顶层函数）。
    """

    def __init__(self, models_dir=None):
        self._models_dir = Path(models_dir) if models_dir else ML_MODELS_DIR
        self._lgbm_model = None
        self._model_config = None

    def get_lgbm_model(self):
        if self._lgbm_model is None:
            txt_path = self._models_dir / "lgbm_model.txt"
            self._lgbm_model = lgb.Booster(model_file=str(txt_path))
        return self._lgbm_model

    def get_model_config(self):
        if self._model_config is None:
            with open(
                self._models_dir / "model_config.json", "r", encoding="utf-8"
            ) as f:
                self._model_config = _validate_model_config(json.load(f))
        return self._model_config

    def reset(self):
        """Clear cached model and config (useful in tests)."""
        self._lgbm_model = None
        self._model_config = None


# Module-level singleton — backward compatible with existing callers.
_default_registry = ModelRegistry()

get_lgbm_model = _default_registry.get_lgbm_model
get_model_config = _default_registry.get_model_config
