---
doc_type: decision
category: tech-stack
date: "2026-05-10"
slug: frontend-react-vite-typescript-router
status: active
area: frontend
tags: [react, vite, typescript, react-router, recharts]
---

## 背景

系统采用前后端分离架构，前端需要承担普通用户交互、表单输入、图表展示、历史查看和管理员界面。现有架构文档与依赖文件已经固定前端应用为 React 技术栈。

## 决定

前端采用 `React 19 + Vite 8 + TypeScript + React Router DOM` 作为核心技术栈；图表展示使用 `Recharts`，界面图标使用 `lucide-react`。

## 理由

该组合与项目当前前后端分离形态匹配：React 承载页面与业务组件，React Router DOM 承载页面路由，TypeScript 固化接口和页面状态类型，Vite 负责开发服务与生产构建，Recharts 支持血压趋势、风险分布等数据展示。

## 考虑过的替代方案

现有文档未记录系统性前端框架对比；本条归档当前已拍板和已实现的选型。

## 后果

- 前端新增页面、路由和业务组件应继续沿用 React + TypeScript + React Router DOM。
- 涉及前端视觉、交互或路由的改动，需要在浏览器中验证关键路径。
- 前端构建命令保持为 `cd frontend && pnpm run build`。

## 相关文档

- `README.md`
- `frontend/package.json`
- `.codestable/architecture/ARCHITECTURE.md`
- `.codestable/attention.md`
