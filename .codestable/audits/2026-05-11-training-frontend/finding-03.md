---
doc_type: audit-finding
audit: 2026-05-11-training-frontend
finding_id: "bug-03"
nature: bug
severity: P2
confidence: high
suggested_action: cs-issue
status: fixed
---

# Finding 03：dataset_hash 会随随机 seed 改变而非只反映数据内容

## 速答

训练数据 hash 在随机打乱之后生成，导致同一份数据只要 seed 不同，`dataset_hash` 就可能不同，削弱训练产物追踪语义。

## 关键证据

- `backend/training/data.py:135` — `_build_dataset_hash()` 直接把 `merged[_HASH_COLUMNS]` 转成 record list。
- `backend/training/data.py:140` — JSON payload 使用 `to_dict(orient="records")`，记录顺序会参与 hash。
- `backend/training/data.py:197` — `dataset_summary` 中的 `dataset_hash` 来自 `_build_dataset_hash(merged)`。
- `backend/training/data.py:239` — 在生成 summary 前，`merged` 已经执行 `sample(frac=1, random_state=random_seed)`。

## 影响

同一基础数据集和系统导出样本，在仅修改 `--seed` 做多随机种子实验时，dataset hash 可能变化。这样 `training_meta.json` 和 `model_config.json` 中的 hash 不再只代表数据内容，也会混入训练随机性，后续比较实验时容易误判数据集版本发生变化。

## 修复方向

在 shuffle 前生成 dataset hash，或对 `_HASH_COLUMNS` 按稳定键排序后再 hash；hash 只反映数据内容和标签来源，不反映训练 seed。

## 建议动作

`cs-issue`，因为这是训练产物可追踪性 bug，适合补一个“同数据不同 seed hash 不变”的单测。
