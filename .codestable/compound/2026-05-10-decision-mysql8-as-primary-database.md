---
doc_type: decision
category: tech-stack
date: "2026-05-10"
slug: mysql8-as-primary-database
status: active
area: database
tags: [mysql8, sqlalchemy, flask-migrate, persistence]
---

## 背景

系统需要持久化用户账号、健康档案、血压记录、预测记录和 Prophet 模型元数据。项目级约束、README 和架构文档均明确数据库为 MySQL 8。

## 决定

业务数据库采用 MySQL 8；后端通过 SQLAlchemy ORM 与 PyMySQL 访问数据库，通过 Flask-Migrate 管理 schema 演进。

## 理由

MySQL 8 承担系统主要关系型业务数据持久化，适配用户、档案、血压记录、预测记录和模型元数据等结构化数据。SQLAlchemy 与 Flask-Migrate 让模型定义、查询和迁移流程与 Flask 后端保持一致。

## 考虑过的替代方案

现有文档未记录 PostgreSQL、SQLite 或其他数据库方案的系统性对比；本条归档当前已拍板和已实现的数据库选型。

## 后果

- 未经确认，不修改数据库结构、迁移脚本或生产配置。
- 新增持久化能力应考虑 MySQL 8、SQLAlchemy 模型和 Flask-Migrate 迁移的一致性。
- 本地数据库连接通过 `DATABASE_URL` 等环境变量配置。

## 相关文档

- `AGENTS.md`
- `README.md`
- `backend/pyproject.toml`
- `.codestable/architecture/ARCHITECTURE.md`
- `.codestable/attention.md`
