# AGENTS.md

本文件是 AI 协作的项目级硬约束入口。所有 AI 协作工作流默认遵守本文件的所有规则。

## 代码规范

- 待项目维护者补充语言、框架、命名、格式化和测试规范。
- 后端采用Python语言、Flask框架、UV进行项目管理、Flask Migrate、Flask Sqlalchemy
- 前端采用React+TypeScrypt、React Router。
- 数据库Mysql8
- 模型LightGBM和Prophet

## 禁止事项

- 未经确认，不删除、重命名或大范围移动已有文件。
- 未经确认，不修改数据库结构、迁移脚本或生产配置。
- 未经确认，不引入新的框架级依赖或替换核心技术栈。

## 已知坑

- 待项目维护者补充历史问题、环境差异和容易误改的位置。

## UI 验证要求

- 涉及前端视觉、交互或路由的改动，需要在浏览器中验证关键路径。

## 运行与验证

- 后端测试：`cd backend && uv run pytest`（23 tests）
- 模型训练：`cd backend && uv run python scripts/train_models.py [--seed N | --random-seed] [--params config.json | --save-params config.json]`
- Prophet 评价：`cd backend && uv run python scripts/evaluate_prophet_accuracy.py`
- 趋势融合评价：`cd backend && uv run python scripts/evaluate_trend_fusion.py`
- 训练数据导出：`cd backend && uv run python scripts/export_training_data.py [--recent-bp-count N]`
- 后端启动：`cd backend && uv run flask run`
- 前端构建：`cd frontend && pnpm run build`

## Agent skills

### Issue tracker

Issues and PRDs are tracked in GitHub Issues for `honestman9527/HPS`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default five-label triage vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single-context domain documentation layout. See `docs/agents/domain.md`.
