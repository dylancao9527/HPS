# 《基于Prophet与LightGBM的高血压风险预测系统设计与实现》图片清单

## 生成说明

- 图表资产目录：`lunwen-doc/论文写作材料/thesis-assets/diagrams/`
- 页面截图目录：`lunwen-doc/论文写作材料/thesis-assets/screenshots/`
- 模型图保留 `.mmd`、`.png`、`.svg` 三种文件。
- 页面截图基于本地系统真实运行页面生成；普通用户使用 `demo_showcase_high`。
- 预测结果截图来自真实 `/api/predict` 调用，生成了 Prophet 血压趋势预测与 LightGBM 风险概率输出。
- 2026-05-11 大纲调整后，正文主要面向算法研究。系统页面只保留“预测流程与页面展示”一个小节，正文优先使用 7 天风险预测页面和 7 天风险预测结果页面；其他系统页面降级为附件或备用材料。
- 2026-05-11 已删除正文不再使用的治理链路图、E-R 图、风险因素档案页、血压记录页、预测历史页和预测结果治理页。

## 第4章建议图表

| 编号 | 建议图题 | 文件 | 放置位置 | 用途 |
| --- | --- | --- | --- | --- |
| 图4-1 | Prophet-LightGBM 双模型总体流程图 | `lunwen-doc/论文写作材料/thesis-assets/diagrams/figure-4-3-prophet-lightgbm-pipeline.png` | §4.1 | 作为第4章主图，展示双模型串联、风险融合、建议与记录留存 |
| 图4-2 | Prophet 血压趋势预测流程图 | `lunwen-doc/论文写作材料/thesis-assets/diagrams/figure-4-1-prophet-bp-trend-flow.png` | §4.2 | 说明血压日序列聚合、训练上下文、模型复用/重训与 7 天预测输出 |
| 图4-3 | LightGBM 风险分类输入输出图 | `lunwen-doc/论文写作材料/thesis-assets/diagrams/figure-4-2-lightgbm-risk-io.png` | §4.3 | 说明风险因素档案与 Prophet 预测期血压特征如何进入 LightGBM |
| 图4-5 | 7 天风险预测页面 | `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-8-risk-prediction-page.png` | §4.5 | 展示预测前的数据准备状态、血压数据充分性和预测入口 |
| 图4-6 | 7 天风险预测结果页面 | `lunwen-doc/论文写作材料/thesis-assets/screenshots/figure-4-9-prediction-result-page.png` | §4.5 | 展示高血压风险概率、风险等级、血压趋势图和指南型健康建议 |

## 截图尺寸核验

| 文件 | 尺寸 | 说明 |
| --- | --- | --- |
| `figure-4-8-risk-prediction-page.png` | 1440 x 1100 | 风险预测页 |
| `figure-4-9-prediction-result-page.png` | 1440 x 2338 | 预测结果页 |

## 正文使用注意

- 第4章先放模型设计图，最后只放预测入口和预测结果两张页面截图。
- 正文中不需要放真实源码，也不需要展开 E-R 图、后台治理页、历史页等系统材料。
- 截图说明应避免写成临床诊断页面，统一使用“风险预测”“健康管理参考”“指南型健康建议”等表述。

