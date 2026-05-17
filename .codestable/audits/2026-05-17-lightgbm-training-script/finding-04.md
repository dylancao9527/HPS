---
doc_type: audit-finding
audit: 2026-05-17-lightgbm-training-script
finding_id: "security-04"
nature: security
severity: P2
confidence: medium
suggested_action: cs-issue
status: open
---

# Finding 04：训练数据缺少二值标签与取值范围约束，存在数据污染入口

## 速答

训练数据读取只做数值 coercion 和必要列检查，没有校验 `Risk` 是否严格为 0/1，也没有校验二值特征和生理指标范围；被污染的 CSV 可能进入训练或导致训练中途失败。

## 关键证据

- `backend/training/data.py:77` - 特征列和目标列统一 `pd.to_numeric(..., errors="coerce")`。
- `backend/training/data.py:80` - 只丢弃 `Risk` 为空的样本，没有检查 `Risk` 是否属于 `{0, 1}`。
- `backend/training/data.py:89` - 二值类别特征直接 `astype("category")`，没有限制只能是 0/1。
- `backend/training/data.py:263` - `X = merged[feature_columns].copy()` 之前没有范围/异常值过滤。
- `backend/training/data.py:264` - `y = merged[MODEL_TARGET_COLUMN].astype(int)` 会把已通过 coercion 的目标直接转成整数。
- `backend/prediction/infrastructure/risk_model_gateway.py:37` - 推理侧类别特征固定成 `pd.Categorical(..., categories=[0, 1])`，说明线上契约实际只接受 0/1 类别。

## 影响

当前默认基础数据集可能是干净的，所以这不是必现问题；但系统导出样本、手工合并 CSV 或后续数据源扩展一旦出现 `Risk=2`、`currentSmoker=9`、负年龄、异常血压等值，训练脚本不会在入口处给出清晰拦截。轻则训练失败位置靠后，重则污染模型参数和特征重要性，形成模型供应链层面的数据污染风险。

## 修复方向

在 `_read_training_frame()` 或独立 `validate_training_frame()` 中增加数据质量门禁：`Risk` 严格 0/1，二值特征只能 0/1/缺失，连续字段按医学和数据集口径设置宽松范围；输出 invalid-row summary，超过阈值直接失败，少量异常行进入隔离报告。

## 建议动作

`cs-issue`，因为这是训练入口数据安全和模型质量问题，应补最小复现 CSV 单测，确认异常标签和异常类别不会静默进入训练。
