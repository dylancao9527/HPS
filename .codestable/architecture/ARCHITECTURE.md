---
doc_type: architecture
status: current
last_reviewed: "2026-05-10"
area: system
tags: [architecture, prediction, frontend, backend, modeling]
---

# 系统架构文档

## 0. CodeStable 文档入口

- 当前能力愿景：[提供高血压 7 天风险预测能力](../requirements/hypertension-risk-prediction-system.md)
- 领域语言与论文口径：[domain-language.md](domain-language.md)
- 前后端与模型技术栈决策位于 `.codestable/compound/2026-05-10-decision-*.md`
- 旧 `AGENTS.md` / `CONTEXT.md` 已整理到 CodeStable 入口中，原文件已删除。

## 1. 架构目标

本系统的设计目标不是做“临床诊断系统”，而是构建一个面向普通用户的高血压风险预测系统。论文题目固定为《基于Prophet与LightGBM的高血压风险预测系统设计与实现》。系统需要同时满足以下要求：

- 支持日常血压记录、个人档案维护与风险预测
- 能输出普通用户易理解的指南型健康建议
- 兼顾模型可复用、可追踪、可治理
- 支持论文实验所需的结构化分析、结果回溯与工程说明

论文叙述主线应围绕 Prophet 与 LightGBM 的双模型预测链路展开。用户注册、权限、数据库、前端页面和后台管理是预测链路落地所需的工程支撑，不应喧宾夺主写成传统 CRUD 管理系统；模型章节可以参考模型类样文的结构节奏，但必须基于本项目真实的 Prophet 趋势预测、LightGBM 风险分类和训练评估结果，不夸大为深度学习训练系统。

因此，系统采用“前后端分离 + 双模型预测 + 紧凑预测记录存储 + 模型持久化”的整体架构。

## 2. 总体架构

```text
┌──────────────────────────────────────────────────────────────┐
│                         前端 React 应用                      │
│  React 19 + Vite + TypeScript + React Router + Recharts     │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTP / JSON
┌──────────────────────────────▼───────────────────────────────┐
│                         Flask 后端 API                       │
│                                                              │
│  routes/                                                     │
│  ├─ auth                                                     │
│  ├─ profile                                                  │
│  ├─ bp_records                                               │
│  ├─ health_tasks                                             │
│  ├─ predictions                                              │
│  └─ admin                                                    │
│                                                              │
│  prediction/                                                 │
│  ├─ application                                              │
│  ├─ domain                                                   │
│  └─ infrastructure                                           │
└──────────────────────────────┬───────────────────────────────┘
                               │ SQLAlchemy
┌──────────────────────────────▼───────────────────────────────┐
│                           MySQL 8                            │
│ users / admin_users / user_profiles                          │
│ user_risk_factor_profiles / bp_records                       │
│ prediction_records / user_prophet_models                     │
│ compact JSON prediction payloads                             │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                      本地运行时文件存储                       │
│ backend/runtime/mock_emails.json                             │
│ backend/runtime/prophet_models/<storage_key>/                │
│   ├─ sys_model.pkl                                           │
│   └─ dia_model.pkl                                           │
└──────────────────────────────────────────────────────────────┘
```

## 3. 技术选型

### 前端

- `React 19`
- `Vite 8`
- `TypeScript`
- `React Router DOM`
- `Recharts`

前端负责用户交互、表单输入、图表展示、历史查看和管理员界面。

### 后端

- `Flask`
- `Flask-SQLAlchemy`
- `Flask-Migrate`
- `JWT`

后端负责认证、数据存储、预测编排、建议生成和治理接口。

### 数据与模型

- `MySQL 8`：业务数据持久化
- `Prophet`：血压趋势预测
- `LightGBM`：风险分类
- `Optuna + LightGBMTunerCV`：LightGBM 调参

## 4. 后端分层设计

预测模块采用分层设计，核心目录为 `backend/prediction/`。

### 4.1 application 层

负责组织业务用例，典型类包括：

- `PredictUseCase`
- `GetPredictionHistoryUseCase`
- `DeletePredictionUseCase`
- `GetBPDataStatusUseCase`

这一层的职责是“编排流程”，不直接关心底层数据库细节和具体模型文件读写。

### 4.2 domain 层

负责沉淀稳定的业务规则与策略，例如：

- 风险融合策略
- 趋势方向判断
- 置信度规则
- 血压数据状态判断

这一层强调“规则可复用、可测试、与基础设施解耦”。

### 4.3 infrastructure 层

负责与外部资源交互，包括：

- `PredictionRepository`
- `prophet_gateway`
- `risk_model_gateway`
- `prophet_model_store`
- `compact_prediction_mapper`

这一层处理数据库读写、Prophet 模型序列化、文件存储、缓存和数据映射。

## 5. 核心业务模块

### 5.1 用户认证与账户

由 `auth` 路由模块实现，支持：

- 注册
- 登录
- 修改密码
- 找回密码
- 修改邮箱
- 身份校验

账户信息的邮箱格式、密码长度和密码复杂度由 `account_contract` 集中约束，认证流程、管理员密码重置和前端预校验复用同一套规则，避免不同入口出现凭证规则漂移。

### 5.2 个人档案

由 `profile` 路由负责，维护普通用户的个人档案。领域上个人档案包含两类信息：

- 风险因素档案：进入 7 天风险预测的个人健康与生活方式风险因素
- 诊断反馈：用户自报或反馈性健康状态信息，可作为训练数据导出标签来源，但不进入用户侧预测输入

当前物理存储采用轻量拆分：

- `user_profiles` 保存展示资料与诊断反馈
- `user_risk_factor_profiles` 保存风险因素档案

风险因素档案维护的主要特征包括：

- 年龄
- 性别
- BMI
- 是否吸烟及日吸烟支数
- 是否服用降压药
- 是否糖尿病
- 总胆固醇
- 血糖

### 5.3 血压记录

由 `bp_records` 路由负责，支持：

- 新增血压记录
- 查询血压记录
- 删除单条记录
- 批量删除记录

血压记录是 Prophet 模型训练与趋势分析的直接输入。

### 5.4 今日健康任务

由 `health_tasks` 模块负责，为首页和预测页提供“今天要做什么”的轻量提醒，例如：

- 今天是否已记录血压
- 当前连续记录天数
- 建议动作提示

### 5.5 管理员模块

由 `admin` 路由负责，支持：

- 用户管理
- 系统统计
- 训练数据导出
- 预测结果治理信息查看与导出

## 6. 预测链路设计

## 6.1 目标

系统的预测不是单一返回一个概率值，而是输出完整的一次预测结果，包括：

- 当前用户档案输入
- 最近血压状态
- Prophet 趋势预测
- LightGBM 输出的高血压发病风险概率
- 趋势融合后的最终风险
- 指南型健康建议
- 训练与置信度元信息

## 6.2 预测主流程

`POST /api/predict` 最终会进入 `PredictUseCase.execute()`，主流程如下：

```text
1. 校验并读取风险因素档案和最近血压记录；风险因素档案缺失或未完成时阻止预测
2. 校验血压记录自然日数量；低于最低自然日要求时阻止预测
3. 检查当前 Prophet 模型状态
4. 判断新增血压自然日数是否达到重训阈值
5. 若未达到阈值，则复用已有 Prophet 模型重新计算趋势
6. 若达到阈值，则基于最新数据重训 Prophet 模型
7. 使用 LightGBM 基于预测期血压特征和用户个人风险因素计算 raw_probability
8. 使用趋势融合策略得到 fused_probability
9. 生成指南型健康建议
10. 紧凑持久化 prediction_records 预测记录聚合
11. 返回预测结果
```

第 1、2 步属于预测前校验。校验失败时不会创建 `prediction_records`，也不会进入普通用户预测历史或管理员预测结果治理。若后续需要统计失败预测尝试，应新增独立审计日志，不复用预测记录表。

## 6.3 为什么不再复用旧预测结果

当前版本已经取消“直接复用旧 prediction result”的策略，原因是：

- 用户最近一次血压输入变化后，即使 Prophet 模型仍可复用，风险融合结果也可能变化
- 直接复用旧 prediction result 容易让用户误以为系统没有重新计算
- 对论文实验来说，“每次预测都有独立结果记录”更利于比较、追踪和展示

因此系统现在采用：

- 复用模型
- 重新生成结果

而不是：

- 复用旧结果记录

## 7. Prophet 模型设计

## 7.1 训练数据组织

系统首先将用户血压记录按“自然日”聚合，得到每日均值序列：

- `systolic`
- `diastolic`
- `measurements`

再根据数据量、波动情况和预测周期构造 Prophet 训练上下文。

## 7.2 参数画像

当前系统会根据历史数据情况选择参数画像：

- `short`
- `standard`
- `volatile`

其目的是在数据较短、波动较大或常规情况下采用更合适的 Prophet 参数。

## 7.3 置信度元信息

训练上下文会生成：

- `confidence_level`
- `confidence_reasons`
- `avg_measurements_per_day`
- `recent_sys_range_mean`
- `recent_dia_range_mean`

这些信息既用于前端解释，也用于历史治理和论文展示。

## 7.4 模型重训策略

当前新增的关键策略是：

- 配置项：`PROPHET_RETRAIN_AFTER_DAYS`
- 含义：当新增血压“自然日”数达到该阈值时，重新训练 Prophet 模型

例如：

- 阈值为 `3`
- 上次模型训练截止到 `2026-04-20`
- 用户新增了 `2026-04-21`、`2026-04-22`

此时新增自然日为 `2`，未达到阈值，系统复用已有模型重新预测。

如果又新增了 `2026-04-23`，则新增自然日为 `3`，触发重训。

## 7.5 模型持久化

Prophet 模型采用三层持久化结构：

### 1. 元数据层：`user_prophet_models`

保存：

- 用户 ID
- `forecast_days`
- 模型版本
- 数据签名
- 训练截止日期
- 参数画像
- 季节性配置
- 文件存储键
- 是否为当前活跃模型

### 2. 文件资产层：`backend/runtime/prophet_models/`

按如下结构保存：

```text
user_<user_id>/fd_<forecast_days>/<model_version>/<data_signature>/
```

其中包含：

- `sys_model.pkl`
- `dia_model.pkl`

### 3. 内存缓存层：`InMemoryProphetModelCache`

用于保存最近使用的 Prophet 模型，减少反序列化和文件 IO。

## 8. LightGBM 风险分类设计

当前风险分类使用 12 个核心特征：

```python
[
    "male",
    "age",
    "currentSmoker",
    "cigsPerDay",
    "BPMeds",
    "diabetes",
    "totChol",
    "sysBP",
    "diaBP",
    "BMI",
    "heartRate",
    "glucose",
]
```

其中 `sysBP` 和 `diaBP` 来自 Prophet 未来7天预测收缩压和舒张压均值，其他字段来自用户个人风险因素。模型输出 `raw_probability`，随后再进入趋势融合流程。

### 8.1 趋势融合

风险融合策略会综合考虑：

- 未来血压趋势
- 高血压天数
- 趋势斜率
- 波动程度
- 是否正在服用降压药

最后得到：

- `raw_probability`
- `fused_probability`
- `adjustment`
- `trend_adjustment`
- `medication_adjustment`

## 9. 建议生成设计

指南型健康建议模块以”知识库映射 + 模板化自然语言输出”为主，不做医学诊断。知识库基于《中国高血压防治指南（2024年修订版）》，规则存储在 `backend/data/guideline_knowledge_base.json`。

### 9.1 信号维度

预测完成后，`PredictUseCase._build_guideline_signal()` 组装以下信号传入建议引擎（`backend/prediction/application/predict_use_case.py`）：

- `risk_level`：融合风险等级（low / medium / high）
- `bp_grade`：基于 Prophet 预测均值的血压分级（normal / normal_high / grade1 / grade2 / grade3），按《指南》分级标准计算
- `trend_direction`：趋势方向（upward / stable / volatile）
- `high_bp_days`：预测期内高血压天数
- `record_days`：可用记录天数
- `confidence_level`：置信度等级

### 9.2 规则匹配与分组输出

`RecommendationEngine.build()` 按 topic 分组匹配，每组取优先级最高的一条，返回 list[dict]（`backend/services/recommendation_engine.py`）：

```python
[
    {
        “topic”: “follow_up”,        # urgent / follow_up / lifestyle / prevention / maintenance
        “summary”: “...”,
        “reason”: “...”,
        “actions”: [“...”, “...”],
        “source_label”: “建议依据：中国高血压防治指南（2024年修订版）...”
    },
    ...
]
```

`confidence_notice` 类规则不单独成卡片，附加到第一张卡片的 `reason` 末尾。

### 9.3 知识库结构

规则存储在 `backend/data/guideline_knowledge_base.json`，每条规则含：

- `trigger_conditions`：匹配条件（支持精确值、列表、`_min`/`_max` 后缀范围）
- `topic`：分类维度
- `priority`：high / medium / low
- `summary_template` / `explanation_template` / `action_templates`：输出模板
- `safety_boundary`：安全边界标注（`avoid_diagnosis: true`）

### 9.4 前端展示

预测结果页通过 `PredictionRecommendationPanel` → `RecommendationList` 展示多张卡片，每张对应一个 topic，展示 summary + reason + actions（`frontend/src/features/prediction/components/RecommendationList.tsx`）。

## 10. 数据持久化设计

## 10.1 核心表

### `users`

保存账户主体信息：

- 用户名
- 邮箱
- 密码摘要

### `user_profiles`

保存普通用户个人档案主信息：

- 昵称
- 头像
- 诊断反馈

诊断反馈不进入用户侧预测输入。

### `user_risk_factor_profiles`

保存进入 7 天风险预测和训练数据导出的风险因素档案：

- 年龄
- 性别
- 身高和体重
- 是否吸烟及日吸烟支数
- 是否服用降压药
- 是否糖尿病
- 总胆固醇
- 血糖

其中年龄、性别、身高和体重构成预测前的最低完整性要求；当前是否吸烟、日吸烟支数、是否服用降压药、是否糖尿病、总胆固醇和血糖可以缺失，由模型输入策略或缺失值处理承担。非吸烟者的日吸烟支数按 0 处理。可缺失字段为空时不阻止预测，紧凑预测记录中的输入快照保留空值，并在预测结果治理中作为模型输入字段缺失的数据质量信号呈现。

训练数据导出同样只要求最低完整性字段、血压聚合结果和标签来源满足导出规则；当前是否吸烟、日吸烟支数、是否服用降压药、是否糖尿病、总胆固醇和血糖为空时保留空值进入 CSV，由模型训练缺失值策略处理。

训练数据导出有两个入口：管理员网页导出继续用于后台管理，本地训练链路优先使用命令行导出。两个入口都复用同一份 `export_training_csv()` 服务规则，避免网页导出和本地训练样本口径分叉。

### `admin_users`

保存管理员账户信息。管理员不关联个人档案、风险因素档案、血压记录或预测记录。

### `bp_records`

保存日常血压记录：

- 收缩压
- 舒张压
- 心率
- 记录时间

7 天风险预测启动前会按自然日检查血压记录最低要求。低于最低要求时服务端拒绝生成预测；达到最低要求但未达到推荐自然日数量时，预测可以继续，并通过 Prophet 预测说明与预测结果治理体现低置信度或数据不足信号。

血压数据充分性策略集中在 `prediction.domain.bp_data_policy`。`/api/bp-data-status`、`/api/predict`、Prophet 训练边界和预测结果治理都应引用同一最低自然日规则，避免状态提示与实际预测阻断条件漂移。

### `prediction_records`

保存每次预测的主结果：

- 风险概率
- 风险等级
- 训练数据天数、置信度等级、模型运行模式和异常标记
- 输入快照、血压趋势预测、融合元信息、Prophet 训练说明和指南型健康建议 JSON 载荷
- 创建时间

### `user_prophet_models`

保存 Prophet 模型元数据和治理字段。

## 10.2 紧凑预测记录载荷

当前预测历史不再拆分为多张 Prophet/预测明细表，而是以 `prediction_records` 作为一次预测的聚合存储：

- 历史回放
- 治理审查
- 再训练导出
- 毕业论文中的数据结构说明

保留为列的字段包括风险等级、风险概率、训练数据天数、置信度等级、运行模式和是否异常；其余明细保存为 JSON：

- `input_snapshot`
- `fusion_meta`
- `bp_forecast`
- `training_meta`
- `recommendations`
- `anomaly_flags`

## 11. 前端结构设计

前端以页面 + 业务模块的方式组织。

### 11.1 页面层

主要页面包括：

- `PredictionPage`
- `BPRecordsPage`
- `ProfilePage`
- `HistoryPage`
- `AdminOverviewPage`
- `AdminUsersPage`
- `AdminPredictionGovernancePage`
- `AdminExportPage`

### 11.2 业务模块层

位于 `frontend/src/features/`，包括：

- `prediction`
- `bp-records`
- `history`
- `health-tasks`

这种结构便于把页面逻辑、请求逻辑、组件逻辑和类型定义拆开。

### 11.3 当前交互优化方向

当前版本前端强调“更适合普通用户”：

- 首页增加主要信息与快捷入口
- 长页面通过 tab 分块展示
- 说明文字简化，减少过多小字
- 预测结果说明更自然
- 预测页的预测前阻断提示必须可行动；风险因素档案不完整时，提示直接进入 `ProfilePage` 的 `risk-factors` 标签页
- 个人中心的风险因素档案表单只把年龄、性别、身高、体重标记为预测前必填；当前是否吸烟、日吸烟支数、降压药、糖尿病、总胆固醇和血糖保持可缺失语义
- 预测结果治理中的 `missing_key_profile_fields` 表示模型输入字段缺失的数据质量信号，不表示本次预测绕过了风险因素档案最低完整性阻断
- 普通用户预测成功后不额外展示可缺失风险因素提示；成功页只承载预测结果，模型输入字段缺失留给管理员预测结果治理查看

## 12. 管理员预测结果治理设计

预测结果治理页面主要用于后台查看：

- 风险等级分布
- 置信度分布
- 异常预测记录
- 单条预测详情
- 导出治理数据

这部分非常适合在论文中体现“系统不仅能预测，还支持历史追踪、结果导出和可追溯审查”的工程价值。

### 12.1 模型治理一期范围

模型治理一期收束为预测链路治理，不新增额外治理表，而是复用 `prediction_records` 的紧凑预测记录载荷推导治理指标和异常规则。

一期治理数据主要来自：

- `prediction_records` 普通列：风险等级、风险概率、训练天数、置信度、是否异常、创建时间
- `prediction_records.input_snapshot`：档案字段完整性和模型输入快照
- `prediction_records.fusion_meta`：原始概率、融合后概率和融合调整信息
- `prediction_records.training_meta`：Prophet 置信度、训练说明、是否复用/重训
- `prediction_records.recommendations`：是否生成指南型健康建议
- `prediction_records.bp_forecast`：预测期血压点和偏高情况

一期管理员操作边界为查看、筛选和导出，不修改预测结果、风险等级或指南型健康建议。治理备注作为二期扩展能力。

## 13. 训练与实验说明

LightGBM 训练入口为：

```bash
cd backend
uv run python scripts/train_models.py
uv run python scripts/train_models.py --seed 7
uv run python scripts/train_models.py --random-seed
uv run python scripts/train_models.py --save-params scripts/experiments/my_params.json
uv run python scripts/train_models.py --params scripts/experiments/my_params.json
```

本地训练前可先导出系统补充样本：

```bash
cd backend
uv run python scripts/export_training_data.py
```

该命令默认写入 `datasets/training_data_export.csv`，也就是训练脚本读取的系统导出样本路径；如需调整最近血压均值窗口，可使用 `--recent-bp-count <n>`。网页管理员导出入口保留，但本地训练不需要依赖浏览器操作。

训练脚本不会自动触发导出。推荐本地流程固定为两步：先显式导出训练 CSV，再运行 `train_models.py`。这样训练入口只负责训练编排，离线复现实验时也不会隐式连接应用数据库。

如果 `datasets/training_data_export.csv` 不存在，训练不会失败；脚本会明确提示导出样本不存在，并只使用基础训练集完成训练。系统导出样本是补充数据源，不是训练入口的硬性前置条件。

`datasets/training_data_export.csv` 由本地数据库导出，可再生成且可能包含系统运行样本，因此通过 `.gitignore` 排除在版本控制之外。已跟踪的基础训练集继续作为训练基线保留。

如果使用 `Optuna + LightGBMTunerCV` 调参，调参过程可能较慢。手动中断时出现 `KeyboardInterrupt` 是正常现象，表示训练被人为停止，而不是系统逻辑错误。

默认训练使用固定 seed（当前为 `42`）以保证调参与评估可复现；如需对比不同随机性影响，可显式传入 `--seed <int>`，或使用 `--random-seed` 为本次训练生成新的 seed。

当前训练脚本采用固定的五段式流程：

1. 数据准备：合并基础训练集与管理员导出的系统样本
2. Baseline：训练 LightGBM 基线模型作为对照
3. 官方调优：使用 `LightGBMTunerCV` 作为唯一自动调优主路径，并开启调参进度条
4. 最终训练：用最优参数确定迭代轮数、重训最终模型并搜索分类阈值
5. 保存产物：写入 `lgbm_model.txt`、`model_config.json`、`training_meta.json` 和 `docs/reports/model_report.md`

终端输出默认只展示阶段状态、样本量、CV AUC、最终 AUC / Recall / F1、阈值、保存路径和本次实际使用的 seed。详细参数、完整指标和特征重要性进入 `docs/reports/model_report.md` 与 `training_meta.json`，避免训练过程刷屏。

### 13.1 训练参数快照与对照实验

训练脚本支持通过 `--save-params` 导出当前默认参数为 JSON 文件，以及通过 `--params` 从外部 JSON 文件加载参数配置。参数文件格式示例：

```json
{
  "seed": 42,
  "test_size": 0.2,
  "threshold_valid_size": 0.1,
  "cv_splits": 5,
  "early_stopping_rounds": 100,
  "max_boost_rounds": 2000,
  "threshold_search_mode": "recall_priority",
  "threshold_min_recall": 0.8,
  "missing_value_strategy": "native",
  "bp_meds_policy": "neutralized_for_conservative_inference",
  "label_mode": "diagnosis_plus_rule",
  "enable_feature_ablation": false,
  "multi_seed_audit_seeds": []
}
```

对照实验工作流：

```bash
# 1. 导出默认参数作为基线快照
uv run python scripts/train_models.py --save-params scripts/experiments/baseline.json

# 2. 修改 scripts/experiments/experiment.json 中的参数（如 max_boost_rounds: 3000）

# 3. 用不同参数分别训练
uv run python scripts/train_models.py --params scripts/experiments/baseline.json --seed 42
uv run python scripts/train_models.py --params scripts/experiments/experiment.json --seed 42

# 4. 比较 backend/ml_models/training_meta.json 或 docs/reports/model_report.md
```

### 13.2 调参策略可替换

默认调参使用 `LightGBMTunerCV`（Optuna 官方步进式调优）。系统支持通过 `TuningStrategy` 适配器注入替代调参策略，例如：

- `LightGBMTunerCVStrategy`：官方 Optuna 步进式调优（默认）
- `NoOpTuningStrategy`：不调参，直接使用 baseline 参数（用于纯参数对照实验）

策略通过 `run_training(tuning_strategy=...)` 注入，不改动训练编排代码即可切换。

## 14. 适合论文描述的创新点

从本科毕业论文角度，当前系统可以重点概括为以下创新或改进点：

- 结合 Prophet 与 LightGBM 形成双模型预测引擎
- 将 Prophet 预测期血压特征输入 LightGBM 风险分类模型，形成可运行的 7 天风险预测链路
- 基于 LightGBM 性能指标、特征重要性和 Prophet 训练说明支撑模型实验分析
- 引入指南型健康建议与知识库式建议映射
- 设计了 Prophet 模型持久化与增量重训阈值机制
- 实现了紧凑预测记录存储与预测结果治理页面
- 构建了前后端分离的高血压风险预测系统
- 强化了普通用户视角下的可理解性和可用性

### 14.1 论文写作主线

论文不宜按传统管理系统写成“登录注册、增删改查、后台管理”的功能堆叙。更稳妥的写作主线是：

1. 说明高血压风险预测场景和 7 天预测目标；
2. 介绍 Prophet 血压趋势预测、LightGBM 风险分类和评价指标；
3. 展开双模型预测链路，说明历史血压如何形成每日血压序列，Prophet 如何得到预测期血压特征，LightGBM 如何输出高血压发病风险概率；
4. 说明 Web 系统如何完成风险因素档案维护、血压记录采集、预测结果展示、指南型健康建议和预测记录追踪；
5. 第5章固定命名为“模型训练、实验结果与系统测试”，用 LightGBM 模型报告、特征重要性、Prophet 训练说明和系统测试结果收束实验与实现效果。

最终目录参考模型类样文，而不是传统管理系统样文：

```text
第1章  绪论
§1.1 研究背景及意义
§1.2 国内外研究现状
§1.3 研究方法与内容

第2章  相关理论介绍
§2.1 时间序列预测
§2.2 Prophet模型
§2.3 LightGBM模型
§2.4 本章小结

第3章  实验数据集与评价指标
§3.1 实验数据集介绍
§3.2 数据预处理与特征构建
§3.3 模型评价指标
§3.4 本章小结

第4章  双模型预测原理与系统设计
§4.1 Prophet血压趋势预测方法
§4.2 LightGBM风险分类方法
§4.3 双模型预测链路设计
§4.4 系统数据结构设计
§4.5 系统界面设计
§4.6 本章小结

第5章  模型训练、实验结果与系统测试
§5.1 实验环境
§5.2 LightGBM训练结果分析
§5.3 特征重要性分析
§5.4 Prophet运行策略分析
§5.5 系统功能测试
§5.6 本章小结

第6章  总结与展望
§6.1 总结
§6.2 展望
```

正文实现说明尽量不直接粘贴真实源码。第4章优先使用模型设计图、预测流程图、E-R 图、接口表、数据结构表、页面截图和核心逻辑摘要；如确需体现算法或业务规则，只给短伪代码或少量关键片段，大段源码不进入正文。

第4章图表应先解释模型链路，再展示系统落地。建议保留以下模型设计图：

- Prophet 血压趋势预测流程图：说明血压记录如何聚合为每日血压序列，并生成未来 7 天收缩压、舒张压预测；
- LightGBM 风险分类输入输出图：说明风险因素档案与预测期血压特征如何进入分类模型，输出高血压风险概率；
- 双模型预测链路图：说明 Prophet 输出如何转换为 LightGBM 输入，以及风险等级、血压趋势和健康建议如何形成预测结果；
- 预测结果治理链路图：说明输入快照、预测结果、置信度、异常标记和导出治理数据之间的关系。

第4章页面截图按预测链路组织，优先保留以下页面：

- 风险因素档案页：说明 LightGBM 风险输入来源；
- 血压记录页：说明 Prophet 趋势预测的数据来源；
- 风险预测页：说明 7 天风险预测入口；
- 预测结果页：说明风险概率、风险等级、血压趋势和健康建议输出；
- 预测历史页：说明历史预测回溯；
- 预测结果治理页：说明管理员对预测记录、置信度和异常结果的追踪。

参考文献不直接沿用任务书中的少量工具书。写作前应重新建立参考文献池，优先核验并选用近五年真实文献，覆盖高血压风险预测、Prophet 或时间序列预测、LightGBM 或机器学习分类、健康管理系统和中国高血压防治指南等方向；最终参考文献按正文引用顺序回填，并保留文献核验清单。

### 14.2 模型治理答辩表述

答辩中不宜表述为“模型治理已经完整实现”。更稳妥的表述是：当前系统已实现管理员预测治理页面，支持风险分布、置信度分布、异常记录筛查、单条详情查看和导出；后续在不改变核心数据结构的前提下，可进一步扩展为预测链路治理，增加模型复用/重训统计、数据质量异常和低置信度高风险等治理规则。

### 14.3 模型治理演示主线

答辩演示建议只展示一条主线：管理员登录后进入预测治理页面，先查看治理摘要，再筛选异常预测记录，随后打开单条预测详情，说明输入快照、融合元数据、置信度原因和指南型健康建议，最后展示治理数据导出能力。演示重点不是穷举所有规则，而是证明系统不仅能完成预测，还能追踪预测结果并帮助管理员发现重点记录。

### 14.4 模型治理与普通后台统计的区别

如果答辩中被问到模型治理和普通后台统计的区别，可以回答：普通后台统计主要关注用户数量、记录数量和系统使用情况；本系统的模型治理关注预测链路本身，包括模型是否复用或重训、预测置信度、风险等级分布、异常预测记录、输入快照和建议生成情况。因此它不是运营统计，而是围绕双模型预测结果可追踪、可解释、可审查而设计的系统级能力。

### 14.5 模型治理功能规划

答辩前的模型治理规划应优先围绕现有紧凑预测记录展开，不新增数据库表或迁移脚本，重点补强治理摘要、异常规则、单条详情和导出字段。可规划的功能包括：扩展治理摘要指标，展示总预测次数、高风险预测数量、低置信度预测占比、异常预测数量和数据不足预测数量；扩展异常预测规则，覆盖高风险且低置信度、数据不足仍完成预测、模型输入字段缺失、预测血压偏高但风险等级偏低等情形；补全治理详情，展示输入快照、融合元数据、置信度原因、指南型健康建议和预测点摘要；补全导出字段，导出异常类型、置信度、关键输入字段和风险概率。

答辩后的扩展可以进一步面向完整模型治理闭环，包括治理备注、模型资产状态页、Prophet 复用/重训趋势图、LightGBM 版本与训练报告对照、数据质量趋势监控等。这些能力需要更多交互和数据结构设计，适合作为系统后续演进方向，而不是答辩前的必须完成项。
