# HPS 架构深化 Issue 草稿

生成时间：2026-05-05

发布目标：`honestman9527/HPS`

统一标签：`needs-triage`

发布状态：已发布。当前 Codex 进程的 PATH 仍未包含 `gh`，本次使用完整路径 `C:\Program Files\GitHub CLI\gh.exe` 发布。

已发布链接：

- #2 建立架构深化基线与保护网：https://github.com/honestman9527/HPS/issues/2
- #3 收敛前端高血压风险展示语言：https://github.com/honestman9527/HPS/issues/3
- #4 收敛 prediction freshness 策略：https://github.com/honestman9527/HPS/issues/4
- #5 深化指南型健康建议安全边界：https://github.com/honestman9527/HPS/issues/5
- #6 深化预测记录读写映射：https://github.com/honestman9527/HPS/issues/6
- #7 深化 Prophet 模型生命周期模块：https://github.com/honestman9527/HPS/issues/7
- #8 深化双模型预测引擎 run module：https://github.com/honestman9527/HPS/issues/8

## 建议发布顺序

1. 建立架构深化基线与保护网
2. 收敛前端高血压风险展示语言
3. 收敛 prediction freshness 策略
4. 深化指南型健康建议安全边界
5. 深化预测记录读写映射
6. 深化 Prophet 模型生命周期模块
7. 深化双模型预测引擎 run module

## 1. 建立架构深化基线与保护网

Type: AFK

Blocked by: None - can start immediately

User stories covered: 管理员与普通用户的现有预测、历史、治理关键路径在后续架构深化前有可回归的质量基线。

```markdown
## What to build

为架构深化工作建立后端与前端基线，记录当前测试、类型检查、静态检查状态，并沉淀需要保护的领域词，避免后续重构把既有失败误判为新问题。

## Acceptance criteria

- [ ] 后端测试基线已运行并记录，命令优先使用 `cd backend; uv run pytest`。
- [ ] 前端 `typecheck`、`lint`、`test` 基线已运行并记录，命令来自 `frontend/package.json`。
- [ ] 已记录既有失败、环境限制或跳过原因，后续 issue 可引用该基线。
- [ ] 已建立领域词保护清单，至少包含高血压风险概率、风险等级、血压趋势预测、指南型健康建议、预测记录、预测结果治理。

## Blocked by

None - can start immediately
```

## 2. 收敛前端高血压风险展示语言

Type: AFK

Blocked by: 建立架构深化基线与保护网

User stories covered: 普通用户查看预测结果与历史记录、管理员查看预测结果治理时，看到一致且不越界的风险表达。

```markdown
## What to build

集中前端风险展示规则，让预测页、历史页、管理员治理页和个人档案相关展示共用一致的风险等级、风险概率、置信度和趋势文案，并移除“临床风险等级”等不符合领域边界的表述。

## Acceptance criteria

- [ ] 新增或复用共享展示模块，集中处理风险等级、风险概率、置信度标签和趋势文案。
- [ ] `prediction`、`history`、`admin`、`profile` 中重复或冲突的风险展示逻辑已收敛到共享规则。
- [ ] 前端界面不出现“临床风险等级”“确诊概率”“医生诊断”等越界表述。
- [ ] 前端 `typecheck` 通过；涉及页面的预测页、历史页、管理员治理页关键路径已在浏览器验证。

## Blocked by

- 建立架构深化基线与保护网
```

## 3. 收敛 prediction freshness 策略

Type: AFK

Blocked by: 建立架构深化基线与保护网

User stories covered: 普通用户每次发起预测都得到本次重新生成的预测结果；管理员可追溯每次不可变预测记录。

```markdown
## What to build

对齐 ADR-0001 与架构文档：系统可以复用 Prophet 模型，但不直接复用旧 prediction result。清理或隔离旧结果 replay 路径，让“模型复用”“重新生成结果”“预测记录创建”成为清晰策略。

## Acceptance criteria

- [ ] 每次执行预测都会保存新的预测记录，不直接返回旧 prediction result 作为本次结果。
- [ ] Prophet 模型复用仍能通过 `model_strategy` 或训练元信息解释。
- [ ] 旧 prediction result replay 路径已删除、隔离或明确标记为兼容路径，调用方不会误用。
- [ ] 相关 cache key/freshness 测试改为描述当前策略，而不是历史结果复用策略。

## Blocked by

- 建立架构深化基线与保护网
```

## 4. 深化指南型健康建议安全边界

Type: AFK

Blocked by: 收敛 prediction freshness 策略

User stories covered: 普通用户获得基于中国高血压防治指南（2024年修订版）的健康建议，且系统不输出临床诊断或处方语义。

```markdown
## What to build

把指南型健康建议信号从 `user_data` 隐式字段中提取为显式输入，在建议模块内集中执行 topic 分组、priority 选择、confidence notice 合并与 `safety_boundary` 校验，同时保持现有前端建议 payload 兼容。

## Acceptance criteria

- [ ] `_guideline_signal` 不再作为散落的隐式 `user_data` 字段传递，建议生成入口表达清晰。
- [ ] 建议模块集中处理 topic 分组、priority 选择和 confidence notice 合并。
- [ ] `backend/data/guideline_knowledge_base.json` 中 `safety_boundary.avoid_diagnosis` 有测试保护。
- [ ] 建议输出仍为前端已支持的卡片列表，并且不输出临床诊断、药物调整或处方指令。

## Blocked by

- 收敛 prediction freshness 策略
```

## 5. 深化预测记录读写映射

Type: AFK

Blocked by: 收敛 prediction freshness 策略

User stories covered: 普通用户可继续查看历史预测记录；管理员可在预测结果治理中追踪规范化明细；旧记录仍可回放。

```markdown
## What to build

拆清预测记录 normalized storage 的写入映射、读取映射和旧格式兼容回放逻辑，用小型 DTO 或 typed dict 约束输入输出，并把 prediction payload assembly 从 repository 细节中剥离出来。

## Acceptance criteria

- [ ] 新预测记录的输入快照、趋势、融合元信息、置信度原因、指南型健康建议和预测点仍完整规范化保存。
- [ ] 旧预测记录和旧格式 recommendation 仍可被历史页与预测结果治理读取。
- [ ] repository 对展示 payload 细节的了解减少，payload assembly 有更清晰的模块边界。
- [ ] mapper 测试覆盖写入、读取、旧格式兼容三类路径。

## Blocked by

- 收敛 prediction freshness 策略
```

## 6. 深化 Prophet 模型生命周期模块

Type: AFK

Blocked by: 深化预测记录读写映射

User stories covered: 普通用户发起预测时系统稳定复用或重训 Prophet 模型；管理员可通过治理明细理解模型复用与趋势预测说明。

```markdown
## What to build

从 `prophet_gateway.py` 中拆出每日血压序列、训练上下文和模型生命周期策略，封装 `inspect` + `predict` 的顺序约束。调用方只请求血压趋势预测，文件存储与内存缓存继续作为 adapters。

## Acceptance criteria

- [ ] Prophet gateway 的公开 interface 更小，调用方不需要理解内部 inspect/predict 顺序。
- [ ] 每日血压序列、训练上下文和模型生命周期策略具有清晰模块边界。
- [ ] 阈值重训、缓存命中、模型持久化和模型复用但重新生成趋势结果均有测试。
- [ ] 测试减少对私有函数 patch，改为围绕“给定每日血压序列和模型状态，得到趋势预测与 Prophet 预测说明”验证。

## Blocked by

- 深化预测记录读写映射
```

## 7. 深化双模型预测引擎 run module

Type: AFK

Blocked by: 深化指南型健康建议安全边界, 深化 Prophet 模型生命周期模块

User stories covered: 普通用户执行一次完整风险预测时，可以追踪从血压趋势预测到高血压发病风险概率、风险等级、指南型健康建议和预测记录保存的完整链路。

```markdown
## What to build

在前置 seam 稳定后深化 `PredictUseCase`，把用户个人风险因素快照、预测期血压特征、风险融合、指南型健康建议和保存 payload 组装收敛为清晰内部步骤，对外保留 `execute(PredictCommand) -> PredictionResult`。

## Acceptance criteria

- [ ] `PredictUseCase` 对外 interface 不扩大，调用方仍通过 `execute(PredictCommand) -> PredictionResult` 完成预测。
- [ ] 用户个人风险因素快照、预测期血压特征、风险融合、指南型健康建议和保存 payload 组装在一次 prediction run 中可追踪。
- [ ] 端到端 use case 测试覆盖 happy path、缺失 BP 默认值、关闭趋势融合、模型复用说明。
- [ ] 高血压发病风险概率、风险等级、预测记录、指南型健康建议使用项目领域词，不出现临床诊断越界表述。

## Blocked by

- 深化指南型健康建议安全边界
- 深化 Prophet 模型生命周期模块
```
