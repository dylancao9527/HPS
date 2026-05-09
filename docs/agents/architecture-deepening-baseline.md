# HPS 架构深化基线与保护网

关联 issue：https://github.com/honestman9527/HPS/issues/2

记录时间：2026-05-05 13:56 +08:00

## 验证命令基线

| 范围 | 命令 | 结果 | 说明 |
|------|------|------|------|
| 后端 | `cd backend; uv run pytest` | 通过 | 86 passed in 1.42s |
| 前端类型检查 | `cd frontend; pnpm run typecheck` | 通过 | `tsc --noEmit -p tsconfig.json && tsc --noEmit -p tsconfig.node.json` 无错误 |
| 前端 lint | `cd frontend; pnpm run lint` | 失败 | `PredictionInsightPanel.tsx` 存在未使用的 `getConfidenceReasonDetails` import |
| 前端测试 | `cd frontend; pnpm run test` | 失败 | Vitest 未找到测试文件，退出码为 1 |

## 已知基线失败

### 前端 lint

文件：`frontend/src/features/prediction/components/PredictionInsightPanel.tsx`

错误：

```text
5:3  error  'getConfidenceReasonDetails' is defined but never used.
Allowed unused vars must match /^[A-Z_]/u  @typescript-eslint/no-unused-vars
```

后续架构改动如果没有触碰该文件或相关 import，不应把这个 lint 失败误判为新引入问题。

### 前端测试

命令：`cd frontend; pnpm run test`

错误：

```text
No test files found, exiting with code 1
include: **/*.{test,spec}.?(c|m)[jt]s?(x)
exclude: **/node_modules/**, **/.git/**
```

这是当前仓库没有前端测试文件导致的基线失败。后续如果新增前端测试，需要重新记录该命令的基线。

## 领域词保护清单

后续 issues、测试名、文案、接口字段说明和重构提交中，优先使用以下项目领域词。

| 推荐用语 | 保护原因 | 避免用语 |
|----------|----------|----------|
| 高血压风险预测系统 | 系统定位是健康管理辅助，不是临床系统 | 临床诊断系统、医疗决策系统、确诊工具 |
| 双模型预测引擎 | Prophet 与 LightGBM 串联，而不是投票或单模型 | 单模型预测、模型投票 |
| 血压趋势预测 | Prophet 输出未来 7 天血压走势 | 风险预测、诊断结论 |
| 高血压发病风险概率 | LightGBM 输出的未来 7 天风险概率 | 确诊概率、患病诊断、临床发病率 |
| 高血压风险概率 | 面向界面的稳妥简称 | 确诊概率、患病诊断 |
| 预测期血压特征 | Prophet 预测结果转换后的 LightGBM 输入特征 | 原始 Prophet 模型、完整预测曲线 |
| 用户个人风险因素 | 风险评估使用的健康与生活方式特征 | 医生诊断信息、治疗方案 |
| 诊断反馈 | 用户档案中的自报或反馈性健康状态 | 模型标签、预测输入、确诊依据 |
| 普通用户 | 系统面向的记录、预测和查看建议用户 | 患者、病人 |
| 管理员 | 维护用户、导出训练数据、查看治理信息的角色 | 医生、专家、审核员 |
| 血压记录 | 普通用户一次录入的血压和心率数据 | 每日样本、训练样本 |
| 每日血压序列 | 按自然日聚合后的日均血压序列 | 原始血压记录、单次测量 |
| 个人档案 | 普通用户维护的健康风险因素集合 | 账户信息、登录信息 |
| 账户信息 | 登录、身份识别和权限控制信息 | 模型特征、健康档案 |
| 训练数据导出 | 管理员导出补充训练样本的后台能力 | 在线训练、模型发布 |
| 模型训练 | 开发或运维人员运行训练脚本 | 后台一键训练、用户侧预测 |
| LightGBM 性能指标 | 评价风险分类模型的分类指标 | 系统临床准确率、Prophet 准确率 |
| Prophet 预测说明 | 解释趋势预测过程、置信度和训练数据状态 | Prophet 准确率、临床诊断准确率 |
| 风险等级 | 高血压发病风险概率映射后的低/中/高展示层级 | 病情分级、临床分级 |
| 健康建议 | 结合风险和指南依据生成的生活方式建议 | 处方、医嘱、治疗方案 |
| 指南型健康建议 | 基于中国高血压防治指南（2024年修订版）的规则建议 | AI 医生建议、智能诊疗建议、LLM 生成建议、个性化处方 |
| 预测结果治理 | 管理员查看、追踪、导出和审查历史预测明细 | 医疗质控、模型审批、临床审核 |
| 预测记录 | 一次预测产生的不可变历史记录 | 可编辑报告、人工结论 |
| 治理备注 | 未来可追加在预测记录旁的人工说明 | 修改预测结果、覆盖健康建议 |
| 中国高血压防治指南（2024年修订版） | 当前指南型健康建议依据 | 中国高血压防治指南2023 |

## 后续使用方式

- 做 #3 到 #8 时，先查看本文件确认当前验证基线。
- 若某阶段修复了既有基线失败，需要在该阶段更新本文件并说明变化。
- 涉及前端视觉、交互或路由的改动，仍需按 `AGENTS.md` 要求做浏览器关键路径验证。

## 阶段 1 更新

更新时间：2026-05-05 14:09 +08:00

#3 已修复前端 lint 既有失败，并新增首个前端 Vitest 测试文件。因此当前前端基线更新为：

| 范围 | 命令 | 结果 | 说明 |
|------|------|------|------|
| 前端类型检查 | `cd frontend; pnpm run typecheck` | 通过 | 无 TypeScript 错误 |
| 前端 lint | `cd frontend; pnpm run lint` | 通过 | 原 `PredictionInsightPanel.tsx` 未使用 import 已移除 |
| 前端测试 | `cd frontend; pnpm run test` | 通过 | `riskPresentation.test.ts` 4 passed |
