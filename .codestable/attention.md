# Attention

本文件是 CodeStable 技能启动必读的项目注意事项入口。所有 CodeStable 子技能开始工作前必须读取它。

## 项目碎片知识

<!-- cs-note managed: 用 cs-note 维护，新条目按下面分节追加 -->

### 编译与构建

- 后端采用 Python + Flask + UV + Flask-Migrate + Flask-SQLAlchemy。
- 前端采用 React + TypeScript + React Router。
- 数据库使用 MySQL 8。
- 模型相关工作围绕 LightGBM 和 Prophet 展开。
- 前端构建：`cd frontend && pnpm run build`。

### 运行与本地起服务

- 后端启动：`cd backend && uv run flask run`

### 测试

- 后端测试：`cd backend && uv run pytest`
- 前端构建：`cd frontend && pnpm run build`
- Prophet 评价：`cd backend && uv run python scripts/evaluate_prophet_accuracy.py`
- 趋势融合评价：`cd backend && uv run python scripts/evaluate_trend_fusion.py`

### 命令与脚本陷阱

- 未经确认，不删除、重命名或大范围移动已有文件。
- 未经确认，不修改数据库结构、迁移脚本或生产配置。
- 未经确认，不引入新的框架级依赖或替换核心技术栈。
- 训练数据导出：`cd backend && uv run python scripts/export_training_data.py [--recent-bp-count N]`
- 模型训练：`cd backend && uv run python scripts/train_models.py [--seed N | --random-seed] [--params config.json | --save-params config.json]`
- 模型训练不自动导出训练数据；需要补充系统样本时先显式导出，再运行训练脚本。
- LightGBM 对照实验统一使用 `recall_priority`，先 `--run-name ... --no-promote` 留档，确认最佳后再 `--promote` 发布生产模型。

### 路径与目录约定

- 涉及前端视觉、交互或路由的改动，需要在浏览器中验证关键路径。
- CodeStable 领域语言入口是 `.codestable/architecture/domain-language.md`；旧 `CONTEXT.md` 已迁移并删除。
- CodeStable 启动硬约束入口是 `.codestable/attention.md`；旧 `AGENTS.md` 已迁移并删除。

### 环境变量与凭证

- 现有凭证、环境变量和本地密钥保持原位，不在这里补写猜测值。

### 其他

- 后端测试基线为 `cd backend && uv run pytest`。
- 需要模型训练或评估时，优先复用仓库现有脚本与参数约定。
- Issues 和 PRD 跟踪使用 GitHub Issues：`honestman9527/HPS`。
- Triage 使用默认五标签词汇。
