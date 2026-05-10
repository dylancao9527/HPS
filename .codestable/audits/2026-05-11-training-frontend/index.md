---
doc_type: audit-index
audit: 2026-05-11-training-frontend
scope: Backend training pipeline and frontend application code.
created: 2026-05-11
status: fixed
total_findings: 5
---

# training-frontend 审计报告

## 范围

本次审计范围为 `backend/training/` 的 LightGBM 训练、数据准备、报告产物逻辑，以及 `frontend/` 的 React 页面、API 封装、鉴权状态、管理员治理与用户交互代码。架构偏离判断对照了 `.codestable/architecture/ARCHITECTURE.md` 中“训练脚本参数可复现”“前端页面 + features 分层”和预测链路治理相关说明。

## 总评

共发现 5 条问题：P1 2 条、P2 3 条；性质分布为 bug 3 条、security 1 条、maintainability 1 条。最值得优先处理的是历史页批量删除可能删除当前筛选/分页不可见的旧选中记录，以及训练参数文件里的 `max_boost_rounds` / `early_stopping_rounds` 没有进入 LightGBMTunerCV 调参阶段。整体看，训练和前端已有测试与模块拆分基础，但个别“实验可复现”和“高风险用户操作”边界还需要收紧。

## 发现清单

| # | 性质 | 严重度 | 置信度 | 标题 | 文件 |
|---|---|---|---|---|---|
| 1 | bug | P1 | high | 预测历史批量删除会带上当前页不可见的旧选中项 | [finding-01.md](finding-01.md) |
| 2 | bug | P1 | high | 训练参数文件无法控制 LightGBMTunerCV 的轮数与早停 | [finding-02.md](finding-02.md) |
| 3 | bug | P2 | high | dataset_hash 会随随机 seed 改变而非只反映数据内容 | [finding-03.md](finding-03.md) |
| 4 | security | P2 | medium | 前端展示本地模拟邮箱验证码缺少环境闸门 | [finding-04.md](finding-04.md) |
| 5 | maintainability | P2 | high | ProfileFormContent 聚合四类表单和密码流程，维护成本偏高 | [finding-05.md](finding-05.md) |

## 按维度分布

| 性质 | P0 | P1 | P2 | 合计 |
|---|---|---|---|---|
| bug | 0 | 2 | 1 | 3 |
| security | 0 | 0 | 1 | 1 |
| performance | 0 | 0 | 0 | 0 |
| maintainability | 0 | 0 | 1 | 1 |
| arch-drift | 0 | 0 | 0 | 0 |
| **合计** | **0** | **2** | **3** | **5** |

## 修复结果

- 5 条发现已全部修复，闭环记录见 [fix-note.md](fix-note.md)。
- 训练侧补齐调参参数透传与 dataset hash 稳定性测试。
- 前端补齐历史页批量删除边界、模拟邮箱验证码环境闸门，以及 ProfileForm hook 拆分。
