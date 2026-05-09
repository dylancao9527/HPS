# 高血压风险预测系统

基于 `Prophet + LightGBM` 的高血压风险预测系统，采用前后端分离架构：

- 前端：`React 19 + Vite + TypeScript`
- 后端：`Flask + SQLAlchemy + JWT`
- 数据库：`MySQL 8`
- 时序预测：`Prophet`
- 风险分类：`LightGBM`

本项目面向“健康管理辅助”场景，核心目标是为普通用户提供更自然、更易理解的风险评估、趋势预测和生活方式建议，不用于替代临床诊断。

## 项目亮点

- 支持用户注册、登录、个人档案维护、血压记录管理、风险预测与历史查看
- 支持管理员查看用户、系统统计、训练数据导出、预测结果治理信息
- 使用 `LightGBM` 进行风险分类，使用 `Prophet` 进行血压趋势预测
- 预测结果支持“指南型健康建议”输出，建议语气更自然、更贴近日常健康管理
- `Prophet` 模型支持本地持久化、内存缓存与增量重训阈值策略
- 预测历史采用紧凑预测记录存储，便于治理、导出、追踪和后续论文撰写

## 当前核心能力

### 普通用户侧

- 首页信息总览与快捷入口
- 血压记录录入、查询、删除
- 风险预测与趋势预测
- 预测解释、推荐建议、历史记录查看
- 个人档案维护
- 今日健康任务提醒
- 周健康报告：最近7天与前7天的血压、风险和记录持续性对比

### 管理员侧

- 用户管理
- 系统统计总览
- 训练数据导出
- 预测结果治理页面

## 目录结构

```text
HPS/
├─ backend/
│  ├─ app.py                     # 应用入口
│  ├─ config.py                  # 后端配置
│  ├─ models/                    # ORM 模型
│  ├─ prediction/                # 预测分层 (api/application/domain/infrastructure)
│  ├─ routes/                    # API 路由
│  ├─ services/                  # 业务服务
│  ├─ training/                  # LightGBM 训练、特征契约与调参
│  ├─ utils/                     # 通用工具 (时间处理等)
│  ├─ scripts/                   # CLI 脚本 (训练、导出、评价)
│  │  └─ experiments/            # 训练参数实验配置
│  ├─ tests/                     # 后端测试
│  ├─ database/                  # SQL dump
│  ├─ migrations/                # 数据库迁移
│  └─ runtime/                   # 运行时文件 (Prophet 模型等)
├─ frontend/
│  └─ src/
│     ├─ features/               # 业务模块
│     ├─ pages/                  # 页面
│     ├─ components/             # 通用组件
│     ├─ test/                   # 前端测试
│     └─ types/                  # 前端类型定义
├─ datasets/                     # 数据集与导出数据
├─ docs/
│  ├─ reports/                   # 训练/评价报告 (脚本生成产物)
│  ├─ architecture/              # 架构文档
│  └─ adr/                       # 架构决策记录
├─ start-dev.bat                 # Windows 开发模式启动脚本
└─ start.bat                     # Windows 单服务启动脚本
```

## 环境要求

- Python `3.10+`
- Node.js `18+`
- MySQL `8.x`
- `uv`
- `pnpm`

建议先确认命令可用：

```bash
python --version
node --version
uv --version
pnpm --version
mysql --version
```

## 安装与初始化

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd HypertensionPredictionSystem
```

### 2. 安装后端依赖

```bash
cd backend
uv sync
cd ..
```

### 3. 安装前端依赖

```bash
cd frontend
pnpm install
cd ..
```

## 数据库与环境变量

### 1. 创建数据库

```sql
CREATE DATABASE hypertension
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
```

如需单独用户，可选：

```sql
CREATE USER 'hypertension_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON hypertension.* TO 'hypertension_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. 配置 `backend/.env`

复制示例文件：

```bash
copy backend\.env.example backend\.env
```

推荐至少包含以下字段：

```env
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/hypertension
SECRET_KEY=replace-with-a-long-random-string-at-least-32-bytes
JWT_EXPIRATION_DAYS=7

ADMIN_USERNAME=dream
ADMIN_PASSWORD=change-me
ADMIN_EMAIL=admin@hypertension.local
INIT_ADMIN_ON_STARTUP=1

EXPORT_RECENT_BP_COUNT=5

ENABLE_LOCAL_MOCK_EMAIL_SERVICE=1
LOCAL_MOCK_EMAIL_STORE=backend/runtime/mock_emails.json

PROPHET_MAX_TRAIN_DAYS=90
PROPHET_RETRAIN_AFTER_DAYS=3
PROPHET_CACHE_VERSION=1
PROPHET_MODEL_STORAGE_ROOT=backend/runtime/prophet_models
PROPHET_MEMORY_CACHE_TTL_SECONDS=900
PROPHET_MAX_INACTIVE_METADATA_PER_SLOT=1
PROPHET_CLEANUP_ENABLED=1
PROPHET_CLEANUP_MAX_INACTIVE_AGE_HOURS=24
```

关键配置说明：

- `DATABASE_URL`：MySQL 连接地址
- `SECRET_KEY`：JWT 签名密钥
- `ADMIN_*`：管理员初始化账号
- `ENABLE_LOCAL_MOCK_EMAIL_SERVICE`：本地邮件模拟服务开关
- `PROPHET_MAX_TRAIN_DAYS`：Prophet 训练窗口上限
- `PROPHET_RETRAIN_AFTER_DAYS`：新增多少个自然日血压数据后重新训练 Prophet 模型
- `PROPHET_MODEL_STORAGE_ROOT`：Prophet 模型文件目录
- `PROPHET_MEMORY_CACHE_TTL_SECONDS`：内存缓存 TTL

### 3. 执行数据库迁移

```bash
cd backend
uv run flask db upgrade
cd ..
```

启动脚本不会自动执行数据库迁移。首次部署、更新迁移脚本或切换数据库后，请先手动执行上述命令，再启动服务。

启动脚本只在 `backend/.venv/` 或 `frontend/node_modules/` 缺失时自动安装依赖。依赖声明变更后，建议手动运行 `uv sync --locked` 或 `pnpm install --frozen-lockfile`。

## 启动项目

### 方式一：Windows 一键启动

```bash
start-dev.bat
```

默认会启动：

- 后端：`http://localhost:5000`
- 前端：`http://localhost:5173`

启动脚本中的 Flask 默认绑定 `0.0.0.0`，便于局域网设备访问演示；本机访问仍使用 `localhost` 地址。

`start-dev.bat` 会在新窗口启动后端，并在当前窗口运行前端开发服务器。停止时，在当前窗口按 `Ctrl+C` 停止前端，关闭后端窗口停止 Flask。

### 方式二：手动启动

终端 1：

```bash
cd backend
uv run flask --app app:create_app --debug run --host 0.0.0.0 --port 5000
```

终端 2：

```bash
cd frontend
pnpm dev
```

### 单服务模式

```bash
start.bat
```

`start.bat` 默认会先执行前端构建，再启动 Flask 单服务。单服务模式下，Flask 会直接托管 `backend/static/` 中的前端构建产物。

该脚本适合本地演示和课程项目运行，不代表正式生产环境的 WSGI 部署方案。

如果确认 `backend/static/` 中已有最新前端产物，可以跳过构建：

```bash
start.bat --skip-build
```

## 常用命令

### 后端测试

```bash
cd backend
uv run pytest
```

### 前端测试

```bash
cd frontend
pnpm test
```

### 前端构建

```bash
cd frontend
pnpm build
```

## 模型训练

LightGBM 训练入口：

```bash
cd backend
uv run python scripts/train_models.py
uv run python scripts/train_models.py --seed 7
uv run python scripts/train_models.py --random-seed
uv run python scripts/train_models.py --save-params scripts/experiments/baseline.json
uv run python scripts/train_models.py --params scripts/experiments/baseline.json
```
### 对照实验

```bash
cd backend

# 步骤 1：编辑两组参数
# scripts/experiments/baseline.json  — 对照组（当前默认参数）
# scripts/experiments/experiment.json — 实验组（你修改的参数）

# 步骤 2：跑 baseline，保存结果
uv run python scripts/train_models.py --params scripts/experiments/baseline.json
copy ml_models/training_meta.json scripts/experiments/baseline_result.json

# 步骤 3：跑 experiment，保存结果
uv run python scripts/train_models.py --params scripts/experiments/experiment.json
copy ml_models/training_meta.json scripts/experiments/experiment_result.json

# 步骤 4：生成对比报告
uv run python scripts/experiments/compare.py --output ../docs/reports/comparison_report.md
```

对比报告输出到 `docs/reports/comparison_report.md`，参数说明和指标解读见 `docs/training_guide.md`。

本地训练前如需使用系统补充样本，可以先显式导出训练数据：

```bash
cd backend
uv run python scripts/export_training_data.py
uv run python scripts/export_training_data.py --recent-bp-count 5
```

导出命令默认写入 `datasets/training_data_export.csv`。训练脚本会自动读取该文件作为补充数据源；如果文件不存在，训练不会失败，而是只使用基础训练集 `datasets/framingham.csv`。训练脚本不会自动连接数据库导出样本，推荐保持“先导出、再训练”的两步流程。

### 训练说明

- 训练流程会读取数据集、构造特征、执行基线训练、官方调优、最终训练和阈值搜索，并输出模型文件到 `backend/ml_models/`
- 默认使用固定 seed（当前为 `42`）保证结果可复现；可通过 `--seed <int>` 指定 seed，或用 `--random-seed` 为单次训练生成新 seed
- 使用 `--params <path>` 时，参数文件中的 `seed` 会作为默认 seed；如果同时传入 `--seed <int>`，命令行 seed 优先
- `--save-params <path>` 会导出当前默认训练参数，便于保存基线配置和做对照实验
- 参数文件可配置测试集比例、阈值验证集比例、最大训练轮数、早停轮数、学习率、缺失值策略、标签来源策略、是否启用特征消融和多 seed 审计等训练设置
- 默认调优策略为 `LightGBMTunerCV`；代码层可通过 `TuningStrategy` 注入 `NoOpTuningStrategy` 等替代策略做纯参数对照实验
- 训练完成后会生成 `lgbm_model.txt`、`model_config.json`、`training_meta.json` 和 `docs/reports/model_report.md`
- `backend/ml_models/`、`docs/reports/model_report.md` 和 `datasets/training_data_export.csv` 属于本地生成产物，默认不纳入版本控制
- 若使用 `Optuna + LightGBMTunerCV`，调参阶段可能耗时较长
- 如果手动中断训练，终端中出现 `KeyboardInterrupt` 属于正常现象，不代表代码报错，只表示调参过程被人为停止

## 预测引擎说明

### 风险预测链路

`POST /api/predict` 的核心流程如下：

1. 读取用户档案和最新血压记录
2. 检查当前用户的 Prophet 模型状态
3. 判断是否达到重训阈值
4. 若未达到阈值，复用已有 Prophet 模型重新生成趋势预测
5. 若达到阈值，基于最新血压数据重新训练 Prophet 模型
6. 使用 LightGBM 计算基础风险概率
7. 使用趋势融合策略修正风险结果
8. 生成指南型健康建议
9. 持久化预测结果与紧凑明细载荷

### 当前 Prophet 策略

当前实现已经不是“每次都重新训练”，也不是“直接复用旧预测结果”，而是：

- 复用模型：当新增血压自然日数小于 `PROPHET_RETRAIN_AFTER_DAYS`
- 重新训练：当新增血压自然日数大于等于阈值
- 每次预测都重新生成本次预测结果，不直接复用旧 prediction record

### Prophet 持久化设计

Prophet 采用三层结构：

1. 数据库元数据：`user_prophet_models`
2. 文件模型资产：`backend/runtime/prophet_models/`
3. 内存热点缓存：短 TTL 缓存最近模型

这样做的好处是：

- 避免把大型模型二进制直接塞进数据库
- 模型可复用、可清理、可治理
- 连续请求时响应更快

## 后端 API 概览

### 认证与账户

- `POST /api/auth/send-register-code`
- `POST /api/auth/register`
- `POST /api/auth/login/user`
- `POST /api/auth/login/admin`
- `GET /api/auth/me`
- `POST /api/auth/change-password`
- `POST /api/auth/send-change-email-code`
- `POST /api/auth/update-account`
- `POST /api/auth/forgot-password`
- `POST /api/auth/reset-password`

### 用户接口

- `GET /api/profile`
- `PUT /api/profile`
- `GET /api/bp-records`
- `POST /api/bp-records`
- `DELETE /api/bp-records/:id`
- `DELETE /api/bp-records/batch`
- `GET /api/health-tasks/today`
- `GET /api/weekly-report`
- `POST /api/predict`
- `GET /api/predictions`
- `DELETE /api/predictions/:id`
- `DELETE /api/predictions/batch`
- `GET /api/profile/prediction-trend`
- `GET /api/bp-data-status`

### 管理员接口

- `GET /api/admin/users`
- `PUT /api/admin/users/:id`
- `DELETE /api/admin/users/:id`
- `DELETE /api/admin/users/batch`
- `GET /api/admin/export/training`
- `GET /api/admin/stats`
- `GET /api/admin/governance/predictions`
- `GET /api/admin/governance/predictions/:id`
- `GET /api/admin/governance/export`

### 开发辅助接口

- `GET /api/dev/mock-emails/latest`（仅 `ENABLE_LOCAL_MOCK_EMAIL_SERVICE=1` 时注册）
- `GET /api/health`

## 论文可强调的实现点

- 前后端分离的健康管理系统架构设计
- 基于 `Prophet + LightGBM` 的双模型预测方案
- 面向普通用户的指南型健康建议生成
- 基于中国高血压防治思路的知识库式建议映射
- Prophet 模型持久化与“按新增自然日阈值重训”的工程策略
- 预测结果治理、历史回溯与紧凑预测记录存储设计

## 相关文档

- 架构文档：[docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)
- 领域语言：[CONTEXT.md](CONTEXT.md)
- 训练报告：[docs/reports/model_report.md](docs/reports/model_report.md)
- Prophet 评价报告：[docs/reports/prophet_evaluation_report.md](docs/reports/prophet_evaluation_report.md)
- 趋势融合评价报告：[docs/reports/trend_fusion_report.md](docs/reports/trend_fusion_report.md)

