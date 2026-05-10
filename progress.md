# 论文补强进度记录

## 2026-05-10

### 本次已完成

- 读取并应用 `planning-with-files-zh`、`lunwen`、`cs`、`cs-brainstorm` 技能规则。
- 扫描 `lunwen-doc`，确认已有主论文、DOCX、附件、参考文献池、截图和图表资源。
- 搜索 Prophet、LightGBM、融合、实验、图表和截图相关材料，确认可用数据来源。
- 创建 `task_plan.md`、`findings.md`、`progress.md` 作为持久化计划文件。
- 创建 `lunwen-doc/论文补强与结构优化计划.md`，记录章节结构、公式、实验解释、图表、截图和待确认问题。

### 当前判断

- `cs` 路由：这是论文大任务，不是代码 feature；适合先用 `cs-brainstorm` 收敛问题，再按文件规划推进。
- `lunwen` 状态：已有模板、任务书、样文和主论文材料，因此可以进入“结构优化与补写计划”，但正文大改前仍需用户确认是否直接修改主论文 MD。

### 下一步

- 用户已确认：可以直接改主论文 Markdown；E-R 图需要重绘为实体 E-R；截图沿用现有；LightGBM 对照实验重新训练；公式按章节编号。
- 当前进入第 2 阶段：先重新训练 LightGBM 对照实验，生成新报告后再补写主论文。

### 本次继续推进

- 按用户确认重新训练 LightGBM 对照实验，生成/更新：
  - `backend/scripts/experiments/baseline_result.json`
  - `backend/scripts/experiments/experiment_result.json`
  - `docs/reports/comparison_report.md`
  - `docs/reports/model_report.md`
  - `backend/ml_models/model_config.json`
- 新实验口径：最终模型采用 `f1` 阈值策略，Tuned 指标为 AUC 0.9480、Accuracy 0.9021、Precision 0.8125、Recall 0.8897、F1 0.8494、Threshold 0.6676。
- 将 `figure-4-5-core-er.mmd` 从 Mermaid `erDiagram` 字段清单重绘为 Chen 风格实体 E-R 图，并重新导出 PNG/SVG。
- 补强主论文 Markdown：
  - 第 2 章增加 Prophet 加性模型、分段趋势项、LightGBM 目标函数、叶子权重和 Sigmoid 概率公式。
  - 第 3 章更新缺失值、数据划分和公式编号。
  - 第 4 章增加预测期血压特征、LightGBM 原始概率、趋势融合、风险等级映射公式，并更新 E-R 图说明。
  - 第 5 章更新 LightGBM 调参结果、混淆矩阵、阈值策略对照和结论指标。

### 遇到的错误

| 错误 | 尝试次数 | 解决方案 |
|---|---:|---|
| `mmdc` 找不到 Puppeteer Chrome 148 缓存 | 1 | 查找本机 Chrome，设置 `PUPPETEER_EXECUTABLE_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe` 后本地渲染成功 |
| Kroki Mermaid 渲染请求超时 | 1 | 放弃网络渲染，改用本地 Chrome + `mmdc` |

### 校验结果

- 主论文 Markdown 中 11 个图片链接均存在。
- 实体 E-R 图 PNG/SVG 已渲染成功，并已人工查看 PNG，形状包含矩形实体、菱形关系和椭圆属性。
- 已扫主论文与计划文件中的旧数据占位；主论文不再含旧数据划分、旧缺失值或“最终采用 recall_priority”的说法。

### E-R 图规范化补改

- 用户指出 Mermaid 版 E-R 图属性不完整，且需要按示例使用 draw.io 风格绘制。
- 新增正式源文件：`lunwen-doc/论文写作材料/thesis-assets/diagrams/figure-4-5-core-er.drawio`。
- 重新生成 `figure-4-5-core-er.png` 与 `figure-4-5-core-er.svg`，补全核心实体字段，标注 PK、FK、派生属性 BMI 和 1/N 基数。
- 更新主论文 §4.4、图片清单和论文写作材料 README，说明图4-5 的正式源文件为 draw.io。
- 当前环境未发现 draw.io CLI，因此 `.drawio` 由标准 XML 生成，PNG/SVG 由同一布局导出预览；后续可用 draw.io Desktop 打开 `.drawio` 继续微调。
