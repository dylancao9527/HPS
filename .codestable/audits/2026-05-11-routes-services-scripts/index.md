---
doc_type: audit-index
audit: 2026-05-11-routes-services-scripts
scope: backend routes, services, and scripts.
created: 2026-05-11
status: fixed
total_findings: 6
---

# routes-services-scripts 审计报告

## 范围

本次审计范围为 `backend/routes/`、`backend/services/`、`backend/scripts/`。扫描维度覆盖 bug 隐患、安全、性能、可维护性和架构偏离，并对照 `.codestable/architecture/ARCHITECTURE.md` 中认证账户、管理员模块、血压记录、预测历史、训练脚本和训练数据导出说明。

## 总评

共发现 6 条问题：P1 3 条、P2 3 条；性质分布为 security 3 条、bug 1 条、performance 1 条、maintainability 1 条。本轮已全部修复并补充回归测试，修复记录见 [fix-note.md](fix-note.md)。

## 发现清单

| # | 性质 | 严重度 | 置信度 | 标题 | 文件 |
|---|---|---|---|---|---|
| 1 | security | P1 | high | 本地模拟邮箱验证码查询接口启用后无鉴权暴露验证码 | [finding-01.md](finding-01.md) |
| 2 | security | P1 | high | 邮箱验证码校验没有失败次数限制，重置密码可被在线撞码 | [finding-02.md](finding-02.md) |
| 3 | security | P1 | medium | demo 用户脚本默认重置真实库并创建固定密码账号 | [finding-03.md](finding-03.md) |
| 4 | bug | P2 | high | 血压记录的非法 recorded_at 会被静默替换为当前时间 | [finding-04.md](finding-04.md) |
| 5 | performance | P2 | high | 多个列表/趋势端点未限制 per_page/limit 上限 | [finding-05.md](finding-05.md) |
| 6 | maintainability | P2 | high | AuthAccountService 聚合验证码、登录和账号维护流程，修改风险偏高 | [finding-06.md](finding-06.md) |

## 按维度分布

| 性质 | P0 | P1 | P2 | 合计 |
|---|---|---|---|---|
| bug | 0 | 0 | 1 | 1 |
| security | 0 | 3 | 0 | 3 |
| performance | 0 | 0 | 1 | 1 |
| maintainability | 0 | 0 | 1 | 1 |
| arch-drift | 0 | 0 | 0 | 0 |
| **合计** | **0** | **3** | **3** | **6** |

## 修复结果

- **Finding 1**：本地模拟邮箱查询接口增加本机/开发令牌访问边界，并脱敏返回字段。
- **Finding 2**：邮箱验证码改用安全随机数，并加入失败次数锁定。
- **Finding 3**：demo 用户脚本默认预览，写库和删除都需要显式参数；固定密码已移除。
- **Finding 4**：非法 `recorded_at` 返回 400，不再静默替换成当前时间。
- **Finding 5**：血压记录、管理员用户和预测趋势端点统一分页/limit 限幅。
- **Finding 6**：认证账户服务拆分为注册、登录、账号维护、密码重置子服务。
