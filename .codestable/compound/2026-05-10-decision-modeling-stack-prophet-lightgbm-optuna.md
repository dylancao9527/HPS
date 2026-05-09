---
doc_type: decision
category: tech-stack
date: "2026-05-10"
slug: modeling-stack-prophet-lightgbm-optuna
status: active
area: modeling
tags: [prophet, lightgbm, optuna, lightgbmtunercv, scikit-learn]
---

## 背景

系统论文和核心能力围绕高血压风险预测展开，需要同时支撑血压趋势预测、风险分类、模型训练评估和可复现实验。现有架构文档、README、训练指南和后端依赖均固定了 Prophet 与 LightGBM 相关模型栈。

## 决定

模型与训练栈采用 `Prophet + LightGBM + scikit-learn + Optuna / LightGBMTunerCV`；数据处理使用 `pandas` 和 `numpy`，模型资产序列化使用 `joblib`。

## 理由

Prophet 用于血压趋势预测，LightGBM 用于风险分类，scikit-learn 支撑训练评估流程，Optuna 与 LightGBMTunerCV 作为 LightGBM 自动调参主路径。该选型与现有双模型预测链路、训练脚本、评价报告和论文叙述主线保持一致。

## 考虑过的替代方案

现有文档未记录其他时序模型、分类模型或调参框架的系统性对比；本条归档当前已拍板和已实现的模型技术栈。具体 Prophet 与 LightGBM 串联方式见相关架构 decision。

## 后果

- 预测功能和论文说明应继续围绕 Prophet 趋势预测与 LightGBM 风险分类组织。
- 模型训练优先复用现有 `train_models.py`、评价脚本和训练指南，不另起独立训练框架。
- 使用 `LightGBMTunerCV` 调参时可能耗时较长，手动中断不代表系统逻辑错误。

## 相关文档

- `README.md`
- `docs/training_guide.md`
- `backend/pyproject.toml`
- `.codestable/architecture/ARCHITECTURE.md`
- `.codestable/compound/2026-05-09-decision-prophet-lightgbm-sequential-prediction-pipeline.md`
- `.codestable/attention.md`
