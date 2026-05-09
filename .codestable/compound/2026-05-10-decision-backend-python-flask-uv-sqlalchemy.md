---
doc_type: decision
category: tech-stack
date: "2026-05-10"
slug: backend-python-flask-uv-sqlalchemy
status: active
area: backend
tags: [python, flask, uv, flask-sqlalchemy, flask-migrate, jwt]
---

## 背景

后端负责认证、业务数据存储、预测编排、建议生成和管理员治理接口。项目级协作约束、README、架构文档和 `backend/pyproject.toml` 均指向 Python + Flask 后端栈。

## 决定

后端采用 Python 3.10+、Flask 3、Flask-SQLAlchemy、Flask-Migrate、PyMySQL 和 PyJWT；项目依赖与命令运行使用 UV 管理。

## 理由

Flask 适合当前 API 服务和预测编排体量；Flask-SQLAlchemy 与 Flask-Migrate 分别承载 ORM 和数据库迁移；PyMySQL 对接 MySQL；PyJWT 承载认证令牌；UV 固定依赖管理和本地命令入口，和现有测试、训练、启动命令一致。

## 考虑过的替代方案

现有文档未记录 FastAPI、Django 或其他依赖管理工具的系统性对比；本条归档当前已拍板和已实现的后端选型。

## 后果

- 后端新增接口和服务应优先沿用 Flask 项目结构与现有扩展对象。
- 未经确认，不替换核心框架或引入新的框架级依赖。
- 后端测试命令保持为 `cd backend && uv run pytest`。

## 相关文档

- `AGENTS.md`
- `README.md`
- `backend/pyproject.toml`
- `.codestable/architecture/ARCHITECTURE.md`
- `.codestable/attention.md`
