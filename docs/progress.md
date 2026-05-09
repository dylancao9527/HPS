# HPS 架构深化进度

> 注：本文是过程日志。旧 Interface 名称出现在早期阶段中时，只表示当时的执行证据，不代表当前仍然存在或推荐继续使用。

## 2026-05-05

### 本次已完成

- 使用 `improve-codebase-architecture` 检查项目领域文档、ADR 和架构文档。
- 识别 5 个架构深化候选：
  - 双模型预测引擎 run module。
  - Prophet model lifecycle module。
  - Prediction freshness policy cleanup。
  - 指南型健康建议 safety module。
  - Frontend risk presentation module。
- 根据用户要求，将候选拆成阶段化执行计划。
- 创建规划文件：
  - `task_plan.md`
  - `findings.md`
  - `progress.md`

### 尚未执行

- 尚未修改业务代码。
- 尚未运行测试。
- 尚未进入任何阶段实施。

### 下一步

建议从 `task_plan.md` 的阶段 0 开始，先跑后端和前端基线验证。

## 2026-05-05 13:33 +08:00

### 本次已完成

- 使用 `planning-with-files-zh` 恢复 `task_plan.md`、`findings.md`、`progress.md`。
- 使用 `to-issues` 读取 issue tracker、triage labels、领域文档、架构文档和 ADR。
- 根据 `task_plan.md` 将架构深化计划拆成 7 个可发布 issue 草稿。
- 创建 issue 草稿文件：
  - `docs/agents/architecture-deepening-issue-drafts.md`

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| `gh` CLI 不可用 | 1 | 记录阻塞；生成可发布 issue 草稿，等待安装/登录 `gh` 或提供 token 后发布 |
| GitHub REST API 未认证请求 rate limit | 1 | 不继续重复未认证查询；需要认证后再去重和发布 |
| `rg` 启动被 Windows 拒绝访问 | 1 | 改用 PowerShell `Get-ChildItem` 查询文件 |

### 尚未执行

- 尚未发布 GitHub issues，因为当前环境缺少 `gh` CLI 且没有认证 token。
- 尚未运行后端或前端测试；本次只执行 issue 化拆分。

### 下一步

- 用户确认 issue 粒度和依赖关系后，安装并登录 `gh`，或提供可用 `GH_TOKEN`/`GITHUB_TOKEN`，再按草稿顺序发布 issue 并添加 `needs-triage` 标签。

## 2026-05-05 13:40 +08:00

### 本次已完成

- 用户完成 GitHub CLI 登录后，使用完整路径 `C:\Program Files\GitHub CLI\gh.exe` 验证认证状态。
- 发现仓库缺少 `needs-triage` 标签，已创建该标签。
- 检查 open issues 为空，按依赖顺序发布 7 个架构深化 issues：
  - #2 建立架构深化基线与保护网：https://github.com/honestman9527/HPS/issues/2
  - #3 收敛前端高血压风险展示语言：https://github.com/honestman9527/HPS/issues/3
  - #4 收敛 prediction freshness 策略：https://github.com/honestman9527/HPS/issues/4
  - #5 深化指南型健康建议安全边界：https://github.com/honestman9527/HPS/issues/5
  - #6 深化预测记录读写映射：https://github.com/honestman9527/HPS/issues/6
  - #7 深化 Prophet 模型生命周期模块：https://github.com/honestman9527/HPS/issues/7
  - #8 深化双模型预测引擎 run module：https://github.com/honestman9527/HPS/issues/8
- 验证所有 7 个 open issues 均带 `needs-triage` 标签。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| `gh` 已登录但当前 Codex 进程 PATH 仍无法解析 `gh` | 1 | 定位到 `C:\Program Files\GitHub CLI\gh.exe`，改用完整路径执行 |

### 尚未执行

- 尚未运行阶段 0 的后端和前端基线验证。

### 下一步

- 从 #2 / 阶段 0 开始执行基线与保护网。

## 2026-05-05 13:56 +08:00

### 本次已完成

- 使用 `tdd` 流程执行 #2：把现有验证命令作为公开行为接口，先运行命令获取真实基线，再记录保护网。
- 读取 #2 issue 内容，确认验收范围：
  - 后端测试基线。
  - 前端 `typecheck`、`lint`、`test` 基线。
  - 既有失败记录。
  - 领域词保护清单。
- 运行后端基线：
  - `cd backend; uv run pytest`
  - 结果：通过，86 passed in 1.42s。
- 运行前端基线：
  - `cd frontend; pnpm run typecheck`
  - 结果：通过。
  - `cd frontend; pnpm run lint`
  - 结果：失败，`PredictionInsightPanel.tsx` 存在未使用的 `getConfidenceReasonDetails` import。
  - `cd frontend; pnpm run test`
  - 结果：失败，Vitest 未找到测试文件并以 1 退出。
- 创建基线与保护网文档：
  - `docs/agents/architecture-deepening-baseline.md`
- 更新 `task_plan.md`，将阶段 0 标记为 complete。
- 清理 `pnpm run typecheck` 生成的未跟踪缓存文件：
  - `frontend/tsconfig.node.tsbuildinfo`

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| 前端 lint 基线失败：未使用 import | 1 | 记录为既有基线失败，后续涉及该文件时可单独修复 |
| 前端 test 基线失败：无测试文件 | 1 | 记录为既有基线失败，后续新增前端测试后重新记录 |

### 尚未执行

- 尚未修复前端 lint 既有失败。
- 尚未新增前端测试文件。
- 尚未执行 #3 及后续架构深化 issue。

### 下一步

- 在 GitHub issue #2 留言同步基线结果。
- 后续可从 #3 或 #4 开始，执行前先引用 `docs/agents/architecture-deepening-baseline.md`。

### Issue 同步

- 已在 #2 留言同步本地基线结果：https://github.com/honestman9527/HPS/issues/2#issuecomment-4376851278

## 2026-05-05 14:09 +08:00

### 本次已完成

- 执行 #3：收敛前端高血压风险展示语言。
- 新增共享风险展示模块：
  - `frontend/src/features/shared/riskPresentation.ts`
- 新增共享模块行为测试：
  - `frontend/src/features/shared/riskPresentation.test.ts`
- 新增 Vitest setup：
  - `frontend/src/test/setup.ts`
- 替换 prediction/history/admin/profile 中的重复风险展示逻辑：
  - `frontend/src/features/prediction/components/RiskBadge.tsx`
  - `frontend/src/features/prediction/utils.ts`
  - `frontend/src/features/history/utils.ts`
  - `frontend/src/features/history/components/HistoryDetailPanel.tsx`
  - `frontend/src/features/history/components/HistoryList.tsx`
  - `frontend/src/features/history/components/HistoryRecordList.tsx`
  - `frontend/src/features/admin/components/PredictionGovernanceOverview.tsx`
  - `frontend/src/features/admin/components/PredictionAuditTable.tsx`
  - `frontend/src/features/admin/components/PredictionAuditDetailCard.tsx`
  - `frontend/src/features/admin/hooks/usePredictionGovernanceData.ts`
  - `frontend/src/features/profile/components/HealthProfileSection.tsx`
- 修复阶段 0 记录的前端 lint 既有失败：
  - 移除 `PredictionInsightPanel.tsx` 未使用 import。
- 更新 `docs/agents/architecture-deepening-baseline.md`，记录 #3 后前端 lint/test 已变绿。
- 清理 Playwright 和 typecheck 生成的未跟踪缓存：
  - `frontend/.playwright-cli`
  - `frontend/tsconfig.node.tsbuildinfo`

### 验证结果

- `cd frontend; pnpm exec vitest run src/features/shared/riskPresentation.test.ts`：通过，4 passed。
- `cd frontend; pnpm run typecheck`：通过。
- `cd frontend; pnpm run lint`：通过。
- `cd frontend; pnpm run test`：通过，1 test file / 4 tests passed。
- 静态扫描：前端源码未出现“临床风险等级”“确诊概率”“医生诊断”“已确诊”“未确诊”。
- Playwright 浏览器验证：
  - 预测页：mock 预测后出现“高血压风险等级”“高血压风险概率”“置信度：高”，无禁止文案。
  - 历史页：mock 历史记录出现“中风险 (48.6%)”“整体有上升趋势”，无禁止文案。
  - 管理员预测治理页：mock governance 数据将 `high`/`medium` 展示为中文标签，无禁止文案。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| Vitest 配置引用的 `src/test/setup.ts` 不存在 | 1 | 新增最小 setup，并导入 `@testing-library/jest-dom/vitest` |
| Vite 首次启动只监听 IPv6 `::1`，Playwright 访问 `127.0.0.1` 被拒绝 | 1 | 重启 Vite，使用 `pnpm exec vite --host 127.0.0.1 --port 5173` |
| Playwright CLI PowerShell wrapper 参数透传错误导致 `--raw eval` 输出 help | 1 | 改用显式 `ValueFromRemainingArguments` 函数或直接调用 CLI |

### 尚未执行

- 尚未执行 #4 及后续架构深化 issue。

### 下一步

- 在 GitHub issue #3 留言同步实现与验证结果。
- 后续可从 #4 开始执行 prediction freshness 策略收敛。

### Issue 同步

- 已在 #3 留言同步本地实现与验证结果：https://github.com/honestman9527/HPS/issues/3#issuecomment-4376960760

## 2026-05-05 15:14 +08:00

### 本次已完成

- 使用 `tdd` 流程执行 #4：收敛 prediction freshness 策略。
- 新增/调整后端行为测试，确认：
  - 同一用户同一预测条件连续执行预测时，会保存新的预测记录。
  - Prophet 模型复用只通过 `cache_mode="model_reuse"` 表达，预测结果不被标记为旧结果缓存。
  - `PredictUseCase` 不再暴露 `_result_from_records` 旧 replay builder。
  - route freshness service 和 repository 门面不再暴露 `get_reusable_prediction`。
  - freshness key 稳定且对预测天数、模型状态和风险输入敏感。
- 删除后端旧结果复用路径：
  - `PredictionRouteCacheService.get_reusable_prediction`
  - `PredictionRepository.get_reusable_prediction`
  - `PredictionRecordRepository.get_reusable_prediction`
  - `prediction.domain.cache_policy.classify_cache_mode`
- 将 `build_prediction_cache_key` / `_build_result_cache_key` 命名收敛为 freshness key 语义。
- 更新 `task_plan.md`，将阶段 2 标记为 complete。

### 验证结果

- `cd backend; uv run pytest tests/prediction/test_predict_use_case.py tests/routes/test_predictions_cache_helpers.py tests/prediction/test_prediction_repository_boundaries.py`：通过，19 passed。
- `cd backend; uv run pytest`：通过，84 passed。

### 尚未执行

- 尚未执行 #5 及后续架构深化 issue。

### 下一步

- 在 GitHub issue #4 留言同步实现与验证结果。
- 后续可从 #5 “深化指南型健康建议安全边界”开始。

### Issue 同步

- 已在 #4 留言同步本地实现与验证结果：https://github.com/honestman9527/HPS/issues/4#issuecomment-4377219459

## 2026-05-05 15:24 +08:00

### 本次已完成

- 使用 `tdd` 流程执行 #5：深化指南型健康建议安全边界。
- 将指南型健康建议信号从隐式 `user_data["_guideline_signal"]` 改为显式入口：
  - `PredictUseCase` 调用 `recommendation_service.generate(guideline_signal=..., risk_probability=...)`。
  - `RecommendationService` 与 `generate_recommendations` 同步改为 keyword-only 显式参数。
- 在 `RecommendationEngine` 内集中执行：
  - topic 分组。
  - priority 选择。
  - confidence notice 合并到第一张卡片。
  - `safety_boundary` 文案改写。
- 新增建议引擎行为测试：
  - 显式指南信号不会藏入输入快照。
  - 同 topic 取高优先级建议。
  - confidence notice 合并到第一张卡片。
  - 知识库规则必须声明 `safety_boundary.avoid_diagnosis=true`。
  - 输出保持前端卡片列表结构，且不出现确诊、诊断、处方、药物干预、调整治疗方案等越界表述。
- 更新 `task_plan.md`，将阶段 3 标记为 complete。

### 验证结果

- `cd backend; uv run pytest tests/prediction/test_predict_use_case.py tests/services/test_recommendation_engine.py`：通过，9 passed。
- `cd backend; uv run pytest`：通过，88 passed。

### 尚未执行

- 尚未执行 #6 及后续架构深化 issue。

### 下一步

- 在 GitHub issue #5 留言同步实现与验证结果。
- 后续可从 #6 “深化预测记录读写映射”开始。

### Issue 同步

- 已在 #5 留言同步本地实现与验证结果：https://github.com/honestman9527/HPS/issues/5#issuecomment-4377279177

## 2026-05-05 15:32 +08:00

### 本次已完成

- 使用 `tdd` 流程执行 #6：深化预测记录读写映射。
- 新增 `NormalizedPredictionRows` DTO，让 mapper 负责一次性构造：
  - Prophet 预测主记录。
  - 预测主记录。
  - 输入快照。
  - 融合元信息。
  - 置信度原因。
  - 指南型健康建议明细。
  - Prophet 预测点。
  - 训练元信息。
- 收敛 `PredictionRecordRepository.save_prediction()`：repository 只调用 `mapper.build_normalized_prediction(payload)` 并负责 `add/commit`，不再逐表拼装 normalized 明细。
- 新增/调整测试覆盖：
  - 写入映射：完整预测 payload 能生成完整 normalized rows。
  - repository 边界：保存路径只消费 normalized rows DTO。
  - 读取兼容：旧格式 `guideline_payload` recommendation 仍能通过完整 payload assembly 回放。
- 更新 `task_plan.md`，将阶段 4 标记为 complete。

### 验证结果

- `cd backend; uv run pytest tests/prediction/test_normalized_prediction_mapper.py tests/prediction/test_prediction_repository_boundaries.py`：通过，20 passed。
- `cd backend; uv run pytest`：通过，91 passed。

### 尚未执行

- 尚未执行 #7 及后续架构深化 issue。

### 下一步

- 在 GitHub issue #6 留言同步实现与验证结果。
- 后续可从 #7 “深化 Prophet 模型生命周期模块”开始。

### Issue 同步

- 已在 #6 留言同步本地实现与验证结果：https://github.com/honestman9527/HPS/issues/6#issuecomment-4377337808

## 2026-05-05 15:43 +08:00

### 本次已完成

- 使用 `tdd` 流程执行 #7：深化 Prophet 模型生命周期模块。
- 收敛调用方接口：
  - `PredictUseCase` 不再先调用 `prophet_gateway.inspect()` 再 `predict()`。
  - `PredictUseCase` 只请求 `prophet_gateway.predict(user_id, forecast_days)`，模型版本、数据签名、缓存命中和复用策略由预测结果返回。
  - `prediction.infrastructure.gateways.ProphetGateway` 公开包装不再暴露 `inspect()`。
- 新增 Prophet 子模块边界：
  - `prophet_training_context.py`：每日血压序列聚合、训练上下文、参数画像、置信度和数据签名。
  - `prophet_lifecycle_policy.py`：基于活跃模型、模型版本、新增自然日数和重训阈值判断是否复用 Prophet 模型。
  - `prophet_model_lifecycle.py`：封装 inspect + predict 顺序约束。
- `prophet_gateway.py` 继续保留文件存储、内存缓存和模型训练/预测 adapter，并委托新模块处理训练上下文与生命周期策略。
- 新增/调整测试覆盖：
  - 调用方不再理解 inspect/predict 顺序。
  - 每日血压序列聚合和训练上下文构造。
  - 生命周期封装的 inspect + predict 顺序。
  - 阈值重训策略：低于阈值复用，达到阈值重训。
  - 既有模型复用、缓存命中、模型持久化和重训路径。
- 更新 `task_plan.md`，将阶段 5 标记为 complete。

### 验证结果

- `cd backend; uv run pytest tests/prediction/test_prophet_gateway.py tests/prediction/test_predict_use_case.py`：通过，12 passed。
- `cd backend; uv run pytest`：通过，95 passed。

### 尚未执行

- 尚未执行 #8 双模型预测引擎 run module 深化。

### 下一步

- 在 GitHub issue #7 留言同步实现与验证结果。
- 后续可从 #8 “深化双模型预测引擎 run module”开始。

### Issue 同步

- 已在 #7 留言同步本地实现与验证结果：https://github.com/honestman9527/HPS/issues/7#issuecomment-4377397438

## 2026-05-05 16:02 +08:00

### 本次已完成

- 使用 `tdd` 流程执行 #8：深化双模型预测引擎 run module。
- 新增 `PredictionRun` 内部 Module，把一次预测 run 的关键步骤收敛为清晰内部流程：
  - 用户个人风险因素快照。
  - Prophet 预测期血压特征。
  - LightGBM 高血压发病风险概率评分。
  - 趋势与用药信号融合。
  - 指南型健康建议信号与建议 payload。
  - 预测记录保存 payload。
- `PredictUseCase` 保持外部入口不变：调用方仍通过 `execute(PredictCommand) -> PredictionResult` 完成预测。
- 新增/调整 use case 行为测试，覆盖 happy path、缺失 BP 默认值、关闭趋势融合、模型复用说明，以及预测 run payload 可追踪性。
- 更新 `task_plan.md`，将阶段 6 标记为 complete。

### 验证结果

- `cd backend; uv run pytest tests/prediction/test_predict_use_case.py`：通过，10 passed。
- `cd backend; uv run pytest`：通过，98 passed。

### 尚未执行

- 尚未提交本地 git commit。

### 下一步

- 可按 #2-#8 阶段边界整理提交或关闭已完成 issue。

### Issue 同步

- 已在 #8 留言同步本地实现与验证结果：https://github.com/honestman9527/HPS/issues/8#issuecomment-4377438695

## 2026-05-06 21:02 +08:00

### 本次已完成

- 使用 `planning-with-files-zh` 恢复并读取现有规划文件：
  - `task_plan.md`
  - `findings.md`
  - `progress.md`
- 确认现有 #2-#8 架构深化计划已经全部标记为 complete。
- 根据用户要求“按顺序做成计划，全部”，把 2026-05-06 全盘扫描得到的 8 个新候选追加为二期阶段计划：
  - 阶段 7：双模型预测引擎装配 Module。
  - 阶段 8：预测运行决策 Module。
  - 阶段 9：预测记录规范化读写 Module。
  - 阶段 10：训练数据导出 Module。
  - 阶段 11：个人档案字段契约 Module。
  - 阶段 12：账户信息凭证规则 Module。
  - 阶段 13：预测链路治理前端 Module。
  - 阶段 14：周健康报告语义收敛。
- 更新 `task_plan.md`，追加二期目标、策略、每阶段任务、涉及文件、验收标准和风险控制。
- 更新 `findings.md`，追加二期全盘扫描发现和优先级判断。

### 当前工作区状态

- 业务代码仍包含上一轮已完成但尚未提交的模型训练入口结构优化：
  - `backend/train_models.py`
  - `backend/training/__init__.py`
  - `backend/training/pipeline.py`
  - `backend/tests/training/test_train_models_orchestration.py`
- 本次只追加计划与发现记录，没有继续修改业务逻辑。

### 尚未执行

- 尚未实施二期阶段 7-14。
- 尚未为二期阶段创建 GitHub issues。
- 尚未运行新的测试；本次是规划整理。

### 下一步

- 若用户确认执行，可从阶段 7 “双模型预测引擎装配 Module”开始。
- 若用户希望继续走 GitHub issue 流程，可先把阶段 7-14 拆成 issues。

## 2026-05-06 21:10 +08:00

### 本次正在执行

- 使用 `planning-with-files` 按二期计划进入阶段 7：双模型预测引擎装配 Module。
- 已确认当前工作区存在上一轮未提交训练入口优化改动，本阶段不修改相关文件：
  - `backend/train_models.py`
  - `backend/training/__init__.py`
  - `backend/training/pipeline.py`
  - `backend/tests/training/test_train_models_orchestration.py`
- 已完成阶段 7 初步代码阅读，准备新增预测用例装配 Module 并让预测路由只保留 HTTP 层和薄委托。

### 阶段 7 已完成

- 新增 `backend/prediction/application/composition.py`，集中预测相关 use case 装配。
- 收敛 `backend/routes/predictions.py`，路由层不再直接装配 repository、gateway、metadata window 和模型复用窗口。
- 调整 `backend/tests/routes/test_predictions_route_use_cases.py`，补充路由薄委托和装配工厂边界测试。

### 验证结果

- `cd backend; uv run pytest tests/routes/test_predictions_route_use_cases.py tests/prediction/test_predict_use_case.py`：通过，21 passed。
- `cd backend; uv run pytest`：通过，118 passed。

### 下一步

- 继续执行阶段 8：预测运行决策 Module。

## 2026-05-06 21:20 +08:00

### 阶段 8 已完成

- 新增预测运行 key domain policy：
  - `backend/prediction/domain/run_key_policy.py`
- 新增指南型健康建议信号与血压分级 domain policy：
  - `backend/prediction/domain/guideline_signal_policy.py`
- 新增预测保存 payload 与结果组装 builder：
  - `backend/prediction/application/prediction_result_builder.py`
- 收敛 `backend/prediction/application/prediction_run.py`，保留流程编排与风险评分调用，移出运行 key、指南信号、血压分级和结果组装规则。
- 新增 `backend/tests/prediction/test_prediction_run_policies.py`，并更新运行 key 测试改为直接覆盖 domain policy。

### 验证结果

- `cd backend; uv run pytest tests/prediction/test_predict_use_case.py tests/prediction/test_prediction_run_policies.py`：通过，14 passed。
- `cd backend; uv run pytest`：通过，121 passed。

### 下一步

- 继续执行阶段 9：预测记录规范化读写 Module。

## 2026-05-06 21:32 +08:00

### 阶段 9 已完成

- 保留 `backend/prediction/infrastructure/normalized_prediction_mapper.py` 作为 facade。
- 新增规范化预测记录内部 mapping modules：
  - `backend/prediction/infrastructure/normalized_prediction_input_mapping.py`
  - `backend/prediction/infrastructure/normalized_prediction_fusion_mapping.py`
  - `backend/prediction/infrastructure/normalized_prediction_training_mapping.py`
  - `backend/prediction/infrastructure/normalized_prediction_forecast_mapping.py`
  - `backend/prediction/infrastructure/normalized_prediction_recommendation_mapping.py`
  - `backend/prediction/infrastructure/normalized_prediction_rows.py`
- 写入映射、读取映射和旧格式指南型健康建议回放路径保持原行为，历史页与预测结果治理继续共用 `PredictionPayloadAssembler`。

### 验证结果

- `cd backend; uv run pytest tests/prediction/test_normalized_prediction_mapper.py tests/prediction/test_prediction_repository_boundaries.py`：通过，28 passed。
- `cd backend; uv run pytest`：通过，121 passed。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| Windows 下 `rg ... backend\prediction\infrastructure\normalized_prediction*` 路径通配报 `os error 123` | 1 | 改用 `rg -g "normalized_prediction*.py"` 进行扫描 |

### 下一步

- 继续执行阶段 10：训练数据导出 Module。

## 2026-05-06 21:44 +08:00

### 阶段 10 已完成

- 新增 `backend/training/export_samples.py`，集中训练数据导出样本构造规则：
  - 最近 BP 均值。
  - diagnosis/rule 标签来源。
  - LightGBM 特征行构造。
  - 非吸烟者 `cigsPerDay=0`。
  - 缺失字段保留。
  - 无效样本跳过。
- 收敛 `backend/services/export_service.py`，保留 CSV 输出和导出统计服务编排。
- 更新 `backend/tests/services/test_export_service.py` 并新增 `backend/tests/training/test_export_samples.py`。

### 验证结果

- `cd backend; uv run pytest tests/services/test_export_service.py tests/training/test_export_samples.py tests/training/test_train_models_orchestration.py`：通过，10 passed。
- `cd backend; uv run pytest`：通过，125 passed。

### 下一步

- 继续执行阶段 11：个人档案字段契约 Module。

## 2026-05-06 21:58 +08:00

### 阶段 11 已完成

- 新增后端个人档案字段契约：
  - `backend/services/profile_contract.py`
- 收敛后端 ProfileService：
  - `backend/services/profile_service.py`
- 新增后端契约测试：
  - `backend/tests/services/test_profile_contract.py`
- 新增前端 ProfileForm 状态与字段解析模块：
  - `frontend/src/features/profile/profileFormState.ts`
- 新增前端状态测试：
  - `frontend/src/features/profile/profileFormState.test.ts`
- ProfileForm 保留现有 UI 结构，健康档案状态、BMI、吸烟联动和保存 payload 构造已经移出组件。

### 验证结果

- `cd backend; uv run pytest tests/routes/test_profile_routes.py tests/services/test_profile_contract.py`：通过，9 passed。
- `cd frontend; pnpm exec vitest run src/features/profile/profileFormState.test.ts`：通过，3 passed。
- `cd frontend; pnpm run typecheck`：通过。
- `cd frontend; pnpm run lint`：通过。
- `cd frontend; pnpm run test`：通过，6 files / 14 tests passed。
- `cd backend; uv run pytest`：通过，129 passed。
- Playwright 浏览器验证：个人中心 `/profile` 页面正常渲染，诊断反馈语义保留，BMI 显示正常；将“当前是否吸烟”切换为“否”后，“日吸烟支数”自动变为 0 并禁用；保存健康档案时 PUT `/api/profile` payload 包含 `current_smoker: 0` 与 `cigs_per_day: 0`。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| 读取 `frontend/vitest.config.ts` 失败，实际项目使用 `vite.config.js` | 1 | 改读 `frontend/vite.config.js` |
| 读取 `frontend/vite.config.ts` 失败，实际项目使用 `vite.config.js` | 1 | 改读 `frontend/vite.config.js` |
| `npx -p playwright node -e "require('playwright')"` 无法解析临时包 | 1 | 改用 `@playwright/cli` 的 `open/route/snapshot/request-body` |
| `playwright-cli open --headless` 不支持 `--headless` 选项 | 1 | 使用默认 `open` 命令 |
| 在 `about:blank` 设置 localStorage 触发浏览器 `SecurityError` | 1 | 进入同源登录页后再设置 token |
| 首次浏览器验证未 mock `/api/prophet-predictions` 导致 Vite proxy 502 | 1 | 补充 `**/api/prophet-predictions**` route 后重开干净会话验证 |

### 下一步

- 继续执行阶段 12：账户信息凭证规则 Module。

## 2026-05-06 22:08 +08:00

### 阶段 12 已完成

- 新增后端账户凭证规则：
  - `backend/services/account_contract.py`
- `backend/services/auth_service.py` 改为复用 account contract。
- 新增后端测试：
  - `backend/tests/services/test_account_contract.py`
- 更新前端统一凭证校验：
  - `frontend/src/features/auth/validation.ts`
  - `frontend/src/features/auth/components/RegisterForm.tsx`
  - `frontend/src/features/auth/components/LoginForm.tsx`
  - `frontend/src/features/profile/components/ProfileForm.tsx`
- 新增前端测试：
  - `frontend/src/features/auth/validation.test.ts`

### 验证结果

- `cd backend; uv run pytest tests/routes/test_auth_routes.py tests/services/test_account_contract.py`：通过，17 passed。
- `cd frontend; pnpm exec vitest run src/features/auth/validation.test.ts src/features/profile/profileFormState.test.ts`：通过，6 passed。
- `cd frontend; pnpm run typecheck`：通过。
- `cd frontend; pnpm run lint`：通过。
- `cd frontend; pnpm run test`：通过，7 files / 17 tests passed。
- `cd backend; uv run pytest`：通过，132 passed。
- Playwright 浏览器验证：注册页无效邮箱显示“邮箱格式不正确”；纯字母密码显示“密码需至少包含字母、数字、符号中的两种”；控制台无 errors。

### 下一步

- 继续执行阶段 13：预测链路治理前端 Module。

## 2026-05-06 22:24 +08:00

### 阶段 13 已完成

- 新增预测链路治理会话 Module：
  - `frontend/src/features/admin/governanceSession.ts`
- 将治理筛选、chips、query string、导出参数、summary/list/detail normalization 和默认详情选择规则从 `adminApi.ts` / `usePredictionGovernanceData.ts` 收敛到治理会话 Module。
- 新增并调整测试：
  - `frontend/src/features/admin/governanceSession.test.ts`
  - `frontend/src/features/admin/api/adminApi.test.ts`

### 验证结果

- `cd frontend; pnpm exec vitest run src/features/admin/governanceSession.test.ts src/features/admin/api/adminApi.test.ts src/features/admin/auditDetailPresentation.test.ts src/features/admin/governancePresentation.test.ts`：通过。
- `cd frontend; pnpm run typecheck`：通过。
- `cd frontend; pnpm run lint`：通过。
- `cd frontend; pnpm run test`：通过，8 files / 21 tests passed。
- Playwright 浏览器验证：管理员预测治理页 `/admin/governance` 正常渲染 summary/list/detail；详情加载 `#901`；异常筛选会更新 chip、URL query 和导出参数；高风险筛选导出请求为 `/api/admin/governance/export?risk_level=%E9%AB%98%E9%A3%8E%E9%99%A9&has_anomaly=true`；控制台无 errors。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| Playwright 脚本尝试用 `high` 选择风险等级，但页面 option value 实际为中文 `高风险` | 1 | 改为选择 `高风险`，确认导出参数也使用中文风险等级 |

### 收口动作

- 已执行 `npx -y @playwright/cli close-all`。
- 已停止占用 `127.0.0.1:5174` 的 Vite `node` 进程。

### 下一步

- 继续执行阶段 14：周健康报告语义收敛。

## 2026-05-06 22:15 +08:00

### 阶段 14 已完成

- 新增周健康报告主服务入口：
  - `backend/services/weekly_report_service.py`
- 更新后端路由：
  - `backend/routes/weekly_report.py` 使用 `WeeklyReportService`。
  - `backend/routes/profile.py` 保留 `/api/profile/weekly-comparison` 兼容入口，并委托同一份周健康报告服务。
- 收敛后端周报摘要文案：
  - 从“本周 / 上周 / 上一周”改为滚动窗口语义“最近7天 / 前7天”。
- 收敛前端周报展示：
  - `frontend/src/features/weekly-report/presentation.ts`
  - `frontend/src/features/weekly-report/components/WeeklyReportMetricGrid.tsx`
  - `frontend/src/features/weekly-report/components/WeeklyReportSummarySection.tsx`
  - `frontend/src/features/profile/components/WeeklyComparisonPanel.tsx`
  - `frontend/src/pages/ProfilePage.tsx`
  - `frontend/src/pages/WeeklyReportPage.tsx`
- Profile 兼容 API `getWeeklyComparison` 继续导出，但内部委托 weekly-report 主 API Module 的 `getProfileWeeklyReport()`。

### 验证结果

- `cd backend; uv run pytest tests/routes/test_weekly_report_routes.py tests/routes/test_profile_routes.py tests/services/test_weekly_comparison_service.py`：通过，10 passed。
- `cd frontend; pnpm exec vitest run src/features/weekly-report/presentation.test.ts`：通过，2 passed。
- `cd backend; uv run pytest`：通过，134 passed。
- `cd frontend; pnpm run typecheck`：通过。
- `cd frontend; pnpm run lint`：通过。
- `cd frontend; pnpm run test`：通过，8 files / 21 tests passed。
- Playwright 浏览器验证：
  - `/weekly-report` 正常渲染“周健康报告”“最近7天 2026-04-19 ~ 2026-04-25”“前7天 2026-04-12 ~ 2026-04-18”“较前7天”指标文案，请求 `/api/weekly-report`。
  - `/profile` 切换到“健康趋势”tab 后正常渲染同一套周健康报告展示，请求 `/api/profile/weekly-comparison`。
  - 两条路径控制台均无 errors。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| Windows 下 `Start-Process -FilePath 'pnpm'` 启动 Vite 报 `%1 不是有效的 Win32 应用程序` | 1 | 改用 `pnpm.cmd` 启动 Vite |

### 收口动作

- 已执行 `npx -y @playwright/cli close-all`。
- 已停止占用 `127.0.0.1:5174` 的 Vite 进程。
- 已删除本次生成的 `frontend/vite-phase14.log` 与 `frontend/vite-phase14.err.log`。

### 下一步

- 二期阶段 7-14 已全部完成。
- 可按阶段边界检查未提交文件，决定是否拆分提交或继续同步 issue。

## 2026-05-07 数据库设计与全量扫描优化规划

### 本次已完成

- 使用 `planning-with-files` 恢复并读取现有规划文件：
  - `task_plan.md`
  - `findings.md`
  - `progress.md`
- 根据用户要求，把数据库设计、`user_profiles` 拆分和全量扫描优化整理为三期计划。
- 更新 `task_plan.md`，新增三期数据库设计与查询优化阶段：
  - 阶段 15：数据库查询基线与索引方案。
  - 阶段 16：普通用户个人档案拆分设计。
  - 阶段 17：预测结果治理查询下推。
  - 阶段 18：训练数据导出批量聚合。
  - 阶段 19：用户侧血压记录状态查询优化。
  - 阶段 20：Prophet 每日血压序列读取边界。
- 更新 `findings.md`，记录数据库表数量判断、`user_profiles` 拆分方向、全量扫描热点和候选索引。
- 明确管理员不需要 profile：`admin_users` 只表达管理员 **账户信息**，不关联 **个人档案**、**风险因素档案**、**诊断反馈**、**血压记录** 或 **预测记录**。

### 尚未执行

- 尚未修改数据库结构、迁移脚本或生产配置。
- 尚未实施索引、表拆分或查询代码优化。
- 尚未运行新的测试；本次是规划整理。

### 下一步

- 若确认执行，建议从阶段 15 开始，先做真实 schema 与 EXPLAIN 基线，再决定索引迁移。
- `user_profiles` 拆分属于 schema 变更，实施前需要单独确认迁移方案和回滚策略。

## 2026-05-07 个人档案拆分计划调整

### 本次已完成

- 根据用户反馈调整三期阶段 16：`user_diagnosis_feedback` 独立表没有必要，`user_profile` 不要拆太散。
- 更新 `task_plan.md`：
  - 阶段 16 改为“普通用户个人档案轻量拆分设计”。
  - 目标结构收敛为 `user_profiles` + `user_risk_factor_profiles` 两张普通用户档案相关表。
  - `diagnosis` 留在 `user_profiles`，继续表达 **诊断反馈**，不进入用户侧 **双模型预测引擎**。
  - 明确不新增 `user_diagnosis_feedback` 表。
- 更新 `findings.md`，记录该设计决策，避免后续架构扫描再次建议过度拆分。

### 尚未执行

- 尚未修改数据库结构、迁移脚本或业务代码。
- 尚未运行测试；本次只调整规划文档。

## 2026-05-07 三期计划执行

### 本次正在执行

- 使用 `planning-with-files` 恢复现有计划，按三期推荐顺序从阶段 15 开始。
- 使用 `tdd` 作为后续代码优化流程：每个可实施阶段先补行为测试，再改实现并回归验证。
- 阶段 15 属于数据库查询基线与索引方案，按项目约束只产出设计和基线说明，不直接新增迁移脚本、不修改生产配置。

### 阶段 15 已完成

- 对照 ORM、Alembic 迁移和 `database/hypertension.sql`，确认 dump 落后于当前 schema：
  - dump 仍有 `users.role`。
  - dump 缺少 `admin_users`。
  - dump 缺少固定 7 天 forecast 的 check constraint。
- 创建数据库查询基线与索引设计说明：
  - `docs/agents/database-query-index-baseline.md`
- 记录候选复合索引、EXPLAIN 模板、重复索引评估和 downgrade 回滚策略。
- 未新增迁移脚本，未修改生产配置。

### 阶段 17 已完成

- 新增治理 read model 测试：
  - `backend/tests/prediction/test_prediction_governance_read_model.py`
- 将预测结果治理 summary 改为数据库聚合计数，避免组装全量治理 payload。
- 将异常筛选规则下推到 SQLAlchemy 条件，列表接口先过滤再分页，导出接口先过滤再组装。

### 阶段 17 验证结果

- `cd backend; uv run pytest tests/prediction/test_prediction_governance_read_model.py`：通过，2 passed。
- `cd backend; uv run pytest tests/services/test_prediction_governance_service.py tests/prediction/test_prediction_governance_policy.py tests/prediction/test_prediction_governance_read_model.py`：通过，5 passed。

### 阶段 18 已完成

- 新增训练导出批量投影和 batch DTO，服务入口不再调用 `User.query.all()`。
- 最近 N 条血压均值、总血压记录数、偏高血压记录数改为批量查询/聚合，保留 CSV 列顺序和标签来源语义。

### 阶段 18 验证结果

- `cd backend; uv run pytest tests/services/test_export_service.py tests/training/test_export_samples.py`：通过，8 passed。

### 阶段 19 已完成

- 血压数据状态改为聚合计数，不再加载用户全量 BP records。
- 今日健康任务改为最新记录 + 日期投影 + 最近 3 个记录日日均血压投影。
- 周健康报告保持最近 14 天窗口读取语义不变。

### 阶段 19 验证结果

- `cd backend; uv run pytest tests/prediction/test_bp_data_repository.py tests/services/test_health_task_service.py`：通过，2 passed。
- `cd backend; uv run pytest tests/routes/test_bp_records_routes.py tests/routes/test_weekly_report_routes.py tests/services/test_weekly_comparison_service.py tests/prediction/test_bp_data_repository.py tests/services/test_health_task_service.py`：通过，13 passed。

### 阶段 16 已完成

- 创建普通用户个人档案轻量拆分设计：
  - `docs/agents/user-profile-lightweight-split-design.md`
- 明确目标表、upgrade/downgrade 草案、兼容读取、前端类型过渡和测试清单。
- 未新增迁移脚本，未修改数据库结构。

### 阶段 20 已完成

- Prophet 每日序列读取改为数据库日聚合投影：
  - `backend/prediction/infrastructure/prophet_gateway.py`
  - `backend/prediction/infrastructure/prophet_training_context.py`
- 新增读取边界说明：
  - `docs/agents/prophet-daily-series-read-boundary.md`

### 阶段 20 验证结果

- `cd backend; uv run pytest tests/prediction/test_prophet_gateway.py::test_load_daily_records_uses_database_daily_projection`：通过，1 passed。
- `cd backend; uv run pytest tests/prediction/test_prophet_gateway.py`：通过，7 passed。

### 三期收口验证

- 后端全量：`cd backend; uv run pytest` 通过，149 passed。
- 前端：`cd frontend; pnpm run typecheck` 通过。
- 前端：`cd frontend; pnpm run lint` 通过。
- 前端：`cd frontend; pnpm run test` 通过，13 files / 28 tests passed。
- 浏览器验证管理员预测治理页通过：
  - `/admin/governance` summary/list/detail 正常渲染。
  - 高风险 + 仅异常筛选后，列表只显示高风险异常记录。
  - 选中详情加载 `#50`。
  - 导出筛选结果请求 `/api/admin/governance/export?risk_level=高风险&has_anomaly=true`，后端返回 200。
  - 浏览器控制台无 error/warning。

## 2026-05-07 三期设计实施

### 本次正在执行

- 使用 `planning-with-files` 继续恢复 `task_plan.md`、`progress.md`、`findings.md`。
- 用户已确认“实施这些设计”，因此阶段 15 的索引方案与阶段 16 的轻量拆分方案进入实际迁移和代码实现。
- 追加 `task_plan.md` 阶段 21：三期设计实施，覆盖索引迁移、`user_risk_factor_profiles`、后端兼容、前端管理员用户表和 dump 更新。
- 执行 `session-catchup.py` 未发现额外输出。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| PowerShell 中用双引号搜索 SQL 反引号表名时触发 `` `u `` Unicode 转义解析错误 | 1 | 改用单引号搜索模式，避免反引号被 PowerShell 解释 |

### 下一步

- 先补后端行为测试，锁定普通用户档案拆分、预测输入、训练导出和管理员 DTO 行为。
- 再实现 ORM、服务、迁移和前端类型/表格调整。

### 阶段 21 已完成

- 新增后端行为测试：
  - `backend/tests/services/test_profile_split_service.py`
  - `backend/tests/models/test_admin_user.py`
- 新增前端组件测试：
  - `frontend/src/features/admin/components/UserTable.test.tsx`
- 新增迁移：
  - `backend/migrations/versions/9c1d2e3f4a5b_profile_risk_factor_split_and_indexes.py`
- 后端实现：
  - 新增 `UserRiskFactorProfile` ORM。
  - `User.to_dict()` 合并普通用户个人档案和风险因素档案。
  - `ProfileService` 将展示资料/诊断反馈与风险因素字段写入不同表。
  - `PredictionInputSnapshot` 改为读取 `user.risk_factor_profile`。
  - 训练导出投影改为连接 `user_profiles.diagnosis` 与 `user_risk_factor_profiles`。
  - `AdminUser.to_dict()` 移除伪健康字段。
  - Demo 用户种子脚本同步创建风险因素档案。
- 前端实现：
  - `AdminUser` 类型的 `age`、`bmi`、`profile_complete` 改为可选，管理员账号不需要提供这些字段。
  - UserTable 测试确认普通用户表显示年龄/BMI，管理员表不显示年龄/BMI。
- 数据库快照：
  - `database/hypertension.sql` 已补齐 `admin_users`、`user_risk_factor_profiles`、复合索引与 7 天 check constraint，并移除旧 `users.role`。

### 阶段 21 验证结果

- 红灯测试确认初始失败：
  - `uv run pytest tests/services/test_profile_split_service.py tests/models/test_admin_user.py`：4 failed，失败点对应缺少 `UserRiskFactorProfile`、预测输入仍读 `user.profile`、训练导出投影未拆分、管理员 DTO 仍含伪健康字段。
- 后端目标测试通过：
  - `uv run pytest tests/services/test_profile_split_service.py tests/models/test_admin_user.py tests/routes/test_profile_routes.py tests/training/test_export_samples.py tests/services/test_export_service.py tests/prediction/test_predict_use_case.py`：29 passed。
- 后端全量测试通过：
  - `uv run pytest`：153 passed。
- 迁移脚本语法检查通过：
  - `uv run python -m py_compile migrations/versions/9c1d2e3f4a5b_profile_risk_factor_split_and_indexes.py`。
- 前端验证通过：
  - `pnpm exec vitest run src/features/admin/components/UserTable.test.tsx`：1 passed。
  - `pnpm run typecheck`：通过。
  - `pnpm run lint`：通过。
  - `pnpm run test`：14 files / 29 tests passed。
- in-app browser 验证 `/admin/users` 通过：
  - mock API 返回普通用户 `alice` 带 `age=56`、`bmi=24.2`。
  - mock API 返回管理员 `root` 不带 `age`、`bmi`、`profile_complete`。
  - 页面普通用户表显示“年龄 / BMI / 56 / 24.2”。
  - 页面管理员表不显示“年龄 / BMI”，只显示账号字段、角色、注册时间和密码操作。
  - 浏览器控制台无 error/warning。

### 阶段 21 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| 使用 `Start-Process node -ArgumentList @('-e', $script)` 启动带空格和引号的 mock API 脚本时，Node 进程立即退出，5000 端口未监听 | 2 | 改用持久 Node REPL 启动 mock HTTP server，浏览器验证完成后在 REPL 中关闭 server |
| PowerShell `foreach ($pid in $pids)` 失败：`$PID` 是只读内置变量 | 1 | 改用 `$processId` 作为循环变量后停止 Vite 相关进程 |

### 收口动作

- 已关闭 Node REPL mock API server。
- 已停止 Vite dev server 相关进程。
- 已清理前端 typecheck 生成的 `frontend/tsconfig.node.tsbuildinfo`。

## 2026-05-07 grill-with-docs：档案拆分领域边界

### 本次已完成

- 使用 `grill-with-docs` 对阶段 21 的档案拆分、管理员账号边界和预测输入契约进行逐问确认。
- 更新 `CONTEXT.md`：
  - **诊断反馈** 属于 **个人档案**，但不属于 **风险因素档案**。
  - **训练数据导出** 可使用 **诊断反馈** 作为标签来源，但导出特征来自 **风险因素档案**、血压聚合结果和模型特征契约。
  - **管理员** 只拥有 **账户信息**，不拥有普通用户健康档案或预测记录体系。
  - 前端 Profile DTO 扁平输出只是过渡兼容策略，不代表领域或数据库无边界。
  - 缺失或未完成 **风险因素档案** 时，系统应阻止 **7天风险预测**。
- 更新 `docs/architecture/ARCHITECTURE.md`：
  - 补齐 `admin_users` 和 `user_risk_factor_profiles`。
  - 修正 `users` 不再保存角色字段。
  - 明确 `user_profiles`、`user_risk_factor_profiles`、`admin_users` 的职责。
  - 预测主流程增加风险因素档案校验。
- 新增 ADR：
  - `docs/adr/0005-separate-admin-accounts-from-user-health-profiles.md`
  - `docs/adr/0006-lightweight-user-profile-risk-factor-split.md`
- 根据确认的后端契约补实现：
  - 新增 `IncompleteRiskFactorProfileError`。
  - `PredictionInputSnapshot.from_user_and_latest_bp()` 在风险因素档案缺失或未完成时抛出领域错误。
  - `/api/predict` 将该错误转为 400，返回“请先完善风险因素档案”。

### 验证结果

- 目标测试通过：
  - `uv run pytest tests/prediction/test_predict_use_case.py tests/routes/test_predictions_route_use_cases.py`：25 passed。
- 后端全量测试通过：
  - `uv run pytest`：155 passed。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| 后端全量测试中 `test_prediction_input_snapshot_reads_risk_factor_profile_not_diagnosis_profile` 的测试 fixture 缺少 `profile_complete`，新增完整性校验后失败 | 1 | 给该测试的风险因素档案 fixture 补 `profile_complete=True`，保持测试关注点为“读风险因素档案而不是诊断反馈” |

## 2026-05-07 grill-with-docs：血压最低自然日预测阻断

### 本次已完成

- 根据用户确认的 Q12，将 **血压记录** 最低自然日要求补到后端 `/api/predict` 预测入口。
- 新增领域错误：
  - `prediction.domain.bp_data_policy.InsufficientBPDataForPredictionError`
- `PredictionRun.execute()` 在进入 Prophet 血压趋势预测前读取 `get_bp_data_status()`，当 `meets_minimum=False` 时阻止预测，并返回“血压记录不足：请至少记录 3 个自然日后再进行预测”。
- `/api/predict` 将血压自然日不足映射为 HTTP 400，不再让 Prophet adapter 的通用 `ValueError` 漏成 500。
- 更新 `CONTEXT.md` 和 `docs/architecture/ARCHITECTURE.md`，明确血压记录不足最低自然日时应在 7 天风险预测能力边界阻止预测；达到最低但未达到推荐自然日时仍可预测，并通过低置信度或数据不足信号解释。

### 验证结果

- 红灯确认：
  - `uv run pytest tests/prediction/test_predict_use_case.py::test_execute_blocks_when_bp_days_are_below_minimum`：先因缺少 `prediction.domain.bp_data_policy` 失败。
  - `uv run pytest tests/routes/test_predictions_route_use_cases.py::test_predict_route_rejects_insufficient_bp_days`：先返回 500，确认路由尚未映射领域错误。
- 目标测试通过：
  - `uv run pytest tests/prediction/test_predict_use_case.py tests/routes/test_predictions_route_use_cases.py`：27 passed。
- 后端全量测试通过：
  - `uv run pytest`：157 passed。

## 2026-05-07 grill-with-docs：预测数据充分性策略收束

### 本次已完成

- 根据用户确认的 Q13，将血压最低自然日和推荐历史天数收束到领域策略：
  - `prediction.domain.bp_data_policy`
- 新增 `build_bp_data_status()`，由 `/api/bp-data-status` 复用同一份策略计算 `minimum_days`、`recommended_days_min/max`、`meets_minimum`、`meets_recommended` 和 `status`。
- `PredictionRun.execute()` 继续通过 `require_minimum_bp_days_for_prediction()` 使用同一策略阻断预测。
- Prophet 训练边界和预测结果治理的 `MINIMUM_TRAIN_DAYS` 改为引用同一最低自然日常量，保留原常量名作为兼容别名。
- 更新 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md` 和 `findings.md`，记录用户侧状态提示、预测入口阻断、Prophet 预测说明和预测结果治理应共享同一套预测数据充分性规则。

### 验证结果

- 红灯确认：
  - `uv run pytest tests/prediction/test_bp_data_policy.py`：先因缺少共享策略常量和 `build_bp_data_status()` 失败。
- 策略影响面目标测试通过：
  - `uv run pytest tests/prediction/test_bp_data_policy.py tests/prediction/test_bp_data_repository.py tests/prediction/test_predict_use_case.py tests/routes/test_predictions_route_use_cases.py tests/prediction/test_prophet_gateway.py tests/prediction/test_prediction_governance_policy.py tests/prediction/test_prediction_governance_read_model.py`：41 passed。
- 后端全量测试通过：
  - `uv run pytest`：159 passed。

## 2026-05-07 grill-with-docs：失败预测尝试不落入预测记录

### 本次已完成

- 根据用户确认的 Q14，明确风险因素档案不完整或血压记录低于最低自然日要求时，属于预测前校验失败。
- 预测前校验失败不创建 `prediction_records` 或 `prophet_predictions`，不进入普通用户预测历史，也不进入管理员预测结果治理。
- 新增保护测试，确认风险因素档案不完整时不会继续查询血压数据状态、不会进入 Prophet、不会调用 LightGBM、不会保存预测记录。
- 更新 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md` 和 `findings.md` 记录该领域边界。

### 验证结果

- 目标测试通过：
  - `uv run pytest tests/prediction/test_predict_use_case.py::test_execute_does_not_record_failed_attempt_when_risk_profile_is_incomplete tests/prediction/test_predict_use_case.py::test_execute_blocks_when_bp_days_are_below_minimum`：2 passed。
- 预测相关目标测试通过：
  - `uv run pytest tests/prediction/test_predict_use_case.py tests/routes/test_predictions_route_use_cases.py tests/prediction/test_bp_data_policy.py`：30 passed。
- 后端全量测试通过：
  - `uv run pytest`：160 passed。

## 2026-05-07 grill-with-docs：预测页风险因素档案阻断入口

### 本次已完成

- 根据用户确认的 Q15，将预测页风险因素档案阻断从普通错误提示改为可行动提示。
- `PredictionForm` 收到后端“请先完善风险因素档案”时，展示阻断提示块和“前往风险因素档案”按钮。
- 预测准备卡中的“个人档案”收束为“风险因素档案”，跳转目标改为 `/profile?tab=risk-factors`。
- `ProfilePage` 支持 `?tab=risk-factors` 查询参数，用户可直接进入个人中心的风险因素档案标签页。
- 更新 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md` 和 `findings.md` 记录该交互边界。

### 验证结果

- 红灯确认：
  - `pnpm exec vitest run src/features/prediction/components/PredictionForm.test.tsx`：先因预测页只显示普通 `error-msg` 且准备卡仍写“个人档案”失败。
- 前端目标测试通过：
  - `pnpm exec vitest run src/features/prediction/components/PredictionForm.test.tsx src/pages/ProfilePage.test.tsx`：4 passed。
- 前端验证通过：
  - `pnpm exec vitest run src/features/prediction/components/PredictionForm.test.tsx src/pages/ProfilePage.test.tsx`：4 passed。
  - `pnpm run typecheck`：通过。
  - `pnpm run lint`：通过。
  - `pnpm run test`：15 files / 32 tests passed。
- 浏览器验证通过：
  - mock `/api/predict` 返回 400 `请先完善风险因素档案` 后，预测页展示阻断提示块和“前往风险因素档案”按钮。
  - 点击后进入 `/profile?tab=risk-factors`，个人中心“风险因素档案”tab 为选中状态，风险因素表单可见。
  - 除预期的 mocked `/api/predict` 400 以外，无页面错误、无未覆盖 4xx/5xx 响应。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| Playwright 临时测试文件通过 `npx @playwright/test` 运行时无法解析临时安装的 `@playwright/test` 包 | 2 | 改用 Codex bundled Node + bundled Playwright 包执行浏览器脚本 |
| 首次浏览器验证 mock API 未覆盖 `/api/prophet-predictions?limit=120`，进入个人中心趋势 tab 初始化时出现 404 | 1 | 补充 mock `/api/prophet-predictions` 后重新验证 |

## 2026-05-07 grill-with-docs：风险因素档案最低完整性表单标记

### 本次已完成

- 根据用户确认的 Q16，个人中心风险因素档案表单显式区分预测前必填字段和可缺失字段。
- `HealthProfileSection` 将年龄、性别、身高、体重标记为“必填”，并给对应控件设置 `required`。
- 降压药、糖尿病、总胆固醇和血糖保持“选填”/可缺失语义，不设置 `required`。
- `SelInput` 支持 `id`、`required` 和字段 badge，风险因素档案表单字段增加 `id/htmlFor` 关联，改善自动化测试和可访问性。
- 更新 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md` 和 `findings.md` 记录该界面边界。

### 验证结果

- 红灯确认：
  - `pnpm exec vitest run src/features/profile/components/HealthProfileSection.test.tsx`：先因 label 未关联控件且没有 required 语义失败。
- 目标测试通过：
  - `pnpm exec vitest run src/features/profile/components/HealthProfileSection.test.tsx`：1 passed。
- 前端验证通过：
  - `pnpm exec vitest run src/features/profile/components/HealthProfileSection.test.tsx src/pages/ProfilePage.test.tsx src/features/profile/profileFormState.test.ts`：6 passed。
  - `pnpm run typecheck`：通过。
  - `pnpm run lint`：通过。
  - `pnpm run test`：16 files / 33 tests passed。
- 浏览器验证通过：
  - `/profile?tab=risk-factors` 直达风险因素档案标签页。
  - 年龄、性别、身高、体重显示 4 个“必填”标记并设置 `required`。
  - 降压药、糖尿病、总胆固醇、血糖显示“选填”标记且未设置 `required`。
  - 页面无 console error/warning，无 4xx/5xx 响应。

## 2026-05-07 grill-with-docs：吸烟字段最低完整性边界

### 本次已完成

- 根据用户确认的 Q17，明确当前是否吸烟和日吸烟支数仍属于风险因素档案，但不属于预测前最低完整性阻断条件。
- 新增后端回归测试，保护风险因素档案在年龄、性别、身高、体重齐全时，即使吸烟字段缺失也可以通过最低完整性校验。
- 更新 `CONTEXT.md` 和 `docs/architecture/ARCHITECTURE.md`，记录吸烟字段可缺失、非吸烟者日吸烟支数按 0 处理，以及前端表单不应把吸烟字段标为预测前必填。
- 更新 `findings.md`，记录 Q17 的领域边界结论。

### 验证结果

- `uv run pytest tests/services/test_profile_split_service.py::test_risk_factor_profile_minimum_completeness_does_not_require_smoking_fields tests/prediction/test_predict_use_case.py::test_prediction_input_snapshot_requires_complete_risk_factor_profile`：2 passed。
- `pnpm exec vitest run src/features/profile/components/HealthProfileSection.test.tsx`：1 passed。

## 2026-05-07 grill-with-docs：可缺失风险因素治理信号

### 本次已完成

- 根据用户确认的 Q18，明确可缺失风险因素字段缺失时，不等同于风险因素档案未完成，不阻止 7 天风险预测。
- `PredictionInputSnapshot` 继续只用风险因素档案最低完整性阻断预测；当前是否吸烟、降压药、糖尿病、总胆固醇、血糖等可缺失字段允许保持空值进入模型输入。
- 规范化预测输入快照和融合元数据允许保存这些缺失值：
  - `prediction_input_snapshots.current_smoker`
  - `prediction_input_snapshots.bp_meds`
  - `prediction_input_snapshots.diabetes`
  - `prediction_fusion_meta.bp_meds_input`
- 更新阶段 21 migration 和 `database/hypertension.sql`，使 schema 与可缺失输入语义一致；downgrade 前会把空值回填为旧版 `0` 后再恢复非空约束。
- 预测结果治理继续使用 `missing_key_profile_fields` 异常码，但前端展示文案从“档案关键字段缺失”收束为“模型输入字段缺失”，避免和风险因素档案未完成混淆。
- 治理规则补充：当前吸烟为“是”但日吸烟支数缺失时，也属于模型输入字段缺失的数据质量信号。
- 更新 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md` 和 `findings.md` 记录该领域边界。

### 验证结果

- 目标测试通过：
  - `uv run pytest tests/prediction/test_predict_use_case.py::test_execute_allows_optional_risk_factor_inputs_to_remain_missing tests/prediction/test_prediction_governance_policy.py::test_optional_missing_risk_factor_inputs_are_governance_signal_only tests/prediction/test_normalized_prediction_mapper.py::test_build_input_snapshot_preserves_optional_missing_risk_factor_fields tests/prediction/test_normalized_prediction_mapper.py::test_build_fusion_meta_preserves_missing_bp_meds_input_signal tests/models/test_prediction_input_snapshot.py`：5 passed。
  - `pnpm exec vitest run src/features/admin/governanceSession.test.ts`：4 passed。
- 相关回归通过：
  - `uv run pytest tests/prediction/test_predict_use_case.py tests/prediction/test_prediction_governance_policy.py tests/prediction/test_prediction_governance_read_model.py tests/prediction/test_normalized_prediction_mapper.py tests/models/test_prediction_input_snapshot.py tests/services/test_profile_split_service.py`：37 passed。
  - `pnpm run typecheck`：通过。
  - `pnpm run lint`：通过。
- 全量回归通过：
  - `uv run pytest`：166 passed。
  - `pnpm run test`：16 files / 33 tests passed。
- 浏览器验证通过：
  - `/admin/governance` 使用 mock API 渲染带 `missing_key_profile_fields` 的治理记录。
  - 列表、异常类型下拉和详情均显示“模型输入字段缺失”。
  - 页面不再显示“档案关键字段缺失”。
  - 缺失的当前吸烟、降压药等输入在详情中以 `—` 呈现。
  - mock API 无 4xx/5xx 响应，浏览器控制台无 error/warning。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| `Start-Process` 直接执行 `pnpm` shim 报 `%1 不是有效的 Win32 应用程序` | 1 | 改用 `pnpm.cmd` 启动 Vite |
| 浏览器验证首次缺少 `/api/admin/stats` mock，后台布局出现 404/toast | 1 | 补充 mock stats 端点后重新验证 |
| Playwright `getByText` 首先匹配隐藏 `<option>`，等待可见文本超时 | 2 | 改用 `document.body.innerText` 验证页面实际可见文本 |
| 治理旧测试中 `currentSmoker=1` 但缺少 `cigsPerDay`，新规则下会同时触发模型输入字段缺失 | 1 | 给该旧样本补 `cigsPerDay=5`，保持测试只覆盖“预测血压偏高但低风险” |

## 2026-05-07 grill-with-docs：成功预测不提示可缺失风险因素

### 本次已完成

- 根据用户确认的 Q19，明确普通用户侧预测成功后，不因为可缺失风险因素为空而额外提示“完善更多风险因素”。
- 新增 `PredictionForm` 行为测试，保护成功预测即使携带 `missing_key_profile_fields` 治理信号，也不显示普通用户 alert、“模型输入字段缺失”或“前往风险因素档案”按钮。
- 更新 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md` 和 `findings.md`，记录该数据质量信号只留在预测结果治理，不推到普通用户成功结果页。

### 验证结果

- `pnpm exec vitest run src/features/prediction/components/PredictionForm.test.tsx`：4 passed。
- `pnpm exec vitest run src/features/prediction/components/PredictionForm.test.tsx src/features/admin/governanceSession.test.ts src/features/profile/components/HealthProfileSection.test.tsx`：9 passed。
- `pnpm run typecheck`：通过。
- `pnpm run lint`：通过。
- `pnpm run test`：16 files / 34 tests passed。

### 说明

- 本次只增加测试和领域/架构文档，不改变页面实际渲染逻辑；Q18 已完成管理员治理页浏览器验证，本次无需重复打开浏览器。

## 2026-05-07 grill-with-docs：训练导出保留可缺失风险因素空值

### 本次已完成

- 根据用户确认的 Q20，明确训练数据导出遇到可缺失风险因素为空时继续导出样本。
- 新增训练导出行为测试，覆盖当前是否吸烟、日吸烟支数、降压药、糖尿病、总胆固醇和血糖均为空时，只要最低完整性字段、血压聚合结果和标签来源满足规则，导出样本仍生成，并保留空值进入特征行。
- 批量投影导出同样补测试，确认批量导出不会因可缺失风险因素为空而跳过样本。
- 更新 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md` 和 `findings.md`，记录空值交给模型训练缺失值策略处理。

### 验证结果

- `uv run pytest tests/training/test_export_samples.py`：7 passed。
- `uv run pytest tests/services/test_export_service.py tests/training/test_export_samples.py`：10 passed。

## 2026-05-07 本地训练数据导出命令

### 本次已完成

- 新增本地命令行导出入口 `backend/export_training_data.py`。
- 默认导出到 `datasets/training_data_export.csv`，与本地 `train_models.py` 读取路径一致。
- 支持 `--output` 自定义导出文件和 `--recent-bp-count` 覆盖最近血压均值窗口。
- 本地 CLI 复用网页管理员导出的 `export_training_csv()`，没有新增第二套训练样本规则。
- 更新 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md`、`findings.md` 和 `task_plan.md`，记录网页管理员导出保留、本地训练优先命令导出的边界。

### 验证结果

- 红灯确认：`uv run pytest tests/training/test_export_training_data_cli.py` 初次失败，原因是缺少 `export_training_data` 模块。
- 目标测试通过：`uv run pytest tests/training/test_export_training_data_cli.py`：3 passed。
- 导出相关回归通过：`uv run pytest tests/services/test_export_service.py tests/training/test_export_samples.py tests/training/test_export_training_data_cli.py`：13 passed。
- CLI smoke 通过：`uv run python export_training_data.py --help` 正常展示 `--output` 和 `--recent-bp-count`。
- 后端全量回归通过：`uv run pytest`：171 passed。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| PowerShell `Select-Object -Index 72..90` 把范围当成字符串，无法转换为整数 | 1 | 改为 `Select-Object -Index (72..90)` |

## 2026-05-07 grill-with-docs：本地训练保持两步命令

### 本次已完成

- 根据用户确认的 Q21，明确本地训练不自动导出训练 CSV。
- `train_models.py` 保持纯训练入口，不隐式调用 `export_training_data.py` 或连接应用数据库执行导出。
- 新增回归测试，保护 `train_models.main()` 只委托训练编排，不自动触发训练数据导出。
- 更新 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md` 和 `findings.md`，记录“先导出、再训练”的两步命令边界。

### 验证结果

- `uv run pytest tests/training/test_train_models_orchestration.py tests/training/test_export_training_data_cli.py`：8 passed。
- `uv run pytest tests/services/test_export_service.py tests/training/test_export_samples.py tests/training/test_train_models_orchestration.py tests/training/test_export_training_data_cli.py`：18 passed。

## 2026-05-07 grill-with-docs：缺少导出样本不阻止训练

### 本次已完成

- 根据用户确认的 Q22，明确 `datasets/training_data_export.csv` 不存在时不阻止本地模型训练。
- 新增训练数据读取回归测试，保护基础训练集单独存在时 `prepare_lgbm_data()` 继续返回训练数据，并输出“仅使用基础数据集训练”提示。
- 更新 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md` 和 `findings.md`，记录系统导出样本是补充数据源，不是训练入口硬性前置条件。

### 验证结果

- `uv run pytest tests/training/test_training_data.py`：1 passed。
- `uv run pytest tests/training/test_training_data.py tests/training/test_train_models_orchestration.py tests/training/test_export_training_data_cli.py`：9 passed。
- `uv run pytest tests/services/test_export_service.py tests/training/test_export_samples.py tests/training/test_training_data.py tests/training/test_train_models_orchestration.py tests/training/test_export_training_data_cli.py`：19 passed。

## 2026-05-07 grill-with-docs：导出训练样本不入库

### 本次已完成

- 根据用户确认的 Q23，将 `datasets/training_data_export.csv` 加入 `.gitignore`。
- 明确基础训练集 `datasets/framingham.csv` 继续作为项目基线数据保留，系统导出的训练样本属于本地可再生成产物。
- 更新 `CONTEXT.md`、`docs/architecture/ARCHITECTURE.md` 和 `findings.md`，记录导出样本不进入版本控制。

### 验证结果

- `git check-ignore -v datasets/training_data_export.csv`：命中 `.gitignore:43:/datasets/training_data_export.csv`。

## 2026-05-08 四期剩余架构优化计划整理

### 本次已完成

- 使用 `planning-with-files` 恢复并读取现有计划文件：
  - `task_plan.md`
  - `findings.md`
  - `progress.md`
- 使用 `improve-codebase-architecture` 对照 `CONTEXT.md`、ADR 和当前代码，整理四期剩余架构优化候选。
- 使用 `grill-with-docs` 的约束，把后续阶段都标记为 `discussion_required`，明确每项执行前必须先讨论。
- 将当前已完成但未登记的 **每日血压序列** Module 深化记录为阶段 23。
- 在 `task_plan.md` 追加四期剩余优化阶段：
  - 阶段 24：Prophet 每日血压序列训练窗口瘦身。
  - 阶段 25：周健康报告主 Module 命名收敛。
  - 阶段 26：今日健康任务读取与规则 Module 收敛。
  - 阶段 27：预测链路治理紧凑记录投影优化。
  - 阶段 28：紧凑预测记录后遗留兼容层清理。
  - 阶段 29：Prophet lifecycle 旧 Interface 收束。
- 在 `findings.md` 追加四期扫描发现、领域约束和 ADR 风险控制。

### 当前工作区状态

- 阶段 23 业务改动仍在工作区中，尚未 staging/commit。
- 本次只更新计划文件和发现/进度记录，没有执行新的业务代码优化。

### 下一步

- 从阶段 24 开始进入讨论。
- 每次只讨论一个阶段、一个设计问题；得到明确确认后才执行代码改动。

## 2026-05-08 阶段 24：Prophet 每日血压序列训练窗口瘦身

### 本次已完成

- 已完成执行前讨论并获得确认：
  - Prophet 读侧拆成 total metrics、训练窗口序列和新增自然日计数三类查询。
  - `data_signature` 只基于实际进入训练窗口的 **每日血压序列**。
  - 本阶段不引入物化 **每日血压序列** 表。
- 已将 `task_plan.md` 阶段 24 状态更新为 `in_progress`。
- 新增 `DailyBPSeriesRepository.count_daily_series_days()`、`load_recent_daily_series()` 和 `count_daily_series_days_after()`。
- `prophet_gateway._load_daily_records()` 改为读取总历史自然日数和最近训练窗口序列。
- `inspect_prophet_model_state_for_user()` 改为通过 `count_daily_series_days_after()` 统计新增自然日数，避免从裁剪后的 daily frame 反推。
- 已将 `task_plan.md` 阶段 24 状态更新为 `complete`。

### 验证结果

- 红灯确认：`uv run pytest tests/bp_series/test_daily_bp_series.py tests/prediction/test_prophet_gateway.py` 初次失败，原因是 `DailyBPSeriesRepository` 尚未提供三类读侧方法，`_load_daily_records()` 也未接收训练窗口参数。
- 目标测试通过：`uv run pytest tests/bp_series/test_daily_bp_series.py tests/prediction/test_prophet_gateway.py`，13 passed。
- 相关回归通过：`uv run pytest tests/bp_series/test_daily_bp_series.py tests/prediction/test_prophet_gateway.py tests/prediction/test_predict_use_case.py tests/prediction/test_prediction_governance_policy.py tests/prediction/test_prediction_governance_read_model.py tests/services/test_health_task_service.py tests/services/test_weekly_comparison_service.py`，37 passed。
- 后端全量回归通过：`uv run pytest`，180 passed。

## 2026-05-08 阶段 26：今日健康任务读取与规则 Module 收敛

### 本次已完成

- 已完成执行前讨论并获得确认：
  - 连续记录天数保持精确回溯，不做近期窗口近似。
  - 最近连续偏高预警只以 **每日血压序列** 为输入，删除 raw-record grouped dict 兼容路径。
  - `latest_record` 继续读取原始最新 **血压记录**，用于展示最近一次录入的具体时间、血压和心率。
- 已将 `task_plan.md` 阶段 26 状态更新为 `in_progress`。
- 调整健康任务测试，让 fake repository 只返回 `daily_series`，不再返回旧 `recorded_days/recent_daily_averages`。
- 新增测试保护 `HealthTaskService` 不再暴露 `_group_records_by_day()`。
- 删除 `HealthTaskService` 中 raw-record grouped dict 兼容分支；streak 和 alert 规则只接收 **每日血压序列**。
- 已将 `task_plan.md` 阶段 26 状态更新为 `complete`。

### 验证结果

- 红灯确认：`uv run pytest tests/services/test_health_task_service.py` 初次失败，原因是 `_group_records_by_day()` 旧 helper 仍存在。
- 阶段相关测试通过：`uv run pytest tests/services/test_health_task_service.py tests/bp_series/test_daily_bp_series.py tests/prediction/test_prophet_gateway.py tests/services/test_weekly_comparison_service.py`，18 passed。
- 后端全量回归通过：`uv run pytest`，181 passed。

## 2026-05-08 阶段 25：周健康报告主 Module 命名收敛

### 本次已完成

- 已完成执行前讨论并获得确认：
  - 后端主实现收束到 `WeeklyReportService`，`WeeklyComparison` 只保留兼容 alias。
  - 前端主组件和类型收束为 `WeeklyReport` 命名，旧 `WeeklyComparison` 导入只保留极薄 alias。
  - `/api/profile/weekly-comparison` 兼容入口继续保留，不删除、不加 warning。
- `backend/services/weekly_report_service.py` 改为真实主实现，包含 repository、calculator 和 service。
- `backend/services/weekly_comparison_service.py` 改为兼容 alias。
- 新增 `frontend/src/features/profile/components/WeeklyReportPanel.tsx`，旧 `WeeklyComparisonPanel.tsx` 转导出该主组件。
- `ProfilePage` 内部状态和加载函数改为 weekly report 命名。
- `frontend/src/types/profile.ts` 新增 `ProfileWeeklyReportSummary`，保留 `WeeklyComparisonSummary` 兼容 alias。
- 已将 `task_plan.md` 阶段 25 状态更新为 `complete`。

### 验证结果

- 后端阶段测试通过：`uv run pytest tests/services/test_weekly_comparison_service.py tests/routes/test_weekly_report_routes.py tests/routes/test_profile_routes.py`，11 passed。
- 前端阶段测试通过：`pnpm exec vitest run src/pages/ProfilePage.test.tsx src/features/weekly-report/presentation.test.ts`，3 passed。
- 后端全量回归通过：`uv run pytest`，182 passed。
- 前端验证通过：
  - `pnpm run typecheck`
  - `pnpm run lint`
  - `pnpm run test`，16 files / 34 tests passed。
- 浏览器验证通过：
  - `/weekly-report` 请求 `/api/weekly-report`，渲染 **周健康报告**、最近7天与前7天周期和四项对比指标。
  - `/profile?tab=trend` 请求 `/api/profile/weekly-comparison`，渲染同一份 **周健康报告** 展示模型。
  - 无 API 4xx/5xx 和 console error。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| Playwright mock 规则 `**/api/**` 误拦截 Vite 源码路径 `/src/features/weekly-report/api/weeklyReportApi.ts`，导致动态 import 404 | 1 | 改为只拦截 URL pathname 以 `/api/` 开头的请求 |

## 2026-05-08 阶段 27：预测链路治理紧凑记录投影优化

### 本次正在执行

- 已完成执行前讨论并获得确认：
  - 异常类型筛选使用 MySQL JSON 条件下推，不改 schema、不新增索引或派生表。
  - summary 的 `anomaly_counts` 按已知异常码分别计数，避免全量读取 `anomaly_flags` JSON 列。
  - fake/in-memory 查询测试保留 Python fallback。
- 已将 `task_plan.md` 阶段 27 状态更新为 `in_progress`。

### 本次已完成

- `PredictionGovernanceReadModel` 新增 `KNOWN_ANOMALY_TYPES` 与 `anomaly_flag_condition()`，异常类型条件使用 MySQL `JSON_CONTAINS`。
- `apply_anomaly_filters()` 对 `anomaly_type` 直接应用具体 JSON 条件；`has_anomaly` 继续表达“任意异常”。
- `list_predictions()` 和 `list_predictions_for_export()` 在非 in-memory 查询中先下推异常类型过滤，再分页或导出。
- in-memory 查询继续通过 `filter_by_anomaly_state()` 做 Python fallback。
- summary 的 `anomaly_counts` 改为按已知异常码分别计数，不再查询 `PredictionRecord.anomaly_flags` 全量 JSON 列。
- 已将 `task_plan.md` 阶段 27 状态更新为 `complete`。

### 验证结果

- 目标读模型测试通过：`uv run pytest tests/prediction/test_prediction_governance_read_model.py`，4 passed。
- 治理相关回归通过：`uv run pytest tests/prediction/test_prediction_governance_read_model.py tests/prediction/test_prediction_governance_policy.py tests/services/test_prediction_governance_service.py`，8 passed。
- 后端全量回归通过：`uv run pytest`，184 passed。

## 2026-05-08 阶段 28：紧凑预测记录后遗留兼容层清理讨论

### 已确认

- `NormalizedPredictionMapper` 暂时保留为兼容 Facade；内部主命名逐步迁向 `CompactPredictionMapper`，旧导入只作为 alias 过渡。
- `backfill_normalized_storage.py` 保留为兼容 no-op 入口，但文案和测试要说明它只是 ADR-0007 紧凑预测记录存储后的历史命令兼容，不执行数据库写入。
- 清理旧命名时新增紧凑记录主 Module，并保留旧 normalized 文件作为 alias；不一次性重命名或大范围移动所有文件。

### 本次补充扫描

- 生产侧 `NormalizedPredictionMapper` 默认实例化集中在 `prediction_record_repository.py`、`prediction_payload_assembler.py` 和 `repositories.py`。
- mapper 家族拆分为顶层 mapper、rows dataclass、input/forecast/fusion/training/recommendation mapping；当前命名仍是 normalized，但实际写入的是紧凑 `PredictionRecord` JSON payload。
- `backfill_normalized_storage.py` 已是 no-op，当前文案仍偏 Task 6/normalized-storage cutover，需要改成 ADR-0007 后历史命令兼容说明。
- 已在 `task_plan.md` 和 `findings.md` 记录下一处待确认问题：compact 主命名是否覆盖整个 mapper 家族，而不是只覆盖顶层 mapper。

### 用户确认

- 用户确认 compact 主命名覆盖整个 mapper 家族：顶层 mapper、rows、input/forecast/fusion/training/recommendation mapping 都新增 compact 主 Module。
- 旧 `normalized_prediction_*` 文件继续保留为 re-export alias，不做删除、重命名或大范围移动。
- 已将 `task_plan.md` 阶段 28 状态更新为 `in_progress`。

### 本次已完成

- 新增 compact 主 mapper 家族：
  - `backend/prediction/infrastructure/compact_prediction_mapper.py`
  - `backend/prediction/infrastructure/compact_prediction_rows.py`
  - `backend/prediction/infrastructure/compact_prediction_input_mapping.py`
  - `backend/prediction/infrastructure/compact_prediction_forecast_mapping.py`
  - `backend/prediction/infrastructure/compact_prediction_fusion_mapping.py`
  - `backend/prediction/infrastructure/compact_prediction_training_mapping.py`
  - `backend/prediction/infrastructure/compact_prediction_recommendation_mapping.py`
- 将旧 `normalized_prediction_*` 文件改为 re-export alias，保留旧导入兼容。
- `PredictionPayloadAssembler`、`PredictionRecordRepository` 和 `PredictionRepository` 默认使用 `CompactPredictionMapper`。
- `PredictionRecordRepository.save_prediction()` 优先调用 `build_compact_prediction()`，并保留旧 mapper fallback。
- `backfill_normalized_storage.py` 继续作为 no-op 兼容入口，文案改为 ADR-0007 后历史命令兼容。
- 已将 `task_plan.md` 阶段 28 状态更新为 `complete`。

### 验证结果

- 红灯确认：`uv run pytest tests/prediction/test_compact_prediction_mapper.py` 初次失败，原因是 `prediction.infrastructure.compact_prediction_forecast_mapping` 等 compact Module 尚未存在。
- 新增 compact mapper 目标测试通过：`uv run pytest tests/prediction/test_compact_prediction_mapper.py`，5 passed。
- 旧 normalized 兼容与 repository 边界测试通过：`uv run pytest tests/prediction/test_normalized_prediction_mapper.py tests/prediction/test_prediction_repository_boundaries.py`，30 passed。
- 阶段相关回归通过：`uv run pytest tests/prediction/test_compact_prediction_mapper.py tests/prediction/test_normalized_prediction_mapper.py tests/prediction/test_prediction_repository_boundaries.py tests/prediction/test_prediction_governance_read_model.py tests/prediction/test_prediction_governance_policy.py tests/services/test_prediction_governance_service.py tests/prediction/test_predict_use_case.py`，58 passed。
- 后端全量回归通过：`uv run pytest`，189 passed。
- 收尾复跑后端全量：`uv run pytest`，189 passed。

## 2026-05-08 阶段 29：Prophet lifecycle 旧 Interface 收束讨论

### 本次补充扫描

- 业务调用路径只使用 `ProphetGateway.predict(user_id, forecast_days)`，没有业务调用方传入 Prophet lifecycle `model_state`。
- `services.prediction_service.predict_bp_trend_for_user()` 兼容 wrapper 也只暴露 `user_id` 和 `forecast_days`。
- `prophet_gateway.predict_bp_trend_for_user(..., model_state=...)` 与 `_predict_bp_trend_from_model_state()` 只在 Prophet gateway 测试中直接使用。
- `ProphetModelLifecycle.__init__(predict_from_model_state=...)` 的 legacy 分支只在 sequence 测试中使用；生产路径已经走正式的 `load_or_train_models`、`predict_from_models`、`build_training_meta` 协作接口。
- `PredictionInputSnapshot.to_persistence_payload(model_state=...)` 是预测结果持久化快照，不属于本阶段要收束的旧 Prophet lifecycle Interface。

### 用户确认

- 移除公开 Prophet 预测入口的 `model_state` 参数；`predict_bp_trend_for_user()` 和 `ProphetGateway.predict()` 只保留 `user_id, forecast_days`。
- 保留 `ProphetModelLifecycle.predict_from_model_state()` 作为 lifecycle 内部/测试 seam。
- 测试注入已构造 state 时，直接测 lifecycle，不再通过公开 gateway 入口。
- 已将 `task_plan.md` 阶段 29 状态更新为 `in_progress`。

### 本次已完成

- `ProphetModelLifecycle.__init__()` 删除 legacy `predict_from_model_state` 注入参数。
- `ProphetModelLifecycle.predict_from_model_state()` 改为显式 keyword-only `model_state`，继续作为 lifecycle 内部/测试 seam。
- `prophet_gateway.predict_bp_trend_for_user()` 公开签名收窄为 `user_id, forecast_days`。
- 删除 `_predict_bp_trend_from_model_state()` helper。
- 将复用已有模型和禁用复用重训两类测试改为直接构造 `ProphetModelLifecycle` 并调用 `predict_from_model_state()`。
- `test_predict_use_case.py` 的 fake Prophet gateway 同步收窄为 `predict(user_id, forecast_days)`。
- 已将 `task_plan.md` 阶段 29 状态更新为 `complete`。

### 验证结果

- 红灯确认：`uv run pytest tests/prediction/test_prophet_gateway.py` 初次失败，原因是 `predict_bp_trend_for_user` 公开签名仍包含 `model_state`。
- 目标 Prophet gateway 测试通过：`uv run pytest tests/prediction/test_prophet_gateway.py`，9 passed。
- 阶段相关回归通过：`uv run pytest tests/prediction/test_prophet_gateway.py tests/prediction/test_predict_use_case.py tests/prediction/test_prediction_run_policies.py tests/prediction/test_prediction_repository_boundaries.py`，45 passed。
- 后端全量回归通过：`uv run pytest`，190 passed。
- 收尾复跑后端全量：`uv run pytest`，190 passed。

## 2026-05-08 最后一轮清理方案生成

### 本次已完成

- 使用 `planning-with-files` 恢复并读取现有 `task_plan.md`、`findings.md`、`progress.md`。
- 使用 `improve-codebase-architecture` 对照 `CONTEXT.md` 和 ADR，按 Module、Interface、Depth、Locality 视角扫描旧残留。
- 使用 `grill-with-docs` 约束检查已有领域决策，特别是 ADR-0007、**周健康报告** 兼容入口和 **7天风险预测** 固定周期。
- 扫描后端 route、前端请求、compact/normalized mapper、旧 cache 语义、Prophet 命名残留、认证入口和开发调试入口。
- 重新生成 `task_plan.md`，替换旧的超长阶段历史，聚焦最后一轮清理计划。
- 更新 `findings.md`，追加本轮旧 Interface 清理扫描证据。

### 当前结论

- 工作区扫描前是干净状态。
- 本次只生成方案和计划文件，没有修改业务代码。
- 推荐下一轮从 `task_plan.md` 阶段 0 开始，先跑保护网，再逐项删除旧 Interface。

### 尚未执行

- 尚未删除任何旧 route、alias、Module 或测试。
- 尚未运行新的后端/前端验证命令；本次是方案生成。
- 阶段 5 的 **周健康报告** 兼容入口是否删除仍需最终确认。

## 2026-05-08 最后一轮清理阶段 0：保护网与接口清单

### 本次已完成

- 使用 `planning-with-files` 恢复现有 `task_plan.md`、`findings.md`、`progress.md`。
- 使用 `grill-me` 执行“能从代码库回答的问题先扫描代码库”的规则。
- 已将 `task_plan.md` 阶段 0 状态更新为 `in_progress`。
- 本阶段只运行验证和收集接口调用证据，不删除业务接口。
- 生成阶段 0 接口清单与分类证据：
  - `docs/agents/final-interface-cleanup-phase0.md`
- 更新 `findings.md`，记录本轮 route、前端请求和待删 Interface 分类。

### 验证结果

- 后端全量：`uv run pytest`，190 passed。
- 前端 typecheck：`pnpm run typecheck`，通过。
- 前端 lint：`pnpm run lint`，通过。
- 前端全量测试：`pnpm run test`，16 files / 34 tests passed。

### 阶段 0 结论

- `PredictionRouteCacheService` 和 `build_cache_snapshot` 属于最干净的删除候选。
- `/api/auth/login` 前端无调用，删除风险主要在后端测试和任何外部手写调用。
- `/api/prophet-predictions` GET 仍被前端个人中心趋势图使用，不能直接删除，需要阶段 2 先做新趋势投影 Interface。
- `/api/profile/weekly-comparison` 仍是生产兼容入口，阶段 5 需要明确是否推翻上一轮保留决定。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| PowerShell 前端请求扫描命令存在多余 `}`，解析失败 | 2 | 改用更窄的 `rg` 扫描，并排除 `backend/static`、测试和规划文件噪声 |

## 2026-05-08 阶段 1：旧 cache Interface 删除

### 用户确认

- 用户同意先删除 `PredictionRouteCacheService` 和 `prediction.domain.cache_policy.build_cache_snapshot` 这两个无生产调用的旧 cache Interface。

### 本次已完成

- 已将 `task_plan.md` 阶段 1 状态更新为 `in_progress`。
- 按 TDD 增加红灯测试：`test_old_prediction_cache_interfaces_are_removed()`。
- 删除旧兼容文件：
  - `backend/services/prediction_route_cache_service.py`
  - `backend/prediction/domain/cache_policy.py`
- 从 domain 聚合导出中移除 `build_cache_snapshot`：
  - `backend/prediction/domain/__init__.py`
  - `backend/prediction/domain/policies.py`
- 更新 `findings.md`，记录删除范围和保留到后续的小步。

### 验证结果

- 红灯确认：`uv run pytest tests/routes/test_predictions_cache_helpers.py` 初次失败，原因是 `services.prediction_route_cache_service` 仍可解析。
- 目标测试通过：`uv run pytest tests/routes/test_predictions_cache_helpers.py`，5 passed。
- 阶段相关回归通过：`uv run pytest tests/routes/test_predictions_cache_helpers.py tests/prediction/test_predict_use_case.py tests/prediction/test_prediction_run_policies.py`，23 passed。
- 后端全量回归通过：`uv run pytest`，191 passed。
- 删除后扫描：`rg "PredictionRouteCacheService|prediction_route_cache_service|build_cache_snapshot|cache_policy"` 只剩测试中的不可导入断言。

### 尚未执行

- 本阶段旧 cache/result-cache Interface 已完成清理。
- `backend/config.py` 中 `PROPHET_RESULT_CACHE_HOURS` 暂未修改，避免未经确认触碰生产配置；后续如需删除配置项，单独确认。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| `backend/services/__init__.py` 不存在 | 1 | 确认 services 目录没有聚合导出文件，不需要修改 |

## 2026-05-08 阶段 1：result cache 字段删除

### 用户确认

- 用户确认继续删除 `PredictionResult` 里的旧 result cache 字段。

### 本次已完成

- 红灯测试确认旧字段仍存在时失败。
- 从 `PredictionResult` 删除：
  - `from_cache`
  - `cached_at`
  - `cache_expires_at`
  - `reuse_window_minutes`
  - `result_cache_hours`
- 从预测结果 builder 和历史 payload assembler 移除旧 result cache 输出。
- 从 `PredictUseCase`、`PredictionRun`、`PredictionUseCaseFactory` 移除 `model_reuse_window` 和 `result_metadata_window` 注入。
- 删除 `PredictionRunMetadataService` 旧 cache-window/run-key class，保留 `PredictionRecordRetentionService`。
- 前端 `PredictionCacheMode` 删除 `hot_reuse` 和 `persistent_reuse`，保留 `fresh_train`、`model_reuse` 和开放字符串兜底。
- 已将 `task_plan.md` 阶段 1 标记为 `complete`。
- 更新 `findings.md` 记录本阶段删除范围和生产配置保留原因。

### 验证结果

- 红灯确认：`uv run pytest tests/prediction/test_predict_use_case.py tests/prediction/test_prediction_run_policies.py` 失败，原因是 `PredictionResult` 仍有旧 result cache 字段。
- 红灯确认：`uv run pytest tests/routes/test_predictions_route_use_cases.py::test_prediction_use_case_factory_centralizes_use_case_assembly ...` 失败，原因是 `PredictUseCase` 仍有 `model_reuse_window`。
- 红灯确认：`uv run pytest tests/prediction/test_prediction_repository_boundaries.py` 失败，原因是 assembler 仍输出 `from_cache`。
- 红灯确认：`uv run pytest tests/routes/test_predictions_cache_helpers.py` 失败，原因是 `PredictionRunMetadataService` 仍存在。
- 阶段相关回归通过：`uv run pytest tests/routes/test_predictions_cache_helpers.py tests/prediction/test_predict_use_case.py tests/prediction/test_prediction_run_policies.py tests/prediction/test_prediction_repository_boundaries.py tests/routes/test_predictions_route_use_cases.py`，54 passed。
- 后端全量回归通过：`uv run pytest`，190 passed。
- 前端验证通过：
  - `pnpm run typecheck`
  - `pnpm run lint`
  - `pnpm run test`，16 files / 34 tests passed。
- 清理后扫描：旧 cache/result-cache 关键词在生产源码范围内无命中，只剩测试中的“不可存在”断言。

## 2026-05-08 阶段 2：个人中心预测趋势投影 Interface 优化

### 本次已完成

- 为个人中心新增趋势 route：`GET /api/profile/prediction-trend`。
- 删除旧 Prophet 趋势 use case 与 route：
  - `backend/prediction/application/list_prophet_predictions.py`
  - `backend/prediction/application/delete_prophet_prediction.py`
  - `GET /api/prophet-predictions`
  - `DELETE /api/prophet-predictions/<id>`
- 新增 `ListPredictionTrendUseCase`，并让 composition / actions / repository 全部切到 `list_prediction_trend()`。
- `PredictionRecordRepository.list_prediction_trend()` 已收窄为轻量 projection 查询，不再组装完整预测 payload。
- 前端个人中心趋势图 API 改为 `getPredictionTrend()`，请求路径改为 `/api/profile/prediction-trend?limit=...`。
- 更新后端 route/use case/repository 测试与前端 API 测试，删除旧 Prophet 趋势测试残留。
- 同步修正 `README.md` 接口列表。

### 验证结果

- 红灯确认（前序会话已记录）：
  - `backend/tests/routes/test_profile_routes.py` 新增 profile 趋势 route 测试在实现前失败。
  - `backend/tests/routes/test_predictions_route_use_cases.py` 新增“旧 Prophet trend helper 不再存在”测试在实现前失败。
  - `frontend/src/features/profile/api/profilePredictionApi.test.ts` 在实现前失败，确认前端尚未请求新路径。
- 定向验证通过：
  - `uv run pytest tests/routes/test_profile_routes.py tests/routes/test_predictions_route_use_cases.py tests/prediction/test_prediction_repository_boundaries.py`，38 passed。
  - `pnpm exec vitest run src/features/profile/api/profilePredictionApi.test.ts`，1 file / 1 test passed。
- 全量验证通过：
  - `uv run pytest`，190 passed。
  - `pnpm run typecheck`，通过。
  - `pnpm run lint`，通过。
  - `pnpm run test`，17 files / 35 tests passed。

### 说明

- 本轮未修改数据库结构、迁移脚本或生产配置。
- 由于当前会话未提供可直接使用的浏览器自动化工具，本轮以定向前端测试和全量回归作为趋势页切换的主要验证证据；如需，我下一步可以继续起本地服务并补一轮手工/自动化页面走查。

## 2026-05-08 阶段 3：compact mapper 后旧 normalized 兼容层收尾（进行中）

### 本次已完成

- 红灯测试先确认以下行为仍旧存在：
  - `PredictionInputSnapshot.to_persistence_payload()` 仍写入 `_cache_snapshot` / `_prophet_cache_key`
  - `CompactPredictionWriteMapper` 仍暴露 `build_normalized_prediction()`
  - `build_input_snapshot()` 仍会把 legacy key 以 `None` 形式写回
  - `PredictionRecordRepository.save_prediction()` 仍接受 legacy-only normalized mapper
- 已收紧写入路径：
  - `backend/prediction/schemas/input_snapshot.py`
  - `backend/prediction/infrastructure/compact_prediction_input_mapping.py`
  - `backend/prediction/infrastructure/compact_prediction_mapper.py`
  - `backend/prediction/infrastructure/prediction_record_repository.py`
- 已更新相关测试，覆盖：
  - 新写入只保留 `_model_state_snapshot` / `_prediction_run_key`
  - 新记录读取不再补出 legacy key
  - 旧记录读取仍能把 legacy key 映射回新 key
  - repository 写入边界只接受 compact mapper
- 已扫描 `normalized_prediction_*` 与 `backfill_normalized_storage.py`：
  - 非测试生产代码无 `normalized_prediction_*` 导入命中
  - 非测试生产代码无 `backfill_prediction_storage` / `backfill_normalized_storage` 调用命中
  - 删除这些现有文件前仍需用户确认

### 验证结果

- 红灯确认：
  - `uv run pytest tests/prediction/test_predict_use_case.py tests/prediction/test_compact_prediction_mapper.py tests/prediction/test_normalized_prediction_mapper.py tests/prediction/test_prediction_repository_boundaries.py` 初次失败，7 failed / 46 passed；失败点均落在 legacy key 写入、legacy write alias、repository fallback 三类预期位置。
- 定向验证通过：
  - `uv run pytest tests/prediction/test_predict_use_case.py tests/prediction/test_compact_prediction_mapper.py tests/prediction/test_normalized_prediction_mapper.py tests/prediction/test_prediction_repository_boundaries.py`，54 passed。
- 全量验证通过：
  - `uv run pytest`，193 passed。
  - `pnpm run typecheck`，通过。
  - `pnpm run lint`，通过。
  - `pnpm run test`，17 files / 35 tests passed。

### 待确认

- `normalized_prediction_forecast_mapping.py`
- `normalized_prediction_fusion_mapping.py`
- `normalized_prediction_input_mapping.py`
- `normalized_prediction_mapper.py`
- `normalized_prediction_recommendation_mapping.py`
- `normalized_prediction_rows.py`
- `normalized_prediction_training_mapping.py`
- `backend/prediction/infrastructure/backfill_normalized_storage.py`

这些文件当前看起来只剩兼容壳和测试引用；若继续删除，需要用户确认删除范围。

### 用户确认后的收尾

- 用户选择激进方案 `2`，确认删除全部 `normalized_prediction_*` 与 `backfill_normalized_storage.py`。
- 已删除以上 8 个兼容文件。
- 已删除测试文件：
  - `backend/tests/prediction/test_normalized_prediction_mapper.py`
- 已更新 compact mapper 测试，改为断言以下旧模块不可导入：
  - `prediction.infrastructure.normalized_prediction_*`
  - `prediction.infrastructure.backfill_normalized_storage`
- 已同步更新：
  - `docs/architecture/ARCHITECTURE.md`

### 删除后验证结果

- 残留扫描通过：生产源码范围内不再存在 `normalized_prediction_*` / `backfill_normalized_storage` 文件或导入，只剩历史清单文档中的阶段 0 快照记录。
- 定向验证通过：
  - `uv run pytest tests/prediction/test_compact_prediction_mapper.py tests/prediction/test_predict_use_case.py tests/prediction/test_prediction_repository_boundaries.py`，47 passed。
- 全量验证通过：
- `uv run pytest`，186 passed。
- `pnpm run typecheck`，通过。
- `pnpm run lint`，通过。
- `pnpm run test`，17 files / 35 tests passed。

## 2026-05-08 阶段 4：认证与开发调试入口清理

### 本次已完成

- 红灯测试确认：
  - `auth` 模块仍暴露旧 `login()` route handler
  - `create_app()` 在 `ENABLE_LOCAL_MOCK_EMAIL_SERVICE=False` 时仍注册 `/api/dev/mock-emails/latest`
- 已删除后端模糊登录入口：
  - `backend/routes/auth.py` 不再定义 `POST /api/auth/login`
- 已收紧 dev tools 注册：
  - `backend/app.py` 仅在 `ENABLE_LOCAL_MOCK_EMAIL_SERVICE=True` 时注册 `dev_tools_bp`
- 已新增 app 级测试：
  - `backend/tests/routes/test_dev_tools_routes.py`
- 已更新 auth route 测试，改为通过 `/api/auth/login/user` 覆盖普通用户登录行为，并显式断言旧 `login` 入口不存在。
- 已同步修正 `README.md` 的认证与开发辅助接口清单。

### 验证结果

- 红灯确认：
  - `uv run pytest tests/routes/test_auth_routes.py tests/routes/test_dev_tools_routes.py` 初次失败，2 failed / 18 passed；失败点分别落在旧 `login` route 仍存在，以及 mock email route 仍被无条件注册。
- 定向验证通过：
  - `uv run pytest tests/routes/test_auth_routes.py tests/routes/test_dev_tools_routes.py`，20 passed。
- 全量验证通过：
  - `uv run pytest`，186 passed。
  - `pnpm run typecheck`，通过。
  - `pnpm run lint`，通过。
  - `pnpm run test`，17 files / 35 tests passed。

### 说明

- 本阶段未修改数据库结构、迁移脚本或生产配置。
- 前端登录与 mock email 调用链在实现前就已符合目标，因此本阶段未做前端代码修改，只保留验证与文档同步。

## 2026-05-08 阶段 5：周健康报告兼容入口最终收尾

### 本次已完成

- 红灯测试确认：
  - `profile` 模块仍暴露 `build_weekly_comparison_service()` / `get_weekly_comparison()`
  - `services.weekly_comparison_service` 仍可导入
- 已删除后端 weekly-comparison 兼容层：
  - `backend/routes/profile.py` 中的 compatibility factory 和 route
  - `backend/services/weekly_comparison_service.py`
- 已删除前端 weekly-comparison 兼容层：
  - `frontend/src/features/profile/api/profileComparisonApi.ts`
  - `frontend/src/features/profile/components/WeeklyComparisonPanel.tsx`
  - `frontend/src/features/profile/index.ts` 中的 comparison alias 导出
  - `frontend/src/types/profile.ts` 中的 `WeeklyComparisonSummary`
- 已统一 canonical weekly report 调用：
  - `frontend/src/features/weekly-report/api/weeklyReportApi.ts` 只保留 `getWeeklyReport()`
  - `frontend/src/features/weekly-report/index.ts` 只导出 `getWeeklyReport()`
  - `frontend/src/pages/ProfilePage.tsx` 改为直接调用 `getWeeklyReport()`
- 已将服务测试重命名为 canonical weekly report 版本，并新增前端 API 测试：
  - `backend/tests/services/test_weekly_report_service.py`
  - `frontend/src/features/weekly-report/api/weeklyReportApi.test.ts`

### 验证结果

- 红灯确认：
  - `uv run pytest tests/routes/test_profile_routes.py tests/services/test_weekly_report_service.py` 初次失败，2 failed / 9 passed；失败点正落在旧 profile compatibility route 和旧 service module 仍存在。
- 定向验证通过：
  - `uv run pytest tests/routes/test_profile_routes.py tests/services/test_weekly_report_service.py`，11 passed。
  - `pnpm exec vitest run src/features/weekly-report/api/weeklyReportApi.test.ts src/pages/ProfilePage.test.tsx`，2 files / 2 tests passed。
- 全量验证通过：
  - `uv run pytest`，189 passed。
  - `pnpm run typecheck`，通过。
  - `pnpm run lint`，通过。
  - `pnpm run test`，18 files / 36 tests passed。

### 说明

- 生产源码扫描后，`weekly-comparison` 相关命中只剩阶段 0 历史清单文档，属于保留的过程记录。
- 本阶段未修改数据库结构、迁移脚本或生产配置。

## 2026-05-08 grill-with-docs：阶段 6 文档收敛口径

### 已确认

- 当前有效文档需要清理旧 Interface 表述，避免误导后续开发。
- 历史记录文件保留旧 Interface 引用作为过程证据，不做伪历史清理。
- 历史记录文件包括 `findings.md`、`progress.md` 和 `docs/agents/final-interface-cleanup-phase0.md`。
- 如需降低 grep 噪声，只在历史记录文件顶部补充“历史扫描快照不代表当前 Interface”的说明。

### 本次已更新

- 已将该口径写入 `task_plan.md` 阶段 6。

## 2026-05-08 阶段 6：旧 Interface 文档残留扫描

### 本次已完成

- 扫描旧 result cache、Prophet prediction history、normalized storage、weekly-comparison 等关键词。
- 当前生产源码里旧 route、旧 alias 和旧 normalized 文件已不再存在；相关命中主要剩历史记录文件和“不可存在”保护测试。
- `PROPHET_RESULT_CACHE_HOURS` 只剩 `backend/config.py` 与 `README.md` 环境变量示例命中，代码路径中未发现真实使用方。

### 待确认

- `backend/config.py` 属于生产配置范围；是否删除未使用的 `PROPHET_RESULT_CACHE_HOURS` 需要单独确认后再改。

## 2026-05-08 阶段 6：配置与历史快照说明收尾

### 用户确认

- 用户确认删除未使用的 `PROPHET_RESULT_CACHE_HOURS`。

### 本次已完成

- 已从 `backend/config.py` 删除 `PROPHET_RESULT_CACHE_HOURS`。
- 已从 `README.md` 环境变量示例删除 `PROPHET_RESULT_CACHE_HOURS`。
- 已把 `CONTEXT.md` 中 `weekly-comparison` 的说明改为历史兼容叫法，不再暗示当前仍有过渡接口。
- 已在 `findings.md`、`progress.md` 和 `docs/agents/final-interface-cleanup-phase0.md` 顶部补充历史快照说明。
- 已将 `task_plan.md` 阶段 6 标记为 complete。

### 验证结果

- 后端全量：`uv run pytest`，189 passed。
- 前端：`pnpm run typecheck`、`pnpm run lint`、`pnpm run test`，均通过。

## 2026-05-08 阶段 7：论文准备最终体检与演示包收口

### 本次已完成

- 使用 `improve-codebase-architecture` 和 `grill-with-docs` 对照当前领域文档，扫描旧 Interface、论文高风险词、迁移历史、前端构建产物和演示脚本。
- 发现 `backend/static` 本地构建产物仍引用旧接口 `/api/prophet-predictions` 与 `/api/profile/weekly-comparison`，风险集中在 `start.bat --skip-build` 单服务演示。
- 已运行 `pnpm build` 刷新 `backend/static`，新构建不再命中旧接口关键词。
- 已清理项目源码范围内 24 个 `__pycache__` 目录，排除 `.venv`。
- 已将前端预测趋势图错误提示改为“预测趋势接口状态”。
- 已更新 `task_plan.md` 与 `findings.md`，记录阶段 7 缺陷和新功能候选。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| 尝试删除 `.codex-*` 日志时文件被当前进程占用 | 1 | 保留这些运行时日志；它们被 `.gitignore` 忽略，不影响源码或演示构建 |

### 验证结果

- 前端定向测试：`pnpm exec vitest run src/features/profile/api/profilePredictionApi.test.ts src/pages/ProfilePage.test.tsx`，2 files / 2 tests passed。
- 后端全量：`uv run pytest`，189 passed。
- 前端：`pnpm run typecheck`，通过。
- 前端：`pnpm run lint`，通过。
- 前端：`pnpm run test`，18 files / 36 tests passed。
- 前端生产构建：`pnpm build`，通过，输出到 `backend/static`。
- 旧 Interface 关键词扫描：有效源码和 `backend/static` 无命中；剩余命中只在保护测试中。

## 2026-05-09 阶段 8：论文正式写作计划落盘

### 本次已完成

- 按 `planning-with-files` 工作流恢复并读取现有 `task_plan.md`、`progress.md`、`findings.md`。
- 读取论文写作准备稿：`lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-论文写作准备稿.md`。
- 已在 `task_plan.md` 新增“阶段 8：论文正式写作与交付计划”。
- 阶段 8 已写入：
  - 总体写作原则。
  - 已冻结目录。
  - 字数预算。
  - 参考文献池检索与核验计划。
  - 图表与截图资产准备计划。
  - 章节正文写作顺序。
  - Word 成稿与附件交付计划。
  - 第4章图表清单。
  - 公式与算法表达计划。
  - 验收标准与风险控制。
- 已同步更新 `findings.md`，记录第8阶段写作计划发现。

### 验证结果

- 本次只更新计划与记录文件，未修改代码，未运行测试。

## 2026-05-09 阶段 8.1：参考文献池检索与核验

### 本次已完成

- 使用 `academic-search` 与 `lunwen` 工作流执行参考文献池建设。
- 读取并遵守论文阶段计划中的第8阶段要求。
- 通过 Crossref 查询并核验 DOI 元数据。
- 通过 OpenAlex 查询开放获取状态、开放 PDF 和引用量参考。
- 通过 PubMed 查询 PMID。
- 通过 Unpaywall 查询开放获取状态。
- 通过期刊官网核验《中国高血压防治指南（2024年修订版）》。
- 通过 DBLP、NeurIPS Proceedings 和 NeurIPS PDF 核验 LightGBM 原始论文。
- 已生成参考文献核验清单：
  - `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-参考文献核验清单.json`
- 已生成参考文献池：
  - `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-参考文献池.md`
- 已将 `task_plan.md` 中阶段 8 标记为 `in_progress`，阶段 8.1 标记为 `complete`。
- 已同步更新 `findings.md`，记录参考文献池核验结果。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
| --- | ---: | --- |
| `academic-search` 的 bash 依赖检查脚本在 Windows 路径下未能直接执行 | 1 | 不阻塞 API 检索；改用 PowerShell/Python 直接调用 Crossref、OpenAlex、PubMed、Unpaywall |
| Semantic Scholar batch API 返回 429 | 1 | 不重试同一路径；改用 OpenAlex `cited_by_count` 作为引用量参考 |
| Unpaywall 使用示例邮箱域名时返回 422 | 1 | 改用可接受格式的联系邮箱参数后成功查询 |

### 验证结果

- JSON 语法校验通过：`python -m json.tool lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-参考文献核验清单.json`。
- 本次只新增论文资料文件和更新计划/记录文件，未修改代码，未运行测试。

## 2026-05-09 阶段 8.2：图表与截图资产准备

### 本次已完成

- 使用 Mermaid 资产继续完成第4章图表闭环，确认 5 张图均已有 `.mmd`、`.png`、`.svg`。
- 运行 `backend/scripts/seed_demo_users.py` 生成截图用普通用户数据。
- 通过真实预测用例为 demo 用户生成预测记录，包含高风险、中风险、低风险和 `model_reuse` 运行模式样例。
- 新增演示管理员账号 `demo_admin_showcase`，用于管理员端预测结果治理截图，不修改原管理员账号。
- 启动本地服务：
  - 后端：`uv run flask --app app:create_app run --host 127.0.0.1 --port 5000`
  - 前端：`pnpm dev -- --host 127.0.0.1 --port 5173`
- 使用 Playwright 抓取第4章页面截图：
  - `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-6-risk-factor-profile-page.png`
  - `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-7-bp-records-page.png`
  - `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-8-risk-prediction-page.png`
  - `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-9-prediction-result-page.png`
  - `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-10-prediction-history-page.png`
  - `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-11-prediction-governance-page.png`
- 新增图片清单：
  - `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-图片清单.md`
- 已将 `task_plan.md` 阶段 8.2 标记为 complete，并修正第4章图表编号。

### 验证结果

- 实际预测调用通过，生成高风险样例：风险概率约 80.5%，风险等级为高风险。
- Playwright 用户端和管理员端控制台检查均为 0 errors。
- 截图尺寸核验通过：
  - 风险因素档案页：1440 x 1343。
  - 血压记录页：1440 x 1254。
  - 风险预测页：1440 x 1100。
  - 预测结果页：1440 x 2338。
  - 预测历史页：1440 x 1100。
  - 预测结果治理页：1440 x 3454。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
| --- | ---: | --- |
| `npx --package playwright node -e` 无法直接 `require('playwright')` | 1 | 改用 `@playwright/cli` 的 session、storage state 和 screenshot 命令 |
| 管理员 `dream/change-me` 登录失败 | 1 | 不改原管理员账号，新增 `demo_admin_showcase` 演示管理员 |

## 2026-05-09 论文资料目录收拢

### 本次已完成

- 按用户要求，将论文文档与正文资源保留在 `lunwen-doc/`，将中间产物移入 `output/`。
- `lunwen-doc/论文写作材料/` 当前保留：
  - 论文写作准备稿。
  - 参考文献池与参考文献核验清单。
  - 图片清单。
  - `thesis-assets/` 图表和截图资产。
- 已移动到 `output/lunwen-intermediate/`：
  - `analysis/` 样式分析 JSON 和样文页面截图。
  - `doc-text/` 任务书、开题报告文本抽取结果。
  - `thesis_analysis/` 样文/规范分析结果、临时脚本和临时日志。
- 已新增 `output/lunwen-intermediate/README.md`，说明中间产物目录边界。
- 已新增 `lunwen-doc/论文写作材料/README.md`，说明目录用途和后续成稿文件位置。
- 已更新 `task_plan.md`、`findings.md`、`progress.md` 和 `lunwen-doc/论文写作材料/README.md` 中的当前有效路径说明。

### 说明

- 原始学校规范、样文、任务书、开题报告仍保留在 `lunwen-doc/` 根目录，未改名、未删除。
- `output/` 中剩余内容主要是开发验证日志、旧 UI 截图和非当前论文交付资产，未纳入本次论文资料目录。

## 2026-05-09 阶段 8.1：参考文献池中文优先比例调整

### 本次已完成

- 使用 `academic-search` 口径复核参考文献池。
- 按用户“尽量找中文的，把控好比例 8:2”要求，将参考文献池调整为中文优先版本。
- 当前参考文献池共 15 篇：
  - 中文 12 篇。
  - 英文 3 篇。
- 英文条目仅保留 Prophet、LightGBM 的模型源头论文和 1 篇高相关高血压可视化风险预测系统论文。
- 已同步更新：
  - `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-参考文献池.md`
  - `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-参考文献核验清单.json`
  - `task_plan.md`
  - `findings.md`

### 验证结果

- 参考文献核验清单 JSON 语法校验通过。
- JSON 统计结果：`zh=12`，`en=3`，符合 80%:20% 比例。

### 下一步

- 进入第3章正文写作，优先使用中文高血压风险预测和健康管理文献支撑数据集、特征构建与评价指标部分。

## 2026-05-09 阶段 8.3：主论文 Markdown 初稿

### 本次已完成

- 使用 `lunwen` 与 `planning-with-files` 工作流进入论文正文写作。
- 读取并对齐：
  - `task_plan.md`
  - `findings.md`
  - `progress.md`
  - 论文写作准备稿
  - 参考文献池
  - 图片清单
  - `docs/model_report.md`
  - `CONTEXT.md`
  - `docs/architecture/ARCHITECTURE.md`
- 已创建主论文 Markdown 初稿：
  - `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现.md`
- 初稿已包含：
  - 中文摘要与关键词。
  - 英文摘要与关键词。
  - 第1章至第6章正文。
  - 第4章 11 张图表/截图引用。
  - 第5章 LightGBM 训练指标、混淆矩阵、特征重要性和 Prophet 运行策略。
  - 致谢。
  - 15 篇参考文献。
- 已更新：
  - `lunwen-doc/论文写作材料/README.md`
  - `task_plan.md`
  - `findings.md`

### 验证结果

- Markdown 结构统计：
  - 字符数：22777。
  - 行数：468。
  - 一级标题：1。
  - 二级标题：10。
  - 三级标题：25。
- 第4章所有图片路径校验通过。
- 参考文献核验清单 JSON 校验通过。
- 禁用/敏感表述扫描结果：
  - “患者”仅出现在参考文献题名中。
  - “临床诊断”“处方”“治疗方案”等只出现在边界否定表述中，用于说明系统不替代诊断或治疗决策。

### 下一步

- 对 Markdown 初稿进行二轮润色，重点压缩重复边界说明、增强第1章研究现状和第4章模型链路叙述。
- 之后进入 Word 成稿与附件生成阶段。

