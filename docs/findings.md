# HPS 架构深化发现记录

> 注：本文包含历史扫描快照和阶段性决策记录。旧 Interface 名称出现在历史段落中时，只表示当时的发现证据，不代表当前仍然存在或推荐继续使用。

## 已确认的项目决策

- 双模型预测引擎采用 Prophet + LightGBM 串联，不做模型投票。
- Prophet 用于血压趋势预测，LightGBM 输出高血压发病风险概率。
- 当前预测期血压特征取未来预测收缩压、舒张压均值。
- 预测记录创建后不可变。
- 系统是高血压风险预测系统，不是临床诊断系统。
- 指南型健康建议基于中国高血压防治指南（2024年修订版），不是 LLM 自由生成，也不是处方。

## 架构观察

### 双模型预测引擎

`backend/prediction/application/predict_use_case.py` 是核心编排点，但目前承担较多细节：

- 结果 cache key 构造。
- 用户个人风险因素快照组装。
- 风险融合。
- 指南型健康建议信号组装。
- 保存 payload 组装。
- fresh result 与 cached result 响应组装。

这说明 `PredictUseCase` 有深化空间。删除它会让大量复杂度回流到路由或测试中，所以它不是无用 Module；问题是 Interface 和实现细节仍纠缠。

### Prophet 模型生命周期

`backend/prediction/infrastructure/prophet_gateway.py` 同时处理：

- 每日血压序列聚合。
- 参数画像选择。
- 置信度元信息。
- data signature。
- 阈值重训。
- 模型加载、训练、持久化、缓存。
- forecast 生成。

这是高价值 Module，但现在内部 seam 不清晰，测试主要通过 patch 私有函数保护行为。

### Prediction freshness

架构文档说明当前不直接复用旧 prediction result，而是复用模型并重新生成结果。

代码中仍存在旧结果复用相关 Module 和测试：

- `backend/services/prediction_route_cache_service.py`
- `PredictUseCase._result_from_records`
- repository 的 `get_reusable_prediction`

这可能是历史遗留。需要决定是删除、隔离，还是重新记录为显式策略。

### 指南型健康建议

建议知识库有 `safety_boundary` 字段，但当前建议引擎主要匹配规则与组装文本，没有明显的安全约束执行层。

`PredictUseCase` 通过 `user_data["_guideline_signal"]` 传递建议上下文，这是隐式 Interface，降低 locality。

### 前端风险展示

风险展示逻辑分散在 prediction、history、admin、profile 多处。

风险 tone、confidence label、趋势文案存在重复实现。

`RiskBadge.tsx` 中出现“临床风险等级”，与项目领域语言冲突。建议改为“风险等级”或“高血压风险等级”。

### 训练数据导出

`UserProfile.diagnosis` 注释和导出逻辑使用“确诊/诊断”语义。CONTEXT.md 将该字段定义为诊断反馈，且不进入 LightGBM 核心预测输入。

训练数据导出可以继续保留，但后续若调整此处，需格外注意论文与领域文档表述。

## 优先级判断

1. 前端风险展示语言收敛：低风险、高收益，能马上减少领域表述漂移。
2. Prediction freshness 策略收敛：避免架构文档和代码行为继续分叉。
3. 指南型健康建议 seam 深化：直接服务安全边界与可测试性。
4. 预测记录读写映射深化：支持预测结果治理长期演进。
5. Prophet 生命周期深化：价值高，但改动面较大，宜后置。
6. 双模型预测引擎 run module 深化：应在依赖 seam 稳定后进行。

## Issue 化发现

- Issue tracker 配置为 GitHub 仓库 `honestman9527/HPS`，要求使用 `gh` CLI 创建 issue，并统一加 `needs-triage` 标签。
- 当前环境无法执行 `gh --version`：PowerShell 报告 `gh` 不是可识别命令。
- 当前环境没有 `GH_TOKEN` 或 `GITHUB_TOKEN`，因此不能改用认证 GitHub REST API 发布 issue。
- 未认证 GitHub REST API 查询 open issues 时触发 rate limit，无法可靠去重已有 issue。
- `rg` 在当前 Codex 桌面打包路径下启动失败并返回“拒绝访问”，本次改用 PowerShell 原生命令查询文件。
- 用户完成 GitHub CLI 登录后，当前 Codex 进程仍无法从 PATH 直接解析 `gh`，但 `gh.exe` 位于 `C:\Program Files\GitHub CLI\gh.exe`，可用完整路径执行。
- 仓库原本缺少 `needs-triage` 标签；发布 issue 前已创建该标签。
- 已发布 7 个架构深化 issues：#2 到 #8，均带 `needs-triage` 标签。

## 阶段 0 基线发现

- 后端 `cd backend; uv run pytest` 基线为绿色：86 passed。
- 前端 `cd frontend; pnpm run typecheck` 基线为绿色。
- 前端 `cd frontend; pnpm run lint` 基线失败，原因是 `frontend/src/features/prediction/components/PredictionInsightPanel.tsx` 中 `getConfidenceReasonDetails` import 未使用。
- 前端 `cd frontend; pnpm run test` 基线失败，原因是当前没有匹配 Vitest include 规则的测试文件。
- 基线与领域词保护清单已记录到 `docs/agents/architecture-deepening-baseline.md`。

## 阶段 1 前端风险展示探索

- #3 要求集中前端风险展示规则，覆盖风险等级、风险概率、置信度标签和趋势文案。
- `frontend/src/features/prediction/utils.ts` 和 `frontend/src/features/history/utils.ts` 均定义了 `confidenceLabels`，且趋势文案函数逻辑重复。
- `frontend/src/features/prediction/components/RiskBadge.tsx` 内部定义风险 tone，并出现“临床风险等级”文案，需改为符合领域词的“高血压风险等级”或“风险等级”。
- `frontend/src/features/history/utils.ts` 与历史组件自行拼接风险概率和风险 badge class，可迁移到共享展示模块。
- `frontend/src/features/admin/components/PredictionGovernanceOverview.tsx`、`PredictionAuditTable.tsx`、`PredictionAuditDetailCard.tsx` 直接显示 raw `risk_level` / `confidence_level`，导致置信度可能展示为 `high`/`medium`/`low`。
- `frontend/src/features/profile/components/HealthProfileSection.tsx` 中“已确诊/未确诊”可改为“诊断反馈”语义，避免和预测风险结果混淆。

## 阶段 1 前端风险展示结果

- 已新增 `frontend/src/features/shared/riskPresentation.ts`，集中处理：
  - 风险等级标签。
  - 风险 tone key/class。
  - 高血压风险概率格式化。
  - 置信度标签。
  - 风险等级与置信度筛选选项。
  - 血压趋势预测文案。
- 已新增 `frontend/src/features/shared/riskPresentation.test.ts`，覆盖风险等级、风险概率、置信度和趋势文案规则。
- 已新增 `frontend/src/test/setup.ts`，修复 Vitest 配置中缺失 setup 文件的问题。
- 前端 `pnpm run lint` 现在通过，阶段 0 记录的 `PredictionInsightPanel.tsx` 未使用 import 已修复。
- 前端 `pnpm run test` 现在通过，阶段 0 记录的“无测试文件”失败已修复。
- 静态扫描确认前端源码中不再出现“临床风险等级”“确诊概率”“医生诊断”“已确诊”“未确诊”。
- Playwright + mock API 已验证：
  - 预测页渲染“高血压风险等级”“高血压风险概率”“置信度：高”。
  - 历史页渲染“中风险 (48.6%)”与“整体有上升趋势”。
  - 管理员预测治理页将 raw `high`/`medium` 展示为中文风险/置信度标签。

## 2026-05-06 二期全盘架构扫描发现

### 扫描前置

- 用户要求对 **模型训练** 部分进行优化并附带扫描后端，已先完成一处低风险结构优化：`backend/train_models.py` 变薄，训练编排迁入 `backend/training/pipeline.py`。
- 后端全量测试基线：`cd backend; uv run pytest` 通过，116 passed。
- 当前二期扫描不修改数据库结构、迁移脚本或生产配置。

### 1. 双模型预测引擎装配

- `backend/routes/predictions.py` 直接装配多个 UseCase、Repository、Gateway 和 metadata window。
- 路由层 Interface 接近 Implementation，`build_*_use_case` 多为 Shallow Module。
- 删除这些工厂后，复杂度会散落在每个 route handler 中；更好的方向是集中成预测用例装配 Module。

### 2. 预测运行决策

- `backend/prediction/application/prediction_run.py` 目前同时处理预测运行键、风险融合、指南型健康建议信号、血压分级、保存 payload 和结果组装。
- `PredictionRun` 是有价值 Module，但内部规则可以继续深化到 domain Module，提升 Locality。

### 3. 预测记录规范化读写

- `backend/prediction/infrastructure/normalized_prediction_mapper.py` 仍集中处理写入、读取、旧格式指南型健康建议兼容和趋势摘要回放。
- 这不违背 ADR-0002，但内部 Interface 可以更深：外部保留 Facade，内部按预测明细类型分工。

### 4. 训练数据导出

- `backend/services/export_service.py` 同时承担最近血压均值、训练标签判定、训练样本行构造、CSV 输出和统计。
- **训练数据导出** 与 **模型训练** 共享 LightGBM 特征契约，但当前共享点主要在 `ml_schema.py`，样本构造规则仍分散。
- 需要特别保护 **诊断反馈** 语义：可以作为导出标签来源，但不进入用户侧 **双模型预测引擎** 的核心风险输入。

### 5. 个人档案字段契约

- 后端 `profile_service.py`、前端 `shared/normalizers.ts`、`ProfileForm.tsx` 都处理 **个人档案** 字段别名、空值、二元字段和数值解析。
- snake_case、camelCase 和历史字段别名会增加维护成本。
- `ProfileForm.tsx` 同时处理账户信息、健康档案、密码设置和邮箱验证码，适合拆出表单状态和字段契约 Module。

### 6. 账户信息凭证规则

- 后端 `auth_service.py` 与前端 `auth/validation.ts`、`ProfileForm.tsx` 都维护邮箱和密码规则。
- 密码类别计数存在细微差异：后端按“字母/数字/符号”三类，前端 auth validation 按“小写/大写/数字/符号”四类计算强度。
- 建议统一 **账户信息** 的预校验和最终校验语义。

### 7. 预测链路治理前端

- `usePredictionGovernanceData.ts` 同时负责 summary、table、detail、filters、chips 和 export。
- `adminApi.ts` 同时包含管理员用户、统计、预测治理规范化和下载逻辑。
- `auditDetailPresentation.ts` 已有较好的展示模型，但治理会话状态仍可深化为独立 Module。

### 8. 周健康报告语义

- 后端同时有 `/api/weekly-report` 和 `/api/profile/weekly-comparison` 两条接近的能力入口。
- `WeeklyComparisonService` 作为 Module 已较深，但领域命名存在 profile weekly comparison 与 **周健康报告** 的语义分叉风险。
- 二期可明确主 Module 和兼容入口，避免后续文案和论文描述漂移。

## 二期优先级判断

1. 双模型预测引擎装配：调用方最多，先减少 route 层认知负担。
2. 预测运行决策：承接阶段 7，让预测运行规则进一步集中。
3. 预测记录规范化读写：保护预测结果治理和历史回放。
4. 训练数据导出：保护模型训练样本与导出样本一致性。
5. 个人档案字段契约：减少前后端字段漂移。
6. 账户信息凭证规则：收敛注册、修改邮箱、重置密码和档案页规则。
7. 预测链路治理前端：提升管理员治理页面的测试与维护 Locality。
8. 周健康报告语义：收束双入口语义，降低论文和界面表述漂移。

## 阶段 7 双模型预测引擎装配探索

- `backend/routes/predictions.py` 当前直接导入并装配 `PredictUseCase`、历史/删除/批量删除/Prophet 历史/血压状态 use case、`PredictionRepository`、Prophet/Risk/Recommendation/RiskLevel gateway，以及 `PredictionRunMetadataService`。
- 路由层对 `model_reuse_window=timedelta(0)` 和 `result_metadata_window=metadata_service.metadata_window()` 有直接了解，这属于预测运行装配细节。
- `UserPredictionRecordActions` 已经把用户预测记录行为集中起来，阶段 7 可以复用它，不需要移动 route handler 的 HTTP 输入输出逻辑。
- 适合新增 `prediction.application.composition`，让默认工厂集中创建 repository、gateway、metadata window 和各个 use case；路由层保留可测试的薄 `build_*` 委托函数。

## 阶段 8 预测运行决策探索

- `backend/prediction/application/prediction_run.py` 当前仍包含多类稳定规则：预测运行 key 构造、指南型健康建议信号、血压分级、Prophet 模型复用模式判断、保存 payload 和 `PredictionResult` 组装。
- 运行 key 是纯规则，但当前在 `PredictionRun._build_prediction_run_key()` 中，并直接依赖 Prophet 聚合模式常量。
- 指南型健康建议信号构造包含趋势方向和血压分级，可下沉为 domain policy，避免建议信号规则藏在 use case 编排里。
- 结果和保存 payload 组装不应进入 route 或 repository，适合保留在 application 层独立 builder，由 `PredictionRun` 调用。

## 阶段 10 训练数据导出探索

- `backend/services/export_service.py` 当前同时处理导出窗口配置、最近 BP 均值、诊断反馈/规则标签判定、LightGBM 特征行构造、CSV 输出和统计。
- `backend/training/data.py` 读取训练 CSV 时已经依赖 `ml_schema.MODEL_FEATURE_COLUMNS`、`MODEL_TARGET_COLUMN`、`LABEL_SOURCE_COLUMN`，导出侧也使用 `TRAINING_EXPORT_COLUMNS` 和 `profile_to_model_feature_row`，列契约可继续由 `ml_schema.py` 统一。
- 适合新增 `backend/training/export_samples.py`，让管理员 CSV 导出和训练数据读取围绕同一 LightGBM 特征契约组织，而 `export_service.py` 保留服务层编排。
- `UserProfile.diagnosis` 在导出中只作为训练标签来源，不进入用户侧双模型预测引擎风险输入，本阶段不改数据库结构或字段语义。

## 阶段 11 个人档案字段契约探索

- 后端 `ProfilePayloadNormalizer` 负责 gender/smoking/cholesterol 旧别名、范围校验、二元字段校验和空值处理，但这些规则原先都藏在 `profile_service.py`。
- 前端 `ProfileForm.tsx` 同时承担账号、健康档案、密码/邮箱验证码状态；个人档案健康字段的字符串化、空值解析、吸烟联动和 BMI 计算适合独立到 `profileFormState.ts`。
- 前端 profile API 已通过 `normalizeProfileUser()` 处理 `currentSmoker`、`cigsPerDay`、`BPMeds`、`totChol` 等历史别名，本阶段保留该共享 normalizer。
- `diagnosis` 继续表达为“诊断反馈”，只进入档案反馈与训练数据导出语义，不作为本次预测输入。

## 阶段 12 账户信息凭证规则探索

- 后端 `auth_service.py` 原先直接维护邮箱格式和密码强度规则，前端 `auth/validation.ts` 也维护一套规则。
- 关键漂移点：后端按“字母/数字/符号”三类计算密码复杂度，前端原先按“小写/大写/数字/符号”四类计算强度。
- `ProfileForm.tsx` 还有局部 `validateEmail` 与 `validatePassword`，与登录/注册页的 `auth/validation.ts` 重复。
- 阶段 12 适合新增后端 `account_contract.py`，并让前端 `auth/validation.ts` 暴露 `getEmailValidationError` 与 `getPasswordValidationError`，统一注册、忘记密码、个人中心修改邮箱/密码的前端预校验语义。

## 阶段 13 预测链路治理前端探索

- `frontend/src/features/admin/hooks/usePredictionGovernanceData.ts` 原先同时承担筛选状态、请求参数、列表/详情选择、summary/detail 正规化、chip 展示和导出参数构造，测试难以只针对治理会话规则。
- `frontend/src/features/admin/api/adminApi.ts` 原先保留部分预测治理响应正规化逻辑，和 hook 内部展示模型有重复。
- 适合新增 `governanceSession.ts` 作为前端深 Module，集中纯规则：筛选、chips、query string、export params、summary/list/detail normalization、selected row decision。
- 管理员预测治理页的风险等级筛选实际 option value 是中文 `高风险/中风险/低风险`，不是英文 `high/medium/low`；浏览器脚本应选择中文值，避免误判为页面问题。

## 阶段 13 预测链路治理前端结果

- 已新增 `frontend/src/features/admin/governanceSession.ts`，集中治理会话纯规则。
- `adminApi.ts` 和 `usePredictionGovernanceData.ts` 已委托治理会话 Module，页面 hook 更接近“请求与事件编排”。
- 已新增 `frontend/src/features/admin/governanceSession.test.ts`，覆盖筛选 chip、详情规范化、默认详情选择和导出参数。
- 前端验证已通过：治理相关 Vitest、`pnpm run typecheck`、`pnpm run lint`、`pnpm run test`。
- Playwright mock API 已验证 `/admin/governance`：summary/list/detail 渲染、详情选择、异常筛选、高风险筛选和导出按钮请求参数均符合预期，控制台无 errors。

## 阶段 14 周健康报告语义探索

- 后端 `/api/weekly-report` 和 `/api/profile/weekly-comparison` 原本已经共用 `WeeklyComparisonService`，但主 Module 命名仍偏“profile weekly comparison”，容易让后续页面和论文描述分叉。
- `WeeklyComparisonCalculator.build_windows()` 实际是滚动窗口：当前窗口为 today-6 到 today，上一窗口为 today-13 到 today-7。它不是日历周，所以 UI 中“本周/上周/上一周”的表达不够精确。
- 前端 Weekly Report 页、首页 summary section 和 Profile 页趋势 tab 已共用 `WeeklyReportMetricGrid`，但周期标签、加载失败文案和 profile API 入口仍各自表达。
- 适合把“周健康报告：最近7天 vs 前7天”作为主语义，profile weekly-comparison 只保留为兼容入口，不再主导前端命名和展示文案。

## 阶段 14 周健康报告语义结果

- 新增 `backend/services/weekly_report_service.py` 作为主服务入口；`routes/weekly_report.py` 与 `routes/profile.py` 均委托 `WeeklyReportService`。
- `/api/profile/weekly-comparison` 继续存在，并通过 `build_weekly_comparison_service()` 兼容旧入口。
- 后端 summary `overall_trend_text` 统一改为“与前7天相比 / 最近7天 / 前7天”滚动窗口语义，未引入诊断或病情结论表达。
- 前端 `weekly-report/presentation.ts` 集中周报标题、周期标签、数据不足提示和周期展示 helper。
- Weekly Report 页和 Profile 页趋势 tab 统一显示“最近7天 / 前7天”和“较前7天”，profile 兼容 API 内部委托 weekly-report 主 API Module。
- 浏览器验证确认：主周报页请求 `/api/weekly-report`，Profile 趋势 tab 请求 `/api/profile/weekly-comparison`，两处展示模型一致，控制台无 errors。

## 2026-05-07 数据库设计与全量扫描优化发现

### 数据库表数量判断

- 当前 ORM 暴露 13 张业务表：`users`、`admin_users`、`user_profiles`、`bp_records`、`prediction_records`、`prophet_predictions`、`user_prophet_models` 和 6 张预测明细表。
- 预测明细表数量偏多但有明确 ADR 支撑：ADR-0002 选择规范化预测结果存储，以支持 **预测结果治理**、历史回放、训练数据导出和论文数据结构说明。
- 现阶段不建议为了减少表数量合并预测明细表；更应优先优化读取投影、索引和治理查询。

### `user_profiles` 职责拆分

- 当前 `user_profiles` 同时包含展示资料、**风险因素档案** 和 **诊断反馈**。
- 用户已明确：`user_profile` 可以拆分区分开，管理员不需要 profile。
- 用户进一步确认：`user_diagnosis_feedback` 独立表没必要，`user_profile` 不要拆太散。
- 推荐轻量拆分方向：
  - `user_profiles` 保留普通用户个人档案主信息：`nickname`、`avatar`、`diagnosis`、`updated_at`。
  - `user_risk_factor_profiles` 保存进入 **7天风险预测** 的 **用户个人风险因素**。
  - 不新增 `user_diagnosis_feedback`；`diagnosis` 留在 `user_profiles` 中继续表达 **诊断反馈**，只进入档案反馈和 **训练数据导出** 标签来源，不进入用户侧 **双模型预测引擎**。
  - `admin_users` 保持独立，仅表达管理员 **账户信息**，不关联任何健康档案表。
- 当前 `AdminUser.to_dict()` 为前端兼容返回了 `age`、`bmi`、`profile_complete` 等伪健康字段；后续拆分时应同步收敛管理员 DTO 和前端用户管理展示模型。

### 全量扫描热点

- `PredictionGovernanceReadModel.get_summary()` 当前通过 `governance_base_query().all()` 组装所有预测 payload 后再计算 **治理核心指标**，这是在线后台接口的主要全量扫描点。
- `PredictionGovernanceReadModel.list_predictions()` 在异常筛选时先 `query.all()` 再 Python 过滤和分页；应改为数据库先过滤再分页。
- `export_training_csv()` 和 `get_training_export_stats()` 当前从 `User.query.all()` 开始，并在样本构造中按用户查询血压记录，存在 N+1 风险。
- `HealthTaskService.get_today_summary()` 为计算今日状态、连续记录天数和最近偏高预警拉取用户全量血压记录。
- `BPDataRepository.get_bp_data_status()` 拉取用户全量血压记录后用 Python set 计算自然日数，可改为 SQL 聚合。
- Prophet 趋势预测读取用户全量血压记录有业务合理性，但仍需结合 `PROPHET_MAX_TRAIN_DAYS` 评估是否能只读取必要窗口，同时保持 `total_history_days` 和新增自然日统计准确。

### 索引缺口

- `bp_records`、`prediction_records`、`prophet_predictions`、`user_prophet_models` 当前多为单列 `user_id` 或状态索引。
- 高频查询普遍是 `user_id + recorded_at/created_at/trained_at` 排序或时间范围筛选，应优先设计复合索引。
- 候选索引包括：
  - `bp_records(user_id, recorded_at)`
  - `prediction_records(user_id, created_at)`
  - `prophet_predictions(user_id, created_at)`
  - `user_prophet_models(user_id, forecast_days, is_active, trained_at, id)`
  - `prediction_records(risk_level, created_at)`
  - `prediction_training_meta(confidence_level, prophet_prediction_id)`

## 三期优先级判断

1. 数据库查询基线与索引方案：先用 EXPLAIN 和真实 schema 确认优化方向，避免盲目加索引。
2. 预测结果治理查询下推：在线后台全量扫描最明显，收益最大。
3. 训练数据导出批量聚合：后台导出可接受稍慢，但 N+1 会随用户数增长明显恶化。
4. 用户侧血压记录状态查询优化：首页和预测页会频繁访问，应移除不必要的全量记录读取。
5. 普通用户个人档案拆分设计：领域边界更清晰，但涉及迁移和前后端兼容，宜在查询优化方案稳定后实施。
6. Prophet 每日血压序列读取边界：需要性能数据支持，必要时再升级为物化每日血压序列表或缓存方案。

## 阶段 15 数据库查询基线发现

- ORM 与 Alembic 已经将管理员拆到 `admin_users`，并删除普通用户 `users.role`；`database/hypertension.sql` 仍保留旧 `users.role` 且没有 `admin_users`，dump 落后于当前迁移。
- ORM 与 Alembic 已经固定 `prophet_predictions.forecast_days = 7` 和 `user_prophet_models.forecast_days = 7`，但 dump 中没有对应 check constraint。
- 当前高频查询普遍使用单列 `user_id` 索引后再排序或 Python 聚合；候选复合索引应围绕 `user_id + recorded_at/created_at/trained_at` 与治理筛选维度设计。
- 阶段 15 文档已创建：`docs/agents/database-query-index-baseline.md`。本阶段只产出索引方案和回滚策略，不新增迁移脚本。

## 阶段 17 预测结果治理查询下推结果

- `PredictionGovernanceReadModel` 新增数据库层 anomaly conditions，覆盖现有治理规则并保持 payload 层 `build_anomaly_flags()` 的语义。
- 治理 summary 改为查询聚合：风险分布、置信度分布、异常计数、低置信度比例、Prophet 模型复用次数都不再依赖全量 payload 组装。
- 列表接口在 `has_anomaly` 或 `anomaly_type` 存在时先应用 SQLAlchemy filter，再调用 `paginate()`，避免先拉全量治理记录到 Python。
- 导出接口仍需要组装导出行，但会先在数据库中过滤风险、置信度和异常条件。

## 阶段 18 训练数据导出批量聚合结果

- 训练数据导出从“全量 User 对象 + 每用户 BP 查询”改为批量样本投影。
- 最近 N 条血压均值通过 `row_number() over(partition by user_id order by recorded_at desc)` 子查询计算；标签所需的总血压记录数和偏高记录数通过按用户聚合一次性取得。
- `export_training_csv()` 和 `get_training_export_stats()` 现在复用 `load_training_export_batch()`，CSV 与统计不会因两套样本构造逻辑产生漂移。
- 旧的单用户样本函数仍保留给单元测试和局部规则复用，但服务入口不再使用 N+1 路径。
- 本地训练链路新增命令行导出入口 `backend/export_training_data.py`，默认写入 `datasets/training_data_export.csv`；它复用管理员网页导出的 `export_training_csv()`，不新增第二套样本规则。
- Q21 确认后，本地训练保持两步命令：`export_training_data.py` 显式导出，`train_models.py` 只训练，不自动触发导出。
- Q22 确认后，缺少 `datasets/training_data_export.csv` 不阻止训练；训练脚本只使用基础数据集，并输出导出样本不存在的提示。
- Q23 确认后，`datasets/training_data_export.csv` 作为本地数据库导出的可再生成样本文件加入 `.gitignore`；已跟踪的基础训练集不受影响。

## 阶段 19 用户侧血压记录状态查询优化结果

- `BPDataRepository.get_bp_data_status()` 已用聚合计数替代全量记录加载：总记录数走 `count()`，自然日数走 `count(distinct date(recorded_at))`。
- 今日健康任务拆出 `HealthTaskRepository`，只读取最新记录、去重记录日期和最近 3 个记录日的日均血压；服务层继续按原规则计算今日状态、连续记录天数和偏高预警。
- 周健康报告已经在二期阶段 14 限定为最近 14 天窗口读取，本阶段保持其窗口语义不变。

## 阶段 16 普通用户个人档案轻量拆分设计结果

- 设计文档已创建：`docs/agents/user-profile-lightweight-split-design.md`。
- 目标结构为 `user_profiles` + `user_risk_factor_profiles`，不新增 `user_diagnosis_feedback` 表。
- `diagnosis` 留在 `user_profiles`，继续表达 **诊断反馈**；用户侧预测输入只读取 `user_risk_factor_profiles`。
- 管理员 `admin_users` 继续只表达 **账户信息**，后续实施时应移除管理员 DTO 中伪造的健康档案字段。

## 阶段 20 Prophet 每日血压序列读取边界结果

- Prophet gateway 已从“加载原始 BP records 后 Python groupby”改为数据库每日聚合投影，Python 侧只接收每日血压序列。
- 新增 `build_daily_training_frame_from_aggregates()`，保持 Prophet training context 的 daily frame 契约不变。
- 当前不引入每日血压序列表；若日聚合查询在真实数据量下仍成为瓶颈，再单独形成 ADR、迁移与一致性方案。

## 阶段 21 三期设计实施发现

- 用户已确认实施三份设计文档，本阶段可以新增 Alembic migration，但仍需提供 downgrade 和数据回填路径。
- 现有迁移 head 为 `f4a9d2c6b8e1_split_admin_users_table.py`，新 migration 应基于该 head。
- `database/hypertension.sql` 当前仍保留旧 `users.role`，缺少 `admin_users`，也缺少固定 7 天 forecast check constraint；阶段 21 若更新 dump，应同时修正这些既有滞后点。
- PowerShell 搜索 SQL dump 时，双引号字符串内的 MySQL 反引号表名会被解释为转义序列；后续使用单引号或直接读文件片段。

## 阶段 21 三期设计实施结果

- `UserProfile` 现在只表达普通用户个人档案主信息：`nickname`、`avatar`、`diagnosis`、`updated_at`。
- 新增 `UserRiskFactorProfile` 表和 ORM，集中保存 `age`、`male`、`height`、`weight`、`current_smoker`、`cigs_per_day`、`bp_meds`、`diabetes`、`tot_chol`、`glucose`。
- `diagnosis` 继续作为 **诊断反馈** 留在 `user_profiles`，训练导出可用它作为标签来源；用户侧预测输入改为只读取 `user_risk_factor_profiles`。
- `User.to_dict()` 在过渡期继续输出扁平 Profile DTO，因此前端个人中心不需要同步拆 API 协议。
- `AdminUser.to_dict()` 不再伪造 `age`、`bmi`、`profile_complete`，管理员账号管理保持 **账户信息** 边界。
- 阶段 15 的复合索引已落入 migration 与 ORM metadata，后续 autogenerate 不应再把这些索引识别为外部漂移。
- `database/hypertension.sql` 已从旧 dump 快照更新到当前迁移后的结构，后续不应再把 `users.role` 当作真实 schema。

## 2026-05-07 grill-with-docs 血压预测阻断发现

- `/api/bp-data-status` 已通过 `BPDataRepository.get_bp_data_status()` 返回 `minimum_days`、`meets_minimum` 和 `meets_recommended`，可作为 `/api/predict` 的服务端预测前校验来源。
- Prophet gateway 的 `_load_daily_records()` 已有 3 个自然日的底层保护，但它抛出通用 `ValueError`；若不在预测运行入口转换为领域错误，路由会将不足血压数据映射为 500。
- 当前实现选择在 `PredictionRun.execute()` 进入 Prophet 之前校验 `meets_minimum`：低于最低自然日直接阻止预测；达到最低但低于推荐自然日保持可预测，让 Prophet 置信度和治理信号承担解释。
- Q13 确认后，最低自然日、推荐自然日和推荐记录数被收束到 `prediction.domain.bp_data_policy`，`bp-data-status`、`/api/predict`、Prophet 训练底层保护和预测结果治理共享同一最低自然日常量。
- Q14 确认后，预测前校验失败不创建失败预测尝试记录；`prediction_records` 和 `prophet_predictions` 只保存已经产出结果的预测。若未来要统计失败尝试，应设计独立审计日志。
- Q15 确认后，预测页风险因素档案阻断需要可行动提示。前端应把后端“请先完善风险因素档案”转换为阻断提示块，并跳转到 `/profile?tab=risk-factors`，而不是只显示普通错误。
- Q16 确认后，风险因素档案表单应显式区分最低完整性字段和可缺失字段：年龄、性别、身高、体重标记为必填；降压药、糖尿病、总胆固醇和血糖保持选填/可缺失。
- Q17 确认后，当前是否吸烟和日吸烟支数仍属于风险因素档案，但不属于预测前最低完整性阻断条件；非吸烟者日吸烟支数按 0 处理，缺失吸烟字段交由模型输入策略或缺失值处理承担。
- Q18 确认后，可缺失风险因素字段缺失不等同于风险因素档案未完成，不阻止 7 天风险预测；系统保留缺失值进入规范化预测输入快照，并在预测结果治理中以“模型输入字段缺失”呈现为数据质量信号。
- Q19 确认后，普通用户侧预测成功后不额外提示“完善更多风险因素”；可缺失字段为空只作为预测结果治理的数据质量信号，不在成功预测结果页制造混合信号。
- Q20 确认后，训练数据导出遇到可缺失风险因素为空时继续导出样本；最低完整性字段、血压聚合结果和标签来源满足规则即可，空值交给模型训练缺失值策略处理。

## 2026-05-08 四期剩余架构优化扫描

### 已完成但需登记的改动

- 用户选择了 **每日血压序列** Module 深化，并确认第一期只做读侧、不改 schema、不改前端接口。
- 当前工作区已新增 `backend/bp_series/`，集中 `DailyBPSeriesPoint`、日均血压读取和偏高/升高阈值规则。
- Prophet、今日健康任务、周健康报告已经迁移到共享 **每日血压序列** 读侧 Module；预测链路治理和趋势规则复用共享阈值。
- 后端全量测试通过：`uv run pytest`，176 passed。

### 领域与 ADR 约束

- `CONTEXT.md` 已定义 **每日血压序列**，不需要新增术语。
- ADR-0001 要求 Prophet 复用模型但重新生成预测结果；后续不得恢复旧预测结果缓存。
- ADR-0003 固定 **双模型预测引擎** 的 Prophet + LightGBM 串联。
- ADR-0004 固定普通用户 **7天风险预测**。
- ADR-0007 已取代 ADR-0002，后续预测记录相关优化必须沿着紧凑预测记录存储走，不能再把多表规范化明细当成目标结构。

### 剩余优化候选

1. **Prophet 每日血压序列训练窗口瘦身**
   - 当前 `_load_daily_records()` 通过 `DailyBPSeriesRepository().load_daily_series(user_id, ascending=True)` 读取用户全量每日序列，再由 `build_training_context()` 按 `PROPHET_MAX_TRAIN_DAYS` 裁剪。
   - `docs/agents/prophet-daily-series-read-boundary.md` 已记录后续可拆成 total metrics、训练窗口序列和新增自然日计数三类查询。
   - 这是下一步最高杠杆读侧优化，但执行前要确认 `data_signature`、`total_history_days`、`new_data_days_since_training` 的精确定义。

2. **今日健康任务读取与规则 Module 收敛**
   - `HealthTaskService` 已使用 **每日血压序列**，但仍保留 raw-record grouped 兼容路径：`_group_records_by_day()`、`_calculate_streak()`/`_calculate_alert()` 同时接受 dict/list。
   - Repository 当前读取截止今天的全量每日序列来计算记录天数和连续 streak；后续可以讨论是否保持精确全量回溯，或引入近期窗口。
   - 最新一次 **血压记录** 展示仍需要原始记录 projection，这和 **每日血压序列** 是两个不同读模型。

3. **周健康报告主 Module 命名收敛**
   - 后端已有 `weekly_report_service.py`，但它只是 `WeeklyComparisonService` 的薄继承/alias。
   - 前端仍有 `WeeklyComparisonPanel`、`WeeklyComparisonSummary` 和 profile weekly-comparison API alias。
   - 领域主语言应是 **周健康报告**；`/api/profile/weekly-comparison` 只应作为兼容入口存在。

4. **预测链路治理紧凑记录投影优化**
   - `PredictionGovernanceReadModel` 已适配紧凑 `PredictionRecord`，但 summary 中 `anomaly_flags` 统计仍读取所有 JSON flags。
   - 指定 `anomaly_type` 筛选时，当前会先按 `has_anomaly` 过滤，再组装 payload 并在 Python 中检查 flag。
   - 若使用 MySQL 8 JSON 查询能力可进一步下推，但需要保留测试 fallback，且不能违反 ADR-0007。

5. **紧凑预测记录后遗留兼容层清理**
   - `NormalizedPredictionMapper` 当前实际构造的是紧凑 `PredictionRecord` JSON payload，但名称仍沿用 normalized storage。
   - `backfill_normalized_storage.py` 是 no-op 兼容入口；是否保留取决于部署脚本兼容需求。
   - 清理方向应先讨论 alias 过渡，而不是直接删除或大范围改名。

6. **Prophet lifecycle 旧 Interface 收束**
   - `ProphetModelLifecycle` 仍保留 `_legacy_predict_from_model_state` 分支。
   - `predict_bp_trend_for_user(..., model_state=...)` 是否是正式业务 Interface 需要再搜索确认。
   - 如果只剩测试辅助，应把 lifecycle Interface 收窄，减少调用方需要理解的顺序约束。

## 阶段 24 Prophet 每日血压序列训练窗口瘦身结果

- **每日血压序列** 读侧 Interface 已拆成三类查询：
  - 总历史自然日数。
  - 最近 `PROPHET_MAX_TRAIN_DAYS` 个自然日的训练窗口序列。
  - `trained_until` 之后新增自然日数。
- Prophet 不再为了训练窗口裁剪读取完整每日序列；`build_training_context()` 继续接收 `total_days`，并基于训练窗口序列构造 `data_signature`。
- `new_data_days_since_training` 不再从裁剪后的 DataFrame 统计，而是通过 `DailyBPSeriesRepository.count_daily_series_days_after()` 查询，保留跨窗口的准确性。
- 本阶段没有引入物化 **每日血压序列** 表；物化表仍需真实慢查询证据和单独 ADR。

## 阶段 26 今日健康任务读取与规则 Module 收敛结果

- 用户确认 **今日健康任务** 的连续记录天数必须精确回溯，不做近期窗口近似；这是普通用户可感知的 streak 数字。
- `latest_record` 继续读取原始最新 **血压记录**，因为它表达最近一次录入的具体时间、血压和心率，不属于 **每日血压序列** 的日均语义。
- streak 和 alert 规则现在只接收 `daily_series`：
  - streak 使用完整 **每日血压序列** 日期集合。
  - 最近连续偏高预警使用最近 3 个 **每日血压序列** 点。
- 已删除 raw-record grouped dict 兼容路径，`HealthTaskService` 不再暴露 `_group_records_by_day()`。

## 阶段 25 周健康报告主 Module 命名收敛结果

- 用户确认后端主实现收束到 `WeeklyReportService`，`WeeklyComparison` 只保留兼容 alias。
- 用户确认前端主组件和类型收束为 `WeeklyReport` 命名，旧 `WeeklyComparison` 导入只保留极薄 alias。
- `/api/profile/weekly-comparison` 继续保留，不删除、不加 deprecation warning；它只是个人中心旧入口兼容路径。
- `backend/services/weekly_report_service.py` 现在承载真实 repository、calculator 和 service 实现。
- `backend/services/weekly_comparison_service.py` 只转导出兼容旧名称。
- 前端 Profile 页主组件改为 `WeeklyReportPanel`，旧 `WeeklyComparisonPanel` 只转导出主组件。
- 浏览器验证确认：
  - `/weekly-report` 请求 `/api/weekly-report` 并渲染 **周健康报告**。
  - `/profile?tab=trend` 请求 `/api/profile/weekly-comparison` 并渲染同一份 **周健康报告** 展示模型。

## 阶段 27 预测链路治理紧凑记录投影优化结果

- 用户确认在 ADR-0007 的紧凑预测记录存储下，不恢复多表规范化预测明细。
- 异常类型筛选走 MySQL `JSON_CONTAINS` 条件下推；本阶段不新增 schema、索引、派生表或 migration。
- summary 中 `anomaly_counts` 按已知异常码分别计数，不再全量读取 `anomaly_flags` JSON 列后在 Python 扫描。
- fake/in-memory 查询保留 Python fallback，用于测试和局部 fake repository；生产 MySQL 路径保持 SQL 过滤后分页/导出。

## 阶段 28 紧凑预测记录后遗留兼容层清理讨论

- 已确认 `NormalizedPredictionMapper` 暂时保留为兼容 Facade；主命名迁向 `CompactPredictionMapper`，旧导入只作为 alias 过渡。
- 已确认 `backfill_normalized_storage.py` 保留为 no-op 兼容入口，但文案和测试需要说明它只是 ADR-0007 后的历史命令兼容，不执行数据库写入。
- 已确认不一次性重命名或大范围移动文件；采用新增 compact 主 Module、保留 normalized alias 的方式。
- 已确认 compact 主命名覆盖整个 mapper 家族，而不是只覆盖顶层 mapper；rows 和 input/forecast/fusion/training/recommendation mapping 都建立 compact 主 Module，旧 normalized 文件降为 re-export alias。
- 代码扫描显示生产侧直接默认实例化 `NormalizedPredictionMapper` 的位置集中在：
  - `backend/prediction/infrastructure/prediction_record_repository.py`
  - `backend/prediction/infrastructure/prediction_payload_assembler.py`
  - `backend/prediction/infrastructure/repositories.py`
- mapper 家族当前有顶层 mapper、rows dataclass 和五个拆分 mapping 文件；这些实现实际已经服务于 ADR-0007 的紧凑 `PredictionRecord` JSON payload。
- 执行方向：新增 compact 主 Module，生产默认入口改用 `CompactPredictionMapper`；旧 normalized 导入继续可用并由测试保护。

## 阶段 28 紧凑预测记录后遗留兼容层清理结果

- compact 主 Module 已覆盖整个 mapper 家族：
  - `compact_prediction_mapper.py`
  - `compact_prediction_rows.py`
  - `compact_prediction_input_mapping.py`
  - `compact_prediction_forecast_mapping.py`
  - `compact_prediction_fusion_mapping.py`
  - `compact_prediction_training_mapping.py`
  - `compact_prediction_recommendation_mapping.py`
- 旧 `normalized_prediction_*` 文件保留为 re-export alias，不删除、不重命名、不大范围移动文件。
- 生产默认入口已切换到 `CompactPredictionMapper`，覆盖 `PredictionPayloadAssembler`、`PredictionRecordRepository` 和 `PredictionRepository`。
- `PredictionRecordRepository.save_prediction()` 优先使用 `build_compact_prediction()`，仅在外部注入旧 mapper 时 fallback 到 `build_normalized_prediction()`。
- `backfill_normalized_storage.py` 继续是兼容 no-op，文案已改为 ADR-0007 后历史命令兼容，并说明不写数据库。
- 红灯测试先确认缺少 `compact_prediction_*` Module 时 `test_compact_prediction_mapper.py` 收集失败；实现后目标测试、预测链路回归和后端全量均通过。

## 阶段 29 Prophet lifecycle 旧 Interface 收束讨论

- 业务路径：`PredictionRun` 调用注入的 `ProphetGateway.predict(user_id, forecast_days)`，`ProphetGateway` 再调用 `predict_bp_trend_for_user(user_id, forecast_days)`；业务侧没有传入 Prophet lifecycle `model_state`。
- `services.prediction_service.predict_bp_trend_for_user()` 作为兼容 wrapper，也只接收 `user_id` 和 `forecast_days`。
- `prophet_gateway.predict_bp_trend_for_user(..., model_state=...)` 与 `_predict_bp_trend_from_model_state()` 的真实用途集中在 Prophet gateway 测试，用于直接验证复用已有模型和禁用复用重训两条分支。
- `ProphetModelLifecycle` 的 `predict_from_model_state` 注入式 legacy 分支只被一个 lifecycle sequence 测试使用；生产 lifecycle 构建已使用 `load_or_train_models`、`predict_from_models`、`build_training_meta` 这组正式协作函数。
- 注意同名概念边界：`PredictionInputSnapshot.to_persistence_payload(model_state=...)` 仍是预测输入快照里的持久化元信息，不是旧 Prophet lifecycle 注入入口，不应在本阶段删除或改名。
- 用户确认从公开 Prophet 预测入口移除 `model_state` 参数；注入已构造 state 的测试改为直接调用 `ProphetModelLifecycle.predict_from_model_state()`。
- 本阶段保留 `PredictionInputSnapshot.to_persistence_payload(model_state=...)`，不改变预测输入快照持久化 payload。

## 阶段 29 Prophet lifecycle 旧 Interface 收束结果

- `ProphetModelLifecycle.__init__()` 已删除 `predict_from_model_state` 注入参数和 `_legacy_predict_from_model_state` 分支。
- `ProphetModelLifecycle.predict()` 仍负责隐藏 inspect-then-predict sequence；`predict_from_model_state()` 保留为 lifecycle 内部/测试 seam，并要求显式 state。
- `prophet_gateway.predict_bp_trend_for_user()` 的公开签名收窄为 `user_id, forecast_days`；公开 gateway 不再接收 `repository` 或 `model_state`。
- 直接注入 state 的复用/重训测试已改为直接构造 lifecycle，并调用 `predict_from_model_state()`，不再通过公开 gateway 入口。
- `PredictionInputSnapshot.to_persistence_payload(model_state=...)` 未改变，继续保存预测结果持久化元信息。
- 红灯测试先确认公开 gateway 签名仍含 `model_state` 时失败；实现后目标回归和后端全量均通过。

## 2026-05-08 最后一轮旧 Interface 清理扫描

### 扫描基线

- 当前 `git status --short` 无输出，工作区干净。
- ADR-0007 明确取代 ADR-0002；后续预测记录相关优化应沿着紧凑 `PredictionRecord` JSON payload 走，不应恢复多表 normalized storage。
- `docs/architecture/ARCHITECTURE.md` 仍在 infrastructure 示例中提到 `normalized_prediction_mapper`，需要在文档收尾阶段改为 compact 主命名。

### 旧 cache 语义残留

- `backend/services/prediction_route_cache_service.py` 只剩兼容 shell，生产代码没有调用。
- `backend/prediction/domain/cache_policy.py` 只把 `build_cache_snapshot()` re-export 到 `build_prediction_run_snapshot()`，生产代码没有调用。
- `PredictionRunMetadataService.build_prediction_run_key()` 仍保留旧 freshness/cache key 风格测试，但真实预测运行 key 已由 `prediction.domain.run_key_policy.build_prediction_run_key()` 负责。
- `PredictionResult` 和 `prediction_result_builder` 仍输出 `from_cache`、`cached_at`、`cache_expires_at`、`reuse_window_minutes` 和 `result_cache_hours`；前端没有使用这些字段。
- `frontend/src/types/prediction.ts` 的 `PredictionCacheMode` 仍包含 `hot_reuse`、`persistent_reuse` 等旧 result cache 模式。

### 紧凑预测记录写入残留

- 生产默认 mapper 已经是 `CompactPredictionMapper`。
- 非测试生产扫描中，`normalized_prediction_*` 只剩 alias 文件自身和 `PredictionRecordRepository.save_prediction()` 的 `build_normalized_prediction()` fallback。
- `PredictionInputSnapshot.to_persistence_payload()` 新预测仍写入 `_cache_snapshot` 和 `_prophet_cache_key`。
- `compact_prediction_input_mapping` 同时处理新 key 与旧 key；读取旧记录需要保留 fallback，但新写入不应继续写旧 key。

### 个人中心预测趋势 Interface 残留

- 前端个人中心趋势图调用 `getProphetPredictions(120)`，路径是 `/api/prophet-predictions`。
- 后端 `/api/prophet-predictions` 实际读取 `prediction_records`，并组装完整预测 payload 后再返回风险概率等字段；这与当前用途相比过重。
- `deleteProphetPrediction()` 和 `/api/prophet-predictions/<id>` 在前端无调用，删除预测记录已经由历史页 `/api/predictions/<id>` 承担。
- 推荐改为轻量“预测趋势投影” Interface，仅返回 `id`、`created_at`、`risk_probability` 和 `risk_level`。

### 认证与开发调试入口

- 前端登录只使用 `/api/auth/login/user` 和 `/api/auth/login/admin`。
- `/api/auth/login` 仍存在并由后端测试覆盖，属于模糊旧入口。
- `dev_tools_bp` 目前无条件注册；前端只在后端返回 `mock_service="local_email"` 后读取 `/api/dev/mock-emails/latest`，但关闭本地 mock email 时 route 仍然暴露。

### 周健康报告兼容入口

- 上一轮已确认 `/api/profile/weekly-comparison`、`WeeklyComparisonPanel`、`WeeklyComparisonSummary` 作为兼容入口保留。
- 若本轮目标是最终整洁，可以把 Profile 页也迁到 `/api/weekly-report`，并删除旧 weekly-comparison route、front alias 和服务 alias。
- 这会推翻上一轮保留兼容入口的决定，执行前应在 `task_plan.md` 阶段 5 记录最终选择。

## 2026-05-08 最后一轮清理阶段 0 保护网与接口证据

- 阶段 0 清单已落到 `docs/agents/final-interface-cleanup-phase0.md`。
- 当前基线全绿：
  - 后端 `uv run pytest`：190 passed。
  - 前端 `pnpm run typecheck`：通过。
  - 前端 `pnpm run lint`：通过。
  - 前端 `pnpm run test`：16 files / 34 tests passed。
- 后端 route 清单确认仍存在旧入口：
  - `/api/auth/login`
  - `/api/prophet-predictions`
  - `/api/prophet-predictions/<id>`
  - `/api/dev/mock-emails/latest`
  - `/api/profile/weekly-comparison`
- 前端请求清单确认：
  - 登录只调用 `/api/auth/login/user` 与 `/api/auth/login/admin`，不调用 `/api/auth/login`。
  - Profile 趋势 tab 仍通过 `/api/profile/weekly-comparison` 读取 **周健康报告**。
  - 个人中心预测趋势图仍通过 `/api/prophet-predictions?limit=...` 读取历史风险趋势。
  - `deleteProphetPrediction()` 存在于 API 文件，但组件未导入或调用。
  - 本地 mock email 调试请求只在后端响应 `mock_service="local_email"` 后触发。
- 待删 Interface 分类结果：
  - `PredictionRouteCacheService`：完全无外部调用。
  - `prediction.domain.cache_policy.build_cache_snapshot`：只剩 re-export，无生产调用方。
  - 旧 result cache 字段：后端仍暴露，前端未消费，测试仍断言。
  - `_cache_snapshot`、`_prophet_cache_key`：新写入仍存在，旧记录读取兼容仍需要。
  - `/api/prophet-predictions` GET：生产仍被个人中心趋势图调用，阶段 2 需要先替换。
  - `/api/prophet-predictions/<id>` DELETE：只剩 API 函数、后端 route 和测试，前端组件未用。
  - `normalized_prediction_*` 与 `build_normalized_prediction()`：生产 fallback 和测试兼容仍存在。
  - `/api/auth/login`：前端无调用，只剩后端 route 和测试。
  - `/api/dev/mock-emails/latest`：route 无条件注册，但前端有本地 mock 条件保护。
  - `/api/profile/weekly-comparison` 与 `WeeklyComparison*`：生产仍用的兼容入口，阶段 5 需再次确认是否删除。

## 2026-05-08 阶段 1 旧 cache Interface 删除结果

- 用户确认先删除 `PredictionRouteCacheService` 和 `prediction.domain.cache_policy.build_cache_snapshot` 两个无生产调用的旧 cache Interface。
- 已新增红灯测试 `test_old_prediction_cache_interfaces_are_removed()`，先确认旧模块仍可解析时失败。
- 已删除：
  - `backend/services/prediction_route_cache_service.py`
  - `backend/prediction/domain/cache_policy.py`
- 已收窄：
  - `backend/prediction/domain/__init__.py` 不再导入或导出 `build_cache_snapshot`。
  - `backend/prediction/domain/policies.py` 不再 lazy export `build_cache_snapshot`。
- 删除后 `rg` 扫描确认 `PredictionRouteCacheService`、`prediction_route_cache_service`、`build_cache_snapshot`、`cache_policy` 只剩测试中的“不可导入”断言。
- 本次不改变 `PredictionRunMetadataService`、`PredictionResult` 旧 result cache 字段或前端 `PredictionCacheMode`；它们留在阶段 1 后续小步处理。

## 2026-05-08 阶段 1 result cache 字段删除结果

- 用户确认继续删除旧 result cache 字段。
- 已通过红灯测试确认旧字段仍存在时失败：
  - `PredictionResult` 不应再有 `from_cache`、`cached_at`、`cache_expires_at`、`result_cache_hours`、`reuse_window_minutes`。
  - `PredictionUseCase` 不应再接收 `model_reuse_window` 或 `result_metadata_window`。
  - 历史 payload assembler 不应再输出 `from_cache`。
  - `PredictionRunMetadataService` 旧 cache-window/run-key Interface 不应再存在。
- 已删除后端输出字段：
  - `backend/prediction/schemas/results.py`
  - `backend/prediction/application/prediction_result_builder.py`
  - `backend/prediction/infrastructure/prediction_payload_assembler.py`
- 已收窄预测运行装配：
  - `PredictUseCase` 与 `PredictionRun` 不再接收 `model_reuse_window` / `result_metadata_window`。
  - `PredictionUseCaseFactory` 不再依赖 `PredictionRunMetadataService.metadata_window()`。
  - `PredictionRunMetadataService` class 已删除；`PredictionRecordRetentionService` 保留。
- 已收窄前端类型：
  - `frontend/src/types/prediction.ts` 的 `PredictionCacheMode` 删除 `hot_reuse`、`persistent_reuse`。
  - `cache_mode` 本身保留，继续表达 `fresh_train` 与 `model_reuse`。
- 生产源码扫描确认旧 result cache 字段、旧 cache policy、旧 route cache service、旧 cache window 注入只剩测试中的“不可存在”断言。
- `backend/config.py` 中 `PROPHET_RESULT_CACHE_HOURS` 未在本阶段修改，因为项目规则要求未经确认不修改生产配置；它后续可作为阶段 6 文档/配置清理问题单独确认。

## 2026-05-08 阶段 2 个人中心预测趋势投影优化结果

- 个人中心趋势图的后端读取入口已从 `/api/prophet-predictions` 迁到 `GET /api/profile/prediction-trend`，更贴近实际归属。
- 旧用户侧 Prophet 趋势删除能力已移除：前端 `deleteProphetPrediction()`、后端 `DELETE /api/prophet-predictions/<id>`、对应 use case 与 repository 方法全部删除。
- 趋势列表读取已不再组装完整预测 payload：
  - `PredictionRecordRepository.list_prediction_trend()` 直接查询 `PredictionRecord.id`、`created_at`、`risk_probability`、`risk_level`
  - repository 边界测试明确保护该路径不会调用 `PredictionPayloadAssembler`
- `PredictionUseCaseFactory` 与 `UserPredictionRecordActions` 已统一用 `ListPredictionTrendUseCase` / `list_prediction_trend()` 命名，旧 `list_prophet_predictions`、`delete_prophet_prediction` 用户侧术语已从生产源码中清空。
- 前端 `PredictionTrendChart` 已改为调用 `getPredictionTrend(120)`，类型命名收束到：
  - `RawProfilePredictionTrendRecord`
  - `ProfilePredictionTrendResponse`
- `README.md` 的接口列表已同步删除旧 `/api/prophet-predictions` 路径，改为记录 `/api/profile/prediction-trend`。

## 2026-05-08 阶段 3 compact 写入边界收紧结果

- `PredictionInputSnapshot.to_persistence_payload()` 新写入已不再包含：
  - `_cache_snapshot`
  - `_prophet_cache_key`
- `compact_prediction_input_mapping.build_input_snapshot()` 已改为只持久化实际传入的 metadata key，因此新 `PredictionRecord.input_snapshot` 不会再出现上述 legacy key 的 `None` 占位。
- `compact_prediction_input_mapping.assemble_input_data()` 现在区分“新记录”和“旧记录”：
  - 新记录：保留 `_model_state_snapshot` / `_prediction_run_key`，不再补 legacy key
  - 旧记录：若库里仍有 `_cache_snapshot` / `_prophet_cache_key`，读取时会映射回新 key，兼容旧记录回放
- `PredictionRecordRepository.save_prediction()` 已只接受 `build_compact_prediction()` 写入边界；legacy-only mapper 会在测试中被拒绝。
- `CompactPredictionWriteMapper` 已不再暴露 `build_normalized_prediction()` 写入 alias。
- 生产源码扫描结果在删除前已确认：
  - `normalized_prediction_*` 在非测试生产代码中无导入命中
  - `backfill_normalized_storage.py` 在非测试生产代码中无调用
- 用户确认激进删除后，已实际删除全部 `normalized_prediction_*` 文件和 `backfill_normalized_storage.py`。
- 兼容测试已改为“旧模块不可导入”断言，`backend/tests/prediction/test_normalized_prediction_mapper.py` 已一并删除。
- `docs/architecture/ARCHITECTURE.md` 的 infrastructure 主命名已同步改为 `compact_prediction_mapper`。

## 2026-05-08 阶段 4 认证与开发调试入口清理结果

- 前端登录链路确认无须迁移：
  - `frontend/src/hooks/useAuth.tsx` 只会请求 `/auth/login/user` 或 `/auth/login/admin`
  - 生产源码中无 `/auth/login` 前端调用
- 后端已删除模糊登录 route `POST /api/auth/login`，用户与管理员登录语义现在只通过角色明确的两个入口暴露。
- `AuthAccountService.login()` 仍保留 `required_role` 参数分支，继续服务用户/管理员两个明确入口；本阶段未改变认证领域逻辑。
- `dev_tools_bp` 已从“无条件注册”改为“仅本地 mock email 开启时注册”：
  - `ENABLE_LOCAL_MOCK_EMAIL_SERVICE=False` 时，`/api/dev/mock-emails/latest` 不出现在 `url_map`
  - `ENABLE_LOCAL_MOCK_EMAIL_SERVICE=True` 时，路由保持可用
- 前端 `RegisterForm`、`LoginForm`、`ProfileForm` 对 `getLatestMockEmail()` 的调用原本就被 `mock_service === "local_email"` 保护，因此不需要额外前端降级逻辑。
- `README.md` 的 API 概览已同步删除旧 `/api/auth/login`，并把 `/api/dev/mock-emails/latest` 标记为仅本地 mock email 开启时注册。

## 2026-05-08 阶段 5 周健康报告兼容入口最终收尾结果

- 用户确认执行阶段 5 推荐方案，删除旧 `weekly-comparison` 兼容入口。
- 后端已移除：
  - `build_weekly_comparison_service()`
  - `GET /api/profile/weekly-comparison`
  - `services.weekly_comparison_service` 模块
- 前端已统一到 canonical weekly report API：
  - `frontend/src/features/weekly-report/api/weeklyReportApi.ts` 仅保留 `getWeeklyReport()`
  - `ProfilePage` 改为直接调用 `getWeeklyReport()`
- 前端 comparison alias 已全部删除：
  - `profileComparisonApi.ts`
  - `WeeklyComparisonPanel.tsx`
  - `features/profile/index.ts` 中对应 re-export
  - `WeeklyComparisonSummary` 类型 alias
- 服务测试已切回 canonical 命名：
  - 删除 `backend/tests/services/test_weekly_comparison_service.py`
  - 新增 `backend/tests/services/test_weekly_report_service.py`
- 扫描结果显示生产源码中 `weekly-comparison` / `WeeklyComparison*` / `getProfileWeeklyReport` 只剩阶段 0 历史清单文档引用，不再出现在生产实现路径中。

## 2026-05-08 阶段 6 文档与配置残留扫描

- 旧 result cache 字段、旧 Prophet prediction history、旧 weekly-comparison 和旧 normalized storage 的生产实现残留已清理；当前命中主要来自历史记录、阶段计划和保护测试。
- `backend/config.py` 仍定义 `PROPHET_RESULT_CACHE_HOURS`，`README.md` 仍列出该环境变量；扫描未发现当前代码路径读取该值。
- 因为 `backend/config.py` 属于生产配置范围，删除该配置项需要用户明确确认；若不删除，应在阶段 6 记录为“未使用但暂保留的兼容配置”。

## 2026-05-08 阶段 6 配置清理确认结果

- 用户确认删除未使用的 `PROPHET_RESULT_CACHE_HOURS`。
- 已从 `backend/config.py` 删除该配置项。
- 已从 `README.md` 的环境变量示例删除该配置项。
- `CONTEXT.md` 已将 `weekly-comparison` 表述为历史兼容叫法，而不是当前接口或领域语言。

## 2026-05-08 阶段 7 论文准备最终体检发现

- 当前生产源码中的旧 Interface 关键词已经基本清空；命中主要来自保护测试和 `CONTEXT.md` 的历史叫法说明。
- 被 `.gitignore` 忽略的 `backend/static` 本地构建产物曾仍引用 `/api/prophet-predictions` 和 `/api/profile/weekly-comparison`；若使用 `start.bat --skip-build`，会有服务到旧前端的演示风险。
- 已通过 `pnpm build` 刷新 `backend/static`，刷新后静态产物不再命中旧 Interface 关键词。
- 项目源码范围曾存在 24 个 `__pycache__` 目录，其中包含已删除旧模块的编译缓存；已清理，且未触碰 `.venv`。
- 后端迁移脚本中的 `prophet_predictions`、旧预测明细表和 compact-storage 回填逻辑属于历史迁移链，不建议为论文准备期清理迁移历史。
- 前端预测趋势图错误提示已从“预测历史接口状态”改为“预测趋势接口状态”，与当前预测趋势投影 Interface 保持一致。
- 最适合论文准备期新增的不是业务功能，而是“演示准备检查”脚本：检查测试、构建、旧 Interface 关键词和静态产物新鲜度，降低答辩演示风险。

## 2026-05-09 阶段 8 论文正式写作计划发现

- 论文正式写作计划已从 `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-论文写作准备稿.md` 落到根目录 `task_plan.md`，后续可直接按阶段恢复工作。
- 第8阶段应先做参考文献池检索与核验，再生成模型设计图、E-R 图和页面截图，最后进入正文写作与 Word 成稿。
- 正文写作顺序建议为：第3章、第4章、第5章先写，再回写第1章、第2章、第6章和摘要。这样能先锁住数据、模型链路和实验结果，减少后面返工。
- 第4章图表顺序已明确：先放 Prophet/LightGBM/双模型链路等模型设计图，再放核心 E-R 图和页面截图；页面截图不能替代模型设计图。
- 参考文献必须重新检索和核验，优先覆盖中国高血压防治指南（2024年修订版）、高血压风险预测、Prophet/时间序列预测、LightGBM/机器学习分类和健康管理系统。
- 正文继续遵守“代码尽量不要放”的用户偏好：真实源码不大量进入正文，必要时只用短伪代码或核心逻辑摘要。

## 2026-05-09 阶段 8.1 参考文献池检索与核验结果

- 已建立 16 篇参考文献池，文献覆盖：
  - 高血压指南与防治：R01-R03。
  - 高血压流行病学背景：R04。
  - 高血压风险预测与机器学习：R05-R12。
  - 健康管理系统/数字健康：R13-R14。
  - Prophet 与时间序列预测：R15。
  - LightGBM 与树模型分类：R16。
- 产物已落到：
  - `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-参考文献核验清单.json`
  - `lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-参考文献池.md`
- Crossref、OpenAlex、PubMed、Unpaywall 四路核验覆盖了大多数 DOI 文献。
- 中国高血压防治指南（2024年修订版）未被 Crossref/OpenAlex/Unpaywall 收录，但可通过《中华高血压杂志（中英文）》官网和公开 PDF 核验，适合进入正文。
- LightGBM 原始论文没有稳定 Crossref DOI；以 DBLP、NeurIPS Proceedings 页面和 NeurIPS PDF 作为核验来源。
- Prophet 原始论文 `Forecasting at Scale` 可通过 Crossref/OpenAlex 核验，但 Unpaywall 显示 closed，正文引用元数据即可。
- Semantic Scholar batch API 本次触发 429，未继续重试；引用量参考改用 OpenAlex `cited_by_count`。

## 2026-05-09 阶段 8.2 图表与截图资产准备结果

- 第4章图表资产已补齐，当前采用 5 张模型/结构类图和 6 张页面截图：
  - Prophet 血压趋势预测流程图。
  - LightGBM 风险分类输入输出图。
  - Prophet-LightGBM 双模型预测链路图。
  - 预测结果治理链路图。
  - 核心数据结构 E-R 图。
  - 风险因素档案、血压记录、7天风险预测、预测结果、预测历史、预测结果治理页面截图。
- 页面截图来自本地系统真实运行环境，普通用户使用 `demo_showcase_high`，管理员使用 `demo_admin_showcase`。
- 预测结果截图由真实 `/api/predict` 调用生成，风险结果为高风险样例，展示了风险概率、未来 7 天血压趋势图和指南型健康建议。
- 管理员环境账号 `dream` 当前密码与 `.env` 中 `ADMIN_PASSWORD=change-me` 不一致；为避免修改原管理员，已新增 `demo_admin_showcase` 演示管理员用于截图。
- Playwright 抓图后用户端与管理员端控制台均无 error；截图尺寸均为 1440px 宽，适合后续插入 Word 后再压缩排版。
- 已生成图片清单：`lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现-图片清单.md`。

## 2026-05-09 论文资料目录收拢

- 用户要求把论文相关资料放入 `lunwen-doc` 文件夹下。
- 当前目录边界调整为：论文原始资料、论文写作材料、参考文献、图片清单、图表截图和后续成稿放入 `lunwen-doc/`。
- 样式分析结果、样文页面截图、任务书/开题报告文本抽取结果、临时脚本和临时日志属于中间产物，统一放入 `output/lunwen-intermediate/`。
- `lunwen-doc` 根目录继续保留学校规范、样文、任务书、开题报告等原始输入资料。
- 后续主论文 `.md`、主论文 `.docx`、附件 `.docx` 和 image-map 文件也应放在 `lunwen-doc/论文写作材料/`。

## 2026-05-09 参考文献池中文优先比例调整结果

- 用户要求参考文献“尽量找中文的，把控好比例 8:2”。
- 当前有效参考文献池已调整为 15 篇，其中中文 12 篇、英文 3 篇，中文占 80.0%，英文占 20.0%。
- 中文文献承担论文主体支撑：指南依据、健康管理规范、流行病学背景、高血压风险预测研究、中文机器学习健康风险预测、可解释机器学习和 Prophet 中文应用。
- 英文文献只保留不可替代或高相关条目：Prophet 原始论文、LightGBM 原始论文，以及高血压可视化风险预测系统论文。
- 参考文献核验清单 JSON 已通过语法校验；后续正式成稿前需再次检查 R07、R08 是否已补齐正式卷期页码。
- R11 只能作为 Prophet 中文应用背景补充，不能替代 Prophet 原始模型论文。

## 2026-05-09 阶段 8.3 主论文 Markdown 初稿结果

- 已创建主论文 Markdown 初稿：`lunwen-doc/论文写作材料/基于Prophet与LightGBM的高血压风险预测系统设计与实现.md`。
- 初稿采用已冻结的六章结构，并补齐中英文摘要、关键词、致谢和参考文献。
- 正文主线保持为 Prophet 血压趋势预测、LightGBM 风险分类、双模型预测链路、模型训练结果和系统落地。
- 第4章已按“模型设计图先于页面截图”的顺序插入 5 张模型/结构类图和 6 张页面截图。
- 第5章已使用真实模型报告指标：Tuned Accuracy 0.8743、AUC 0.9400、Precision 0.8504、Recall 0.8245、F1 0.8373、PR-AUC 0.9128、Brier Score 0.0915。
- 初稿仍需二轮润色：压缩重复边界说明、按学校模板转换 Word、检查图题表题样式和 R07/R08 正式卷期页码。

