---
doc_type: audit-finding
audit: 2026-05-17-lightgbm-training-script
finding_id: "maintainability-03"
nature: maintainability
severity: P2
confidence: high
suggested_action: cs-refactor
status: open
---

# Finding 03：参数 JSON 缺少严格 schema 与取值校验

## 速答

`--params` 加载的 JSON 只用 `dict.get()` 填充 dataclass，没有未知字段提示、类型转换或范围校验；参数拼错可能静默失效，非法取值会在训练深处才报错。

## 关键证据

- `backend/training/config.py:41` - `TrainingConfig.from_dict()` 直接从原始 dict 构造配置。
- `backend/training/config.py:44` - `seed=data.get("seed", 42)` 这类写法会忽略未知键，也不会校验类型。
- `backend/training/config.py:47` - `cv_splits` 未校验是否为整数且大于等于 2。
- `backend/training/config.py:50` - `threshold_search_mode` 未校验枚举值。
- `backend/scripts/train_models.py:125` - CLI 加载参数后直接进入训练，没有显式 `config.validate()`。
- `backend/training/metrics.py:127` - 非 `recall_priority` 的策略会走 else 分支，拼错的策略名实际会按类似 `f1` 的逻辑执行。

## 影响

实验人员可能在 JSON 里写入拼错字段或非法值，例如 `threshold_search_mode: "recall-priority"`、`cv_splits: 1`、`test_size: 0.95`。一部分会静默变成非预期策略，一部分会等到 sklearn/LightGBM 阶段才失败，降低对照实验可复现性，也增加排查成本。

## 修复方向

给 `TrainingConfig` 增加严格加载流程：拒绝未知字段，显式转换 `multi_seed_audit_seeds` 为整数 tuple，校验比例范围、枚举值、CV 折数、早停轮数与最大轮数关系，并在 `--save-params` 生成带注释说明的示例文档或旁路 guide。

## 建议动作

`cs-refactor`，因为主要是配置解析与错误提示的结构性收紧，行为目标清晰且适合补单元测试。
