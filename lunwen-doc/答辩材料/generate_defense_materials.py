from __future__ import annotations

import html
import os
import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "lunwen-doc" / "答辩材料"
ASSET_DIR = ROOT / "lunwen-doc" / "论文写作材料" / "thesis-assets"

PPTX_PATH = OUT_DIR / "基于Prophet与LightGBM的高血压风险预测系统-本科答辩PPT.pptx"
SCRIPT_PATH = OUT_DIR / "基于Prophet与LightGBM的高血压风险预测系统-本科答辩稿.md"

EMU_PER_IN = 914400
SLIDE_W = 13.333
SLIDE_H = 7.5
SLIDE_CX = int(SLIDE_W * EMU_PER_IN)
SLIDE_CY = int(SLIDE_H * EMU_PER_IN)


THEME = {
    "ink": "1F2937",
    "muted": "64748B",
    "subtle": "E2E8F0",
    "paper": "F8FAFC",
    "white": "FFFFFF",
    "teal": "0F766E",
    "green": "16A34A",
    "amber": "D97706",
    "red": "DC2626",
    "navy": "0F172A",
    "mint": "CCFBF1",
    "blue": "2563EB",
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def emu(value: float) -> int:
    return int(value * EMU_PER_IN)


def font_size_pt(size: float) -> int:
    return int(size * 100)


def paragraph_xml(
    text: str,
    *,
    size: float = 18,
    color: str = THEME["ink"],
    bold: bool = False,
    align: str | None = None,
) -> str:
    align_xml = f'<a:pPr algn="{align}"/>' if align else "<a:pPr/>"
    bold_xml = ' b="1"' if bold else ""
    return (
        "<a:p>"
        f"{align_xml}"
        "<a:r>"
        f'<a:rPr lang="zh-CN" sz="{font_size_pt(size)}"{bold_xml}>'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
        '<a:latin typeface="Microsoft YaHei"/>'
        '<a:ea typeface="Microsoft YaHei"/>'
        "</a:rPr>"
        f"<a:t>{esc(text)}</a:t>"
        "</a:r>"
        "</a:p>"
    )


def text_shape(
    shape_id: int,
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    lines: list[str] | str,
    *,
    size: float = 18,
    color: str = THEME["ink"],
    bold: bool = False,
    align: str | None = None,
    fill: str | None = None,
    line: str | None = None,
    margin: float = 0.08,
) -> str:
    if isinstance(lines, str):
        paragraphs = [paragraph_xml(lines, size=size, color=color, bold=bold, align=align)]
    else:
        paragraphs = [
            paragraph_xml(line_text, size=size, color=color, bold=bold, align=align)
            for line_text in lines
        ]
    fill_xml = (
        f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    )
    line_xml = (
        f'<a:ln><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>'
        if line
        else "<a:ln><a:noFill/></a:ln>"
    )
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{shape_id}" name="{esc(name)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        {fill_xml}
        {line_xml}
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" lIns="{emu(margin)}" rIns="{emu(margin)}" tIns="{emu(margin/1.4)}" bIns="{emu(margin/1.4)}"/>
        <a:lstStyle/>
        {''.join(paragraphs)}
      </p:txBody>
    </p:sp>
    """


def bullet_text_shape(
    shape_id: int,
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    bullets: list[tuple[str, str]],
    *,
    size: float = 17,
) -> str:
    paragraphs = []
    for label, body in bullets:
        paragraphs.append(
            "<a:p>"
            '<a:pPr marL="0" indent="0"/>'
            "<a:r>"
            f'<a:rPr lang="zh-CN" sz="{font_size_pt(size)}" b="1">'
            f'<a:solidFill><a:srgbClr val="{THEME["teal"]}"/></a:solidFill>'
            '<a:latin typeface="Microsoft YaHei"/><a:ea typeface="Microsoft YaHei"/>'
            "</a:rPr>"
            f"<a:t>{esc(label)}</a:t>"
            "</a:r>"
            "<a:r>"
            f'<a:rPr lang="zh-CN" sz="{font_size_pt(size)}">'
            f'<a:solidFill><a:srgbClr val="{THEME["ink"]}"/></a:solidFill>'
            '<a:latin typeface="Microsoft YaHei"/><a:ea typeface="Microsoft YaHei"/>'
            "</a:rPr>"
            f"<a:t>{esc(body)}</a:t>"
            "</a:r>"
            "</a:p>"
        )
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{shape_id}" name="{esc(name)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:noFill/>
        <a:ln><a:noFill/></a:ln>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" lIns="{emu(0.04)}" rIns="{emu(0.04)}" tIns="{emu(0.02)}" bIns="{emu(0.02)}"/>
        <a:lstStyle/>
        {''.join(paragraphs)}
      </p:txBody>
    </p:sp>
    """


def rect_shape(
    shape_id: int,
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: str,
    line: str | None = None,
    radius: bool = False,
    transparency: int | None = None,
) -> str:
    prst = "roundRect" if radius else "rect"
    alpha_xml = f'<a:alpha val="{100000 - transparency * 1000}"/>' if transparency else ""
    line_xml = (
        f'<a:ln><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>'
        if line
        else "<a:ln><a:noFill/></a:ln>"
    )
    return f"""
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{shape_id}" name="{esc(name)}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{fill}">{alpha_xml}</a:srgbClr></a:solidFill>
        {line_xml}
      </p:spPr>
      <p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody>
    </p:sp>
    """


def line_shape(shape_id: int, name: str, x: float, y: float, w: float, h: float, *, color: str, width: float = 2.0) -> str:
    return f"""
    <p:cxnSp>
      <p:nvCxnSpPr><p:cNvPr id="{shape_id}" name="{esc(name)}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
        <a:ln w="{int(width * 12700)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:ln>
      </p:spPr>
    </p:cxnSp>
    """


def image_shape(
    shape_id: int,
    name: str,
    rel_id: str,
    x: float,
    y: float,
    w: float,
    h: float,
) -> str:
    return f"""
    <p:pic>
      <p:nvPicPr><p:cNvPr id="{shape_id}" name="{esc(name)}"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>
      <p:blipFill>
        <a:blip r:embed="{rel_id}"/>
        <a:stretch><a:fillRect/></a:stretch>
      </p:blipFill>
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      </p:spPr>
    </p:pic>
    """


def card(
    shape_id: int,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    body: str,
    *,
    accent: str = THEME["teal"],
    title_size: float = 17,
    body_size: float = 12.5,
) -> str:
    return (
        rect_shape(shape_id, f"card-bg-{shape_id}", x, y, w, h, fill=THEME["white"], line=THEME["subtle"], radius=True)
        + rect_shape(shape_id + 1, f"card-accent-{shape_id}", x, y, 0.12, h, fill=accent)
        + text_shape(shape_id + 2, f"card-title-{shape_id}", x + 0.25, y + 0.18, w - 0.35, 0.34, title, size=title_size, bold=True, color=THEME["ink"], margin=0)
        + text_shape(shape_id + 3, f"card-body-{shape_id}", x + 0.25, y + 0.58, w - 0.35, h - 0.68, body, size=body_size, color=THEME["muted"], margin=0)
    )


@dataclass
class Slide:
    title: str
    subtitle: str | None = None
    parts: list[str] = field(default_factory=list)
    images: list[Path] = field(default_factory=list)
    bg: str = THEME["paper"]


def slide_header(slide: Slide, number: int, section: str = "") -> str:
    header = (
        rect_shape(2, "top-band", 0, 0, SLIDE_W, 0.18, fill=THEME["teal"])
        + text_shape(3, "slide-title", 0.55, 0.36, 9.4, 0.52, slide.title, size=26, bold=True, color=THEME["navy"], margin=0)
        + text_shape(4, "page-no", 12.0, 0.38, 0.75, 0.3, f"{number:02d}", size=12, color=THEME["muted"], align="right", margin=0)
    )
    if slide.subtitle:
        header += text_shape(5, "slide-subtitle", 0.56, 0.86, 9.8, 0.32, slide.subtitle, size=13, color=THEME["muted"], margin=0)
    if section:
        header += text_shape(6, "section", 10.5, 0.38, 1.6, 0.3, section, size=10.5, color=THEME["teal"], align="right", margin=0)
    return header


def title_slide() -> Slide:
    s = Slide(title="", bg=THEME["navy"])
    s.parts.extend(
        [
            rect_shape(2, "accent-left", 0, 0, 0.22, SLIDE_H, fill=THEME["teal"]),
            rect_shape(3, "accent-bottom", 0.22, 6.95, SLIDE_W - 0.22, 0.55, fill=THEME["teal"]),
            text_shape(4, "main-title", 0.9, 1.15, 9.8, 1.35, "基于 Prophet 与 LightGBM 的\n高血压风险预测系统设计与实现", size=35, bold=True, color=THEME["white"], margin=0.02),
            text_shape(5, "main-subtitle", 0.95, 2.75, 7.8, 0.5, "本科毕业设计答辩 | 重点：双模型算法与实验结论", size=17, color="CBD5E1", margin=0),
            card(6, 0.95, 4.05, 3.1, 1.2, "研究对象", "家庭血压记录与个人风险因素", accent=THEME["teal"]),
            card(10, 4.35, 4.05, 3.1, 1.2, "核心方法", "Prophet 趋势预测 + LightGBM 风险分类", accent=THEME["green"]),
            card(14, 7.75, 4.05, 3.1, 1.2, "应用边界", "健康管理辅助提醒，不替代临床诊断", accent=THEME["amber"]),
            text_shape(18, "footer", 0.95, 6.96, 6.2, 0.28, "汇报时长：5-10 分钟", size=12, color=THEME["white"], margin=0),
        ]
    )
    return s


def make_slides() -> list[Slide]:
    slides: list[Slide] = [title_slide()]

    s = Slide(
        "研究背景与问题",
        "连续血压记录需要从“保存查询”转向“趋势理解与风险提醒”。",
    )
    s.parts.extend(
        [
            slide_header(s, 2, "问题"),
            card(10, 0.65, 1.45, 3.6, 1.35, "现实问题", "家庭血压计沉淀了大量记录，但多数系统只完成录入、查询和历史展示。", accent=THEME["teal"]),
            card(14, 4.65, 1.45, 3.6, 1.35, "模型缺口", "只看最近一次血压会丢失趋势，只画趋势曲线又难以转化为风险结论。", accent=THEME["amber"]),
            card(18, 8.65, 1.45, 3.6, 1.35, "本文目标", "把短期血压走势、个人风险因素和结果解释连接为一条预测流程。", accent=THEME["green"]),
            text_shape(22, "big-question", 1.0, 3.65, 11.2, 0.72, "核心问题：未来 7 天血压趋势如何参与高血压风险判断？", size=25, bold=True, color=THEME["navy"], align="center", fill="ECFDF5", line="99F6E4"),
            bullet_text_shape(
                23,
                "points",
                1.1,
                4.75,
                10.8,
                1.15,
                [
                    ("思路一：", "用 Prophet 从个人血压序列中提取短期趋势。"),
                    ("思路二：", "用 LightGBM 将预测期血压均值和风险因素合并分类。"),
                    ("思路三：", "用趋势融合对概率做小幅、可追溯修正。"),
                ],
                size=15,
            ),
        ]
    )
    slides.append(s)

    s = Slide("系统总体架构", "系统采用前后端分离，算法链路集中在后端预测模块。")
    s.parts.extend(
        [
            slide_header(s, 3, "架构"),
            rect_shape(10, "flow-bg", 0.7, 1.38, 11.9, 3.2, fill=THEME["white"], line=THEME["subtle"], radius=True),
            text_shape(11, "f1", 1.0, 2.25, 1.7, 0.55, "用户端\nReact", size=17, bold=True, color=THEME["navy"], align="center", fill="E0F2FE", line="BAE6FD"),
            line_shape(12, "l1", 2.82, 2.52, 1.05, 0, color=THEME["teal"], width=2.2),
            text_shape(13, "f2", 3.95, 2.25, 1.8, 0.55, "Flask API\n业务服务", size=17, bold=True, color=THEME["navy"], align="center", fill="ECFDF5", line="A7F3D0"),
            line_shape(14, "l2", 5.92, 2.52, 0.9, 0, color=THEME["teal"], width=2.2),
            text_shape(15, "f3", 6.9, 1.72, 2.0, 0.62, "Prophet\n7天趋势", size=17, bold=True, color=THEME["navy"], align="center", fill="FEF3C7", line="FDE68A"),
            text_shape(16, "f4", 6.9, 3.0, 2.0, 0.62, "LightGBM\n风险分类", size=17, bold=True, color=THEME["navy"], align="center", fill="DCFCE7", line="BBF7D0"),
            line_shape(17, "l3", 8.98, 2.52, 0.9, 0, color=THEME["teal"], width=2.2),
            text_shape(18, "f5", 9.95, 2.25, 1.9, 0.55, "结果展示\n建议生成", size=17, bold=True, color=THEME["navy"], align="center", fill="F1F5F9", line="CBD5E1"),
            card(19, 1.05, 5.0, 3.3, 1.12, "数据来源", "血压记录、个人档案、公开训练数据集", accent=THEME["blue"]),
            card(23, 4.85, 5.0, 3.3, 1.12, "模型产物", "LightGBM txt 模型；用户级 Prophet 模型持久化", accent=THEME["green"]),
            card(27, 8.65, 5.0, 3.3, 1.12, "输出内容", "风险概率、风险等级、未来7天曲线、健康建议", accent=THEME["teal"]),
        ]
    )
    slides.append(s)

    s = Slide("Prophet：7 天血压趋势预测", "把不规则记录整理为日均序列，再生成未来 7 天收缩压和舒张压趋势。")
    s.images.append(ASSET_DIR / "diagrams" / "figure-4-1-prophet-bp-trend-flow.png")
    s.parts.extend(
        [
            slide_header(s, 4, "Prophet"),
            image_shape(10, "prophet-flow", "rIdImg1", 0.6, 1.35, 7.3, 3.55),
            card(20, 8.25, 1.35, 4.3, 1.05, "输入", "用户历史血压记录按自然日聚合：收缩压、舒张压日均值", accent=THEME["teal"]),
            card(24, 8.25, 2.65, 4.3, 1.05, "预测", "默认使用最近 90 天窗口，生成未来 7 天预测点", accent=THEME["green"]),
            card(28, 8.25, 3.95, 4.3, 1.05, "输出", "预测期均值、峰值、高血压天数、趋势方向与置信度说明", accent=THEME["amber"]),
            text_shape(32, "formula", 1.1, 5.65, 11.0, 0.48, "SBP_future = 1/7 × Σ SBP̂(t+k)，DBP_future = 1/7 × Σ DBP̂(t+k)", size=18, bold=True, color=THEME["navy"], align="center", fill="ECFDF5", line="99F6E4"),
        ]
    )
    slides.append(s)

    s = Slide("LightGBM：风险概率分类", "将预测期血压特征和个人风险因素合并，输出可分级的风险概率。")
    s.images.append(ASSET_DIR / "diagrams" / "figure-4-2-lightgbm-risk-io.png")
    s.parts.extend(
        [
            slide_header(s, 5, "LightGBM"),
            image_shape(10, "lgbm-io", "rIdImg1", 0.7, 1.28, 6.2, 3.72),
            card(20, 7.35, 1.35, 4.85, 1.08, "12 个核心特征", "性别、年龄、吸烟、用药、糖尿病、胆固醇、BMI、心率、血糖等。", accent=THEME["teal"]),
            card(24, 7.35, 2.72, 4.85, 1.08, "动态血压输入", "sysBP 与 diaBP 在系统预测时来自 Prophet 的未来 7 天均值。", accent=THEME["green"]),
            card(28, 7.35, 4.09, 4.85, 1.08, "概率输出", "LightGBM 分数经 Sigmoid 转为 p_raw，再映射低/中/高风险。", accent=THEME["amber"]),
            text_shape(32, "threshold", 1.1, 5.75, 11.0, 0.5, "分类策略：健康提醒场景采用召回优先，少量误报比漏掉潜在高风险更可接受。", size=17, bold=True, color=THEME["navy"], align="center", fill="F8FAFC", line="CBD5E1"),
        ]
    )
    slides.append(s)

    s = Slide("双模型衔接与趋势融合", "Prophet 不直接给风险结论，LightGBM 也不脱离近期趋势单独判断。")
    s.images.append(ASSET_DIR / "diagrams" / "figure-4-4-dual-model-algorithm.png")
    s.parts.extend(
        [
            slide_header(s, 6, "双模型"),
            image_shape(10, "dual-model", "rIdImg1", 0.7, 1.25, 7.5, 3.87),
            card(20, 8.55, 1.3, 3.95, 1.05, "特征衔接", "未来7天 SBP/DBP 均值进入 LightGBM 的 sysBP/diaBP。", accent=THEME["teal"]),
            card(24, 8.55, 2.62, 3.95, 1.05, "趋势信号", "高血压天数、峰值、上升趋势、稳定低趋势、用药未控制。", accent=THEME["green"]),
            card(28, 8.55, 3.94, 3.95, 1.05, "约束修正", "只在原始概率基础上微调，保留模型原始判断。", accent=THEME["amber"]),
            text_shape(32, "fusion", 1.1, 5.68, 11.0, 0.5, "p_fused = clip(p_raw + Δ_trend + Δ_med, 0.01, 0.99)", size=20, bold=True, color=THEME["navy"], align="center", fill="ECFDF5", line="99F6E4"),
        ]
    )
    slides.append(s)

    s = Slide("LightGBM 实验结果", "生产方案选择 recall-min85，不只看 AUC，而是服务于健康风险提醒。")
    s.parts.extend(
        [
            slide_header(s, 7, "实验"),
            text_shape(10, "dataset", 0.75, 1.15, 11.8, 0.36, "数据集：Hypertension-risk-model-main.csv，共 4240 条样本，正样本比例 31.1%，测试集 848 条。", size=14.5, color=THEME["muted"], margin=0),
            card(11, 0.85, 1.8, 2.15, 1.25, "AUC", "0.9498", accent=THEME["blue"], title_size=15, body_size=31),
            card(15, 3.25, 1.8, 2.15, 1.25, "Precision", "0.8246", accent=THEME["teal"], title_size=15, body_size=31),
            card(19, 5.65, 1.8, 2.15, 1.25, "Recall", "0.8935", accent=THEME["green"], title_size=15, body_size=31),
            card(23, 8.05, 1.8, 2.15, 1.25, "F1", "0.8577", accent=THEME["amber"], title_size=15, body_size=31),
            card(27, 10.45, 1.8, 2.15, 1.25, "PR-AUC", "0.8706", accent=THEME["red"], title_size=15, body_size=31),
            rect_shape(31, "matrix-bg", 0.85, 3.78, 5.8, 1.95, fill=THEME["white"], line=THEME["subtle"], radius=True),
            text_shape(32, "matrix-title", 1.08, 4.02, 5.25, 0.3, "测试集混淆矩阵（recall-min85）", size=15, bold=True, color=THEME["navy"], margin=0),
            text_shape(33, "matrix-values", 1.08, 4.58, 5.25, 0.65, "TP 235   FN 28\nFP 50     TN 535", size=19, bold=True, color=THEME["ink"], align="center", margin=0),
            rect_shape(34, "conclusion-bg", 7.15, 3.78, 5.0, 1.95, fill="ECFDF5", line="99F6E4", radius=True),
            text_shape(35, "conclusion-title", 7.42, 4.02, 4.45, 0.3, "选择理由", size=15, bold=True, color=THEME["navy"], margin=0),
            text_shape(36, "conclusion-body", 7.42, 4.55, 4.45, 0.72, "漏判率降至 10.65%，比 baseline 多识别 31 个正类样本；误报率 8.55%，在辅助提醒场景可接受。", size=13.2, color=THEME["ink"], margin=0),
        ]
    )
    slides.append(s)

    s = Slide("特征重要性：血压特征是主信号", "实验结果支撑 Prophet 预测期血压特征接入 LightGBM。")
    s.images.append(ASSET_DIR / "diagrams" / "figure-5-3-lightgbm-feature-importance.png")
    s.parts.extend(
        [
            slide_header(s, 8, "实验"),
            image_shape(10, "importance", "rIdImg1", 0.6, 1.25, 6.8, 4.55),
            card(20, 7.85, 1.35, 4.65, 1.12, "sysBP", "gain 占比 74.2%", accent=THEME["teal"], title_size=17, body_size=24),
            card(24, 7.85, 2.75, 4.65, 1.12, "diaBP", "gain 占比 19.5%", accent=THEME["green"], title_size=17, body_size=24),
            card(28, 7.85, 4.15, 4.65, 1.12, "合计", "血压特征 93.7%", accent=THEME["amber"], title_size=17, body_size=24),
            text_shape(32, "interpretation", 1.0, 6.05, 11.6, 0.45, "结论：模型主要依据血压水平做判断，BMI、年龄、心率等因素起补充作用。", size=17, bold=True, color=THEME["navy"], align="center", fill="F8FAFC", line="CBD5E1"),
        ]
    )
    slides.append(s)

    s = Slide("Prophet 回测与趋势融合结论", "趋势预测用于构造动态特征，融合策略用于提升结果解释性。")
    s.parts.extend(
        [
            slide_header(s, 9, "实验"),
            rect_shape(10, "mae-bg", 0.75, 1.25, 5.95, 4.7, fill=THEME["white"], line=THEME["subtle"], radius=True),
            text_shape(11, "mae-title", 1.05, 1.55, 5.3, 0.35, "Prophet 7 天回测", size=18, bold=True, color=THEME["navy"], margin=0),
            text_shape(12, "mae-big", 1.05, 2.15, 5.3, 0.85, "3-7 mmHg", size=34, bold=True, color=THEME["teal"], align="center", margin=0),
            text_shape(13, "mae-desc", 1.05, 3.22, 5.3, 0.75, "稳定血压 profile 在历史数据达到 30 天以上时，7 天收缩压 MAE 通常处于该范围。", size=15, color=THEME["ink"], align="center", margin=0),
            text_shape(14, "volatile", 1.05, 4.52, 5.3, 0.52, "高波动 profile 的 MAE 约 10-13 mmHg，因此系统降低置信度。", size=13.5, color=THEME["muted"], align="center", margin=0),
            rect_shape(20, "fusion-bg", 7.25, 1.25, 5.55, 4.7, fill=THEME["white"], line=THEME["subtle"], radius=True),
            text_shape(21, "fusion-title", 7.55, 1.55, 4.95, 0.35, "趋势融合场景评价", size=18, bold=True, color=THEME["navy"], margin=0),
            text_shape(22, "fusion-big", 7.55, 2.12, 4.95, 0.85, "24 次 / 2 次上调", size=29, bold=True, color=THEME["green"], align="center", margin=0),
            text_shape(23, "fusion-desc", 7.55, 3.2, 4.95, 0.75, "总调整量 0 到 0.12，平均绝对调整量 0.0502。", size=15, color=THEME["ink"], align="center", margin=0),
            text_shape(24, "fusion-note", 7.55, 4.52, 4.95, 0.52, "设计意图是微调而非颠覆 LightGBM 原始概率。", size=13.5, color=THEME["muted"], align="center", margin=0),
            text_shape(30, "overall", 1.0, 6.18, 11.6, 0.42, "实验结论：双模型既利用了短期血压趋势，又保持了分类模型的稳定判断。", size=17, bold=True, color=THEME["navy"], align="center", fill="ECFDF5", line="99F6E4"),
        ]
    )
    slides.append(s)

    s = Slide("总结与展望", "本系统定位为健康管理辅助参考，不输出临床诊断或治疗方案。")
    s.parts.extend(
        [
            slide_header(s, 10, "总结"),
            card(10, 0.85, 1.35, 3.65, 1.38, "完成工作", "实现普通用户血压记录、风险因素维护、7天预测、历史记录与建议展示。", accent=THEME["teal"]),
            card(14, 4.85, 1.35, 3.65, 1.38, "核心创新点", "Prophet 预测期血压特征接入 LightGBM，并加入可追溯趋势融合。", accent=THEME["green"]),
            card(18, 8.85, 1.35, 3.65, 1.38, "实验支撑", "召回优先模型减少漏判；血压特征 gain 占比 93.7%；融合幅度受控。", accent=THEME["amber"]),
            rect_shape(22, "future-bg", 1.1, 3.65, 11.1, 1.55, fill=THEME["white"], line=THEME["subtle"], radius=True),
            text_shape(23, "future-title", 1.45, 3.95, 10.4, 0.34, "后续展望", size=18, bold=True, color=THEME["navy"], margin=0),
            bullet_text_shape(
                24,
                "future-points",
                1.45,
                4.45,
                10.4,
                0.6,
                [
                    ("数据维度：", "纳入盐摄入、睡眠、运动、饮食等生活方式变量。"),
                    ("模型验证：", "引入更多来源数据，评估泛化能力、概率校准和阈值稳定性。"),
                ],
                size=13.8,
            ),
            text_shape(30, "thanks", 0.9, 6.05, 11.7, 0.55, "谢谢各位老师，欢迎批评指正", size=25, bold=True, color=THEME["white"], align="center", fill=THEME["teal"], line=THEME["teal"]),
        ]
    )
    slides.append(s)

    return slides


def build_slide_xml(slide: Slide, idx: int) -> str:
    parts = "\n".join(slide.parts)
    bg = f"""
      <p:bg>
        <p:bgPr>
          <a:solidFill><a:srgbClr val="{slide.bg}"/></a:solidFill>
          <a:effectLst/>
        </p:bgPr>
      </p:bg>
    """
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    {bg}
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{SLIDE_CX}" cy="{SLIDE_CY}"/><a:chOff x="0" y="0"/><a:chExt cx="{SLIDE_CX}" cy="{SLIDE_CY}"/></a:xfrm></p:grpSpPr>
      {parts}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>
"""


def presentation_xml(slide_count: int) -> str:
    slide_ids = "\n".join(
        f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldSz cx="{SLIDE_CX}" cy="{SLIDE_CY}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:sldIdLst>
    {slide_ids}
  </p:sldIdLst>
</p:presentation>
"""


def presentation_rels(slide_count: int) -> str:
    rels = [
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, slide_count + 1)
    ]
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
""" + "\n".join(rels) + "\n</Relationships>\n"


def root_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def content_types(slide_count: int, media_count: int) -> str:
    overrides = [
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
    ]
    overrides.extend(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
""" + "\n".join(f"  {item}" for item in overrides) + "\n</Types>\n"


def core_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>基于Prophet与LightGBM的高血压风险预测系统-本科答辩PPT</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
</cp:coreProperties>
"""


def app_xml(slide_count: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex OpenXML Generator</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
  <Slides>{slide_count}</Slides>
</Properties>
"""


def slide_rels(slide: Slide) -> str:
    if not slide.images:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""
    rels = []
    for image_index, _ in enumerate(slide.images, start=1):
        rels.append(
            f'<Relationship Id="rIdImg{image_index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/slide{image_index_placeholder(slide)}_{image_index}.png"/>'
        )
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
""" + "\n".join(rels) + "\n</Relationships>\n"


def image_index_placeholder(slide: Slide) -> str:
    # Replaced by build_pptx where slide index is known.
    raise RuntimeError("placeholder")


def build_slide_rels(slide: Slide, slide_no: int) -> str:
    if not slide.images:
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""
    rels = []
    for image_index, _ in enumerate(slide.images, start=1):
        rels.append(
            f'<Relationship Id="rIdImg{image_index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/slide{slide_no}_{image_index}.png"/>'
        )
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
""" + "\n".join(rels) + "\n</Relationships>\n"


def build_pptx(slides: list[Slide]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if PPTX_PATH.exists():
        PPTX_PATH.unlink()
    with zipfile.ZipFile(PPTX_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types(len(slides), sum(len(s.images) for s in slides)))
        z.writestr("_rels/.rels", root_rels())
        z.writestr("docProps/core.xml", core_xml())
        z.writestr("docProps/app.xml", app_xml(len(slides)))
        z.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slides)))
        for idx, slide in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{idx}.xml", build_slide_xml(slide, idx))
            z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", build_slide_rels(slide, idx))
            for image_index, image_path in enumerate(slide.images, start=1):
                z.write(image_path, f"ppt/media/slide{idx}_{image_index}.png")


SCRIPT = """# 基于Prophet与LightGBM的高血压风险预测系统设计与实现

## 本科答辩稿（约 5-10 分钟）

### 第 1 页：题目页
各位老师好，我的毕业设计题目是《基于 Prophet 与 LightGBM 的高血压风险预测系统设计与实现》。本课题面向家庭血压记录和健康管理辅助场景，重点不是单纯做一个信息管理系统，而是围绕 Prophet 和 LightGBM 的双模型预测流程，完成短期血压趋势预测、风险概率分类和结果解释。

### 第 2 页：研究背景与问题
高血压管理需要连续监测，但很多系统仍停留在记录保存和查询层面。普通用户看到一串血压数值后，未必能判断近期波动是否已经需要关注。如果只使用最近一次血压，连续记录里的趋势会被忽略；如果只展示趋势曲线，又很难直接转化成风险提醒。因此本文要解决的问题是：如何把未来 7 天血压走势纳入高血压风险判断，并把结果转化为用户能理解的概率、等级和建议。

### 第 3 页：系统总体架构
系统采用前后端分离架构。前端使用 React 和 TypeScript，负责用户注册登录、血压记录、风险因素维护、预测入口和结果展示。后端使用 Flask、SQLAlchemy 和 MySQL，核心预测链路集中在预测模块中。一次预测会先读取用户档案和血压记录，再由 Prophet 生成未来 7 天趋势，随后 LightGBM 输出原始风险概率，最后进行趋势融合和建议生成。系统输出的是健康管理辅助提醒，不替代临床诊断。

### 第 4 页：Prophet 趋势预测
Prophet 在系统中承担时间序列预测任务。用户录入的血压记录会先按自然日聚合，同一天多条记录分别计算收缩压和舒张压均值。随后系统默认截取最近 90 天日均序列，预测未来 7 天收缩压和舒张压。这里 Prophet 的结果不是直接作为高血压结论，而是进一步提取预测期均值、峰值、高血压天数和趋势方向。其中未来 7 天收缩压均值和舒张压均值会作为 LightGBM 的动态血压输入。

### 第 5 页：LightGBM 风险分类
LightGBM 适合处理结构化表格特征，因此本文用它完成高血压风险分类。输入特征包括性别、年龄、吸烟情况、是否用药、糖尿病、总胆固醇、BMI、心率、血糖等个人风险因素，也包括 Prophet 得到的未来 7 天收缩压和舒张压均值。LightGBM 输出的是原始风险概率，再映射为低风险、中风险和高风险。因为系统定位是健康提醒，实验中采用召回优先策略，尽量减少潜在高风险样本被漏掉的情况。

### 第 6 页：双模型衔接与趋势融合
本文的核心不是两个模型简单并列，而是串联使用。Prophet 把历史血压序列转换为未来 7 天的动态血压特征，LightGBM 再结合个人风险因素输出原始概率。随后趋势融合模块会提取高血压天数、血压峰值、上升趋势、稳定低趋势和服药但未控制等信号，对原始概率做小幅修正。融合公式可以概括为 fused probability 等于 raw probability 加趋势调整和用药调整，再限制到合理概率范围内。这样做的目的不是推翻 LightGBM 判断，而是让最终结果能解释近期血压走势带来的影响。

### 第 7 页：LightGBM 实验结果
实验使用 Hypertension-risk-model-main.csv 数据集，共 4240 条样本，正样本比例为 31.1%。调参后生产模型采用 recall-min85 方案，AUC 为 0.9498，PR-AUC 为 0.8706，Precision 为 0.8246，Recall 为 0.8935，F1 为 0.8577。在测试集 848 条样本中，该方案识别出 235 个正类样本，仅漏判 28 个，漏判率为 10.65%。与 baseline 相比，它多识别 31 个正类样本，代价是误报略有增加。对健康管理辅助提醒来说，这种取舍是合理的。

### 第 8 页：特征重要性分析
LightGBM 的特征重要性结果显示，收缩压 sysBP 的 gain 占比为 74.2%，舒张压 diaBP 的 gain 占比为 19.5%，两者合计达到 93.7%。这说明模型判断风险时主要依据血压相关特征，BMI、年龄和心率等特征起补充作用。这个结果支撑了本文的关键设计：在真实系统预测时，不直接使用最近一次血压，而是把 Prophet 预测得到的未来 7 天血压均值接入 LightGBM。

### 第 9 页：Prophet 回测与趋势融合结论
Prophet 回测使用五类模拟血压 profile。结果显示，当历史记录达到 30 天以上时，稳定血压序列的 7 天收缩压 MAE 大约处于 3 到 7 mmHg 范围；高波动 profile 的 MAE 约为 10 到 13 mmHg，因此系统对高波动数据降低置信度是合理的。趋势融合实验构造了 8 个典型场景和 24 次概率模拟，其中只有 2 次发生风险等级上调，总调整量范围为 0 到 0.12，平均绝对调整量为 0.0502。这说明融合策略是受约束的微调，而不是大幅改变 LightGBM 的原始判断。

### 第 10 页：总结与展望
综上，本文完成了一个面向普通用户的高血压风险预测辅助系统。算法上，Prophet 用于提取未来 7 天血压趋势，LightGBM 用于融合预测期血压特征和个人风险因素，趋势融合模块用于增强结果解释性。实验结果表明，召回优先方案更适合健康提醒场景，血压特征在模型判断中占主要权重，Prophet 回测和趋势融合也验证了双模型流程的可行性。后续可以继续扩展盐摄入、睡眠、运动等生活方式字段，并引入更多来源的数据验证模型泛化能力和阈值稳定性。我的汇报到此结束，谢谢各位老师。
"""


def write_script() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPT_PATH.write_text(SCRIPT, encoding="utf-8")


def main() -> None:
    slides = make_slides()
    build_pptx(slides)
    write_script()
    print(PPTX_PATH)
    print(SCRIPT_PATH)


if __name__ == "__main__":
    main()
