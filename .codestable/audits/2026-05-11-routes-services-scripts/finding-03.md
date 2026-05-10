---
doc_type: audit-finding
audit: 2026-05-11-routes-services-scripts
finding_id: "security-03"
nature: security
severity: P1
confidence: medium
suggested_action: cs-issue
status: fixed
---

# Finding 03：demo 用户脚本默认重置真实库并创建固定密码账号

## 速答

`seed_demo_users.py` 直接连接当前 `.env` 指向的应用数据库，默认删除旧 demo 用户并创建一批固定密码账号，没有显式环境检查或二次确认。

## 关键证据

- `backend/scripts/seed_demo_users.py:15` — demo 用户统一密码硬编码为 `Demo@123456`。
- `backend/scripts/seed_demo_users.py:236` — `seed_demo_users()` 支持 `reset_existing` 删除已有 demo 用户。
- `backend/scripts/seed_demo_users.py:240` — reset 时逐个 `db.session.delete(user)` 删除匹配前缀的用户。
- `backend/scripts/seed_demo_users.py:274` — `main()` 直接创建真实 Flask app，使用当前环境配置。
- `backend/scripts/seed_demo_users.py:277` — 命令行入口默认 `seed_demo_users(reset_existing=True)`。
- `backend/scripts/seed_demo_users.py:282` — 脚本还会把统一密码打印到终端。

## 影响

如果开发者在生产或共享演示数据库配置下误运行该脚本，会删除所有 `demo_compare_` / `demo_showcase_` 前缀用户，并创建可预测密码账号。触发条件是运维误操作，但后果包含数据删除和弱凭证账号。

## 修复方向

为脚本增加显式 `--reset`、`--yes-i-understand` 或环境白名单；默认只预览，不写库。固定密码改为参数或运行时生成，并提示只用于本地。

## 建议动作

`cs-issue`，因为这是脚本级高影响误操作边界，修复可以很窄并补 CLI 参数测试。

## 修复结果

已修复。`seed_demo_users.py` 默认进入预览模式，不创建 Flask app、不写数据库；实际写入必须显式传 `--apply`。删除旧 demo 用户必须同时传 `--reset-existing --yes-i-understand`。固定密码已移除，改为 `--password` / `DEMO_USER_PASSWORD` 显式提供或运行时生成。
