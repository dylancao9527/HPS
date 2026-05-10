# 《基于Prophet与LightGBM的高血压风险预测系统设计与实现》图片清单

## 生成说明

- 图表资产目录：`lunwen-doc/论文写作材料/thesis-assets/diagrams/`
- 页面截图目录：`lunwen-doc/论文写作材料/thesis-assets/screenshots/`
- 模型图大多保留 `.mmd`、`.png`、`.svg` 三种文件；图4-5 E-R 图因需要规范实体、联系、属性和基数标注，正式源文件改为 `.drawio`，后续附件 `.docx` 需收录该 `.drawio` 源文件或导出的 XML 源码。本轮根据最新数据库结构只更新 `figure-4-5-core-er.drawio`，不重新导出 PNG/SVG/PDF。
- 页面截图基于本地系统真实运行页面生成；普通用户使用 `demo_showcase_high`，管理员使用 `demo_admin_showcase`。
- 预测结果截图来自真实 `/api/predict` 调用，生成了 Prophet 血压趋势预测与 LightGBM 风险概率输出。

## 第4章建议图表

| 编号 | 建议图题 | 文件 | 放置位置 | 用途 |
| --- | --- | --- | --- | --- |
| 图4-1 | Prophet 血压趋势预测流程图 | `lunwen-doc/论文写作材料/thesis-assets/diagrams/figure-4-1-prophet-bp-trend-flow.png` | §4.1 | 说明血压日序列聚合、训练上下文、模型复用/重训与 7 天预测输出 |
| 图4-2 | LightGBM 风险分类输入输出图 | `lunwen-doc/论文写作材料/thesis-assets/diagrams/figure-4-2-lightgbm-risk-io.png` | §4.2 | 说明风险因素档案与 Prophet 预测期血压特征如何进入 LightGBM |
| 图4-3 | Prophet-LightGBM 双模型预测链路图 | `lunwen-doc/论文写作材料/thesis-assets/diagrams/figure-4-3-prophet-lightgbm-pipeline.png` | §4.3 | 作为第4章模型链路主图，展示双模型串联、风险融合、建议与记录留存 |
| 图4-4 | 预测结果治理链路图 | `lunwen-doc/论文写作材料/thesis-assets/diagrams/figure-4-4-prediction-governance-flow.png` | §4.3 或 §4.5 | 说明预测记录如何支撑历史回看、治理筛选与导出 |
| 图4-5 | 核心实体 E-R 图 | `lunwen-doc/论文写作材料/thesis-assets/diagrams/figure-4-5-core-er.drawio` | §4.4 | 按 Chen E-R 图规范说明用户、风险因素档案、血压记录、预测记录和精简后的 Prophet 模型资产索引关系；本轮只维护 draw.io 源文件 |
| 图4-6 | 风险因素档案页面 | `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-6-risk-factor-profile-page.png` | §4.5 | 展示参与模型预测的年龄、性别、BMI、吸烟、用药、糖尿病等风险因素维护 |
| 图4-7 | 血压记录页面 | `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-7-bp-records-page.png` | §4.5 | 展示用户日常血压记录列表和分页管理 |
| 图4-8 | 7 天风险预测页面 | `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-8-risk-prediction-page.png` | §4.5 | 展示预测前的数据准备状态、血压数据充分性和预测入口 |
| 图4-9 | 7 天风险预测结果页面 | `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-9-prediction-result-page.png` | §4.5 | 展示高血压风险概率、风险等级、血压趋势图和指南型健康建议 |
| 图4-10 | 预测历史页面 | `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-10-prediction-history-page.png` | §4.5 | 展示普通用户历史预测记录列表和回看入口 |
| 图4-11 | 预测结果治理页面 | `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-11-prediction-governance-page.png` | §4.5 | 展示管理员端治理摘要、异常筛查、记录列表和治理明细 |

## 截图尺寸核验

| 文件 | 尺寸 | 说明 |
| --- | --- | --- |
| `figure-4-6-risk-factor-profile-page.png` | 1440 x 1343 | 风险因素档案页 |
| `figure-4-7-bp-records-page.png` | 1440 x 1254 | 血压记录页 |
| `figure-4-8-risk-prediction-page.png` | 1440 x 1100 | 风险预测页 |
| `figure-4-9-prediction-result-page.png` | 1440 x 2338 | 预测结果页 |
| `figure-4-10-prediction-history-page.png` | 1440 x 1100 | 预测历史页 |
| `figure-4-11-prediction-governance-page.png` | 1440 x 3454 | 预测结果治理页 |

## 正文使用注意

- 第4章先放模型设计图，再放 E-R 图，最后放页面截图。
- 正文中不需要放真实源码；图表和截图足以支撑“设计与实现”章节。
- 截图说明应避免写成临床诊断页面，统一使用“风险预测”“健康管理参考”“指南型健康建议”等表述。

