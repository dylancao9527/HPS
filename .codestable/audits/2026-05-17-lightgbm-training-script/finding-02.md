---
doc_type: audit-finding
audit: 2026-05-17-lightgbm-training-script
finding_id: "bug-02"
nature: bug
severity: P1
confidence: high
suggested_action: cs-issue
status: open
---

# Finding 02：阈值候选集缺少低于最小分数的召回边界

## 速答

阈值搜索只遍历模型输出过的概率值，并用 `>` 做分类判断，因此无法选择 "低于最小预测分数" 的阈值；在 `recall_priority` 模式下，可能错过最高可达召回方案。

## 关键证据

- `backend/training/metrics.py:19` - `_build_threshold_candidates()` 从预测分数的唯一值构造候选阈值。
- `backend/training/metrics.py:23` - 候选只保留 `0.0 < score < 1.0` 的实际分数，没有加入低于最小分数的边界值。
- `backend/training/metrics.py:116` - 分类使用 `(y_pred_proba > threshold)`，等于阈值的样本会被判为负类。
- `backend/training/metrics.py:119` - `recall_priority` 会跳过低于 `min_recall` 的候选。
- `backend/training/metrics.py:147` - 如果所有候选都达不到召回下限，会 fallback 到 `f1` 策略，而不是说明 recall 约束不可满足或尝试全正类边界。

## 影响

如果最低预测分数对应正样本，当前候选集无法表达 "把所有样本都判为正类" 或 "包含最低分正样本" 的阈值方案，导致 recall 下限可能被错误判定为不可达。对高血压风险这种偏召回的场景，阈值策略会偏保守，漏报风险被低估。

## 修复方向

候选阈值改成相邻预测分数的 midpoint，并显式加入低于最小预测分数和高于最大预测分数的边界；或者改用 `>=` 并重新定义保存阈值语义。`threshold_selection` 里增加 `recall_constraint_satisfied` 字段，避免 fallback 后仍看起来像 recall-priority 成功。

## 建议动作

`cs-issue`，因为这是阈值搜索逻辑 bug，应该用小数组单测覆盖 "最低分是正样本" 和 "所有分数相同" 两个边界。
