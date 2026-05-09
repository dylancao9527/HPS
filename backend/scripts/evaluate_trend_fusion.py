"""
==============================================================================
趋势融合效果评价脚本
==============================================================================
职责：
  - 构造不同血压预测场景（正常、偏高、高血压、趋势上升、波动）
  - 对每个场景模拟 LightGBM 原始概率 + Prophet 趋势预测
  - 对比有/无趋势融合时的风险概率差异
  - 量化 trend_policy 调整系数的实际影响
  - 将结果输出到 docs/reports/trend_fusion_report.md

运行方式：
  cd backend && uv run python scripts/evaluate_trend_fusion.py
==============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Ensure backend is on path for imports
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from prediction.domain.trend_policy import fuse_risk_with_trend, summarize_forecast_trend

DOCS_DIR = Path(__file__).resolve().parents[2] / "docs" / "reports"
REPORT_PATH = DOCS_DIR / "trend_fusion_report.md"


# ---------------------------------------------------------------------------
# 1. Test scenario definitions
# ---------------------------------------------------------------------------

def _make_forecast(sys_values: list[float], dia_values: list[float]) -> list[dict]:
    """Build a forecast list from systolic/diastolic arrays."""
    return [
        {"day": i + 1, "systolic": s, "diastolic": d}
        for i, (s, d) in enumerate(zip(sys_values, dia_values))
    ]


SCENARIOS = [
    # --- Normal/Low BP scenarios ---
    {
        "name": "正常稳定低血压",
        "description": "收缩压 ~115，舒张压 ~75，稳定无趋势",
        "forecast": _make_forecast(
            [114, 116, 113, 117, 115, 114, 116],
            [74, 76, 73, 77, 75, 74, 76],
        ),
        "raw_probabilities": [0.10, 0.20, 0.35],
        "bp_meds": None,
    },
    # --- Elevated BP scenarios ---
    {
        "name": "偏高血压稳定",
        "description": "收缩压 ~135，舒张压 ~87，稳定无明显趋势",
        "forecast": _make_forecast(
            [133, 136, 134, 137, 135, 133, 136],
            [86, 88, 85, 89, 87, 86, 88],
        ),
        "raw_probabilities": [0.30, 0.45, 0.60],
        "bp_meds": None,
    },
    # --- High BP scenarios ---
    {
        "name": "高血压稳定",
        "description": "收缩压 ~155，舒张压 ~95，持续高于阈值",
        "forecast": _make_forecast(
            [153, 157, 154, 158, 155, 153, 156],
            [94, 96, 93, 97, 95, 94, 96],
        ),
        "raw_probabilities": [0.50, 0.65, 0.80],
        "bp_meds": None,
    },
    # --- Upward trend ---
    {
        "name": "上升趋势",
        "description": "收缩压从 125 上升到 145，舒张压从 80 上升到 90",
        "forecast": _make_forecast(
            [125, 128, 131, 134, 137, 141, 145],
            [80, 81, 83, 84, 86, 88, 90],
        ),
        "raw_probabilities": [0.30, 0.45, 0.60],
        "bp_meds": None,
    },
    # --- Downward trend ---
    {
        "name": "下降趋势",
        "description": "收缩压从 145 下降到 120，舒张压从 90 下降到 78",
        "forecast": _make_forecast(
            [145, 141, 137, 133, 128, 124, 120],
            [90, 88, 86, 84, 82, 80, 78],
        ),
        "raw_probabilities": [0.30, 0.45, 0.60],
        "bp_meds": None,
    },
    # --- Extreme peak ---
    {
        "name": "含极端峰值",
        "description": "大多数天正常，但有 1 天收缩压冲到 155",
        "forecast": _make_forecast(
            [122, 125, 155, 120, 123, 121, 124],
            [78, 80, 96, 77, 79, 78, 80],
        ),
        "raw_probabilities": [0.25, 0.40, 0.55],
        "bp_meds": None,
    },
    # --- High BP + taking meds (uncontrolled) ---
    {
        "name": "服药但血压未控制",
        "description": "正在服用降压药，但收缩压仍 >150",
        "forecast": _make_forecast(
            [152, 155, 148, 156, 153, 150, 154],
            [94, 96, 92, 97, 95, 93, 95],
        ),
        "raw_probabilities": [0.50, 0.65, 0.80],
        "bp_meds": 1,
    },
    # --- High volatility ---
    {
        "name": "高波动",
        "description": "血压日间变化大，均值正常但波动剧烈",
        "forecast": _make_forecast(
            [110, 145, 115, 150, 108, 148, 112],
            [70, 95, 72, 98, 68, 96, 71],
        ),
        "raw_probabilities": [0.30, 0.45, 0.60],
        "bp_meds": None,
    },
]


# ---------------------------------------------------------------------------
# 2. Run evaluation
# ---------------------------------------------------------------------------

def evaluate_scenario(scenario: dict) -> list[dict]:
    """Evaluate a scenario at different raw probability levels."""
    results = []
    for raw_prob in scenario["raw_probabilities"]:
        fusion = fuse_risk_with_trend(
            raw_prob,
            scenario["forecast"],
            bp_meds=scenario.get("bp_meds"),
        )
        trend = fusion["trend_summary"]
        results.append({
            "scenario": scenario["name"],
            "description": scenario["description"],
            "raw_probability": raw_prob,
            "fused_probability": fusion["fused_probability"],
            "total_adjustment": fusion["adjustment"],
            "trend_adjustment": fusion["trend_adjustment"],
            "medication_adjustment": fusion["medication_adjustment"],
            "reasons": fusion["reasons"],
            "avg_sys": trend["avg_sys"],
            "avg_dia": trend["avg_dia"],
            "max_sys": trend["max_sys"],
            "max_dia": trend["max_dia"],
            "sys_slope": trend["sys_slope"],
            "dia_slope": trend["dia_slope"],
            "high_bp_days": trend["high_bp_days"],
            "elevated_bp_days": trend["elevated_bp_days"],
            "bp_meds": scenario.get("bp_meds"),
        })
    return results


def run_evaluation() -> list[dict]:
    """Run trend fusion evaluation across all scenarios."""
    all_results = []
    for scenario in SCENARIOS:
        print(f"  评价场景: {scenario['name']} ...", flush=True)
        all_results.extend(evaluate_scenario(scenario))
    return all_results


# ---------------------------------------------------------------------------
# 3. Report generation
# ---------------------------------------------------------------------------

def _risk_level(prob: float) -> str:
    if prob < 0.3:
        return "低"
    elif prob < 0.6:
        return "中"
    else:
        return "高"


def generate_report(results: list[dict]) -> str:
    """Generate a markdown report from evaluation results."""
    lines = [
        "# 趋势融合效果评价报告",
        "",
        "## 一、评价方法",
        "",
        "构造 8 个典型血压预测场景，对每个场景模拟 3 个不同的 LightGBM 原始概率水平"
        "（低/中/高），对比趋势融合前后的风险概率和风险等级变化。",
        "",
        "趋势融合逻辑来自 `prediction/domain/trend_policy.py`，融合信号包括：",
        "- 高血压天数（high_bp_days）：7 天中收缩压 ≥140 或舒张压 ≥90 的天数",
        "- 血压峰值（peak_bp）：最大收缩压 ≥150 或最大舒张压 ≥95",
        "- 上升趋势（upward_trend）：收缩压 7 天斜率 ≥5 或舒张压斜率 ≥3",
        "- 稳定低趋势（stable_low_trend）：均值正常且无上升趋势时向下修正",
        "- 药物未控制（meds_uncontrolled_high_bp）：服药但仍高血压时附加修正",
        "",
        "## 二、场景说明",
        "",
        "| 场景 | 说明 | 收缩压均值 | 舒张压均值 | 高血压天数 |",
        "|---|---|---|---|---|",
    ]

    seen_scenarios = set()
    for r in results:
        if r["scenario"] not in seen_scenarios:
            seen_scenarios.add(r["scenario"])
            lines.append(
                f"| {r['scenario']} | {r['description']} "
                f"| {r['avg_sys']:.1f} | {r['avg_dia']:.1f} "
                f"| {r['high_bp_days']} |"
            )

    lines.extend([
        "",
        "## 三、融合效果对比",
        "",
        "| 场景 | 原始概率 | 融合后概率 | 调整量 | 风险等级变化 | 触发信号 |",
        "|---|---|---|---|---|---|",
    ])

    level_changes = {"unchanged": 0, "upgraded": 0, "downgraded": 0}

    for r in results:
        raw_level = _risk_level(r["raw_probability"])
        fused_level = _risk_level(r["fused_probability"])
        if raw_level == fused_level:
            level_change = "→ 不变"
            level_changes["unchanged"] += 1
        elif r["fused_probability"] > r["raw_probability"]:
            level_change = f"{raw_level} → {fused_level} ↑"
            level_changes["upgraded"] += 1
        else:
            level_change = f"{raw_level} → {fused_level} ↓"
            level_changes["downgraded"] += 1

        reasons_str = ", ".join(r["reasons"]) if r["reasons"] else "—"
        adj = r["total_adjustment"]
        adj_str = f"+{adj:.4f}" if adj >= 0 else f"{adj:.4f}"
        lines.append(
            f"| {r['scenario']} | {r['raw_probability']:.2f} "
            f"| {r['fused_probability']:.4f} | {adj_str} "
            f"| {level_change} | {reasons_str} |"
        )

    lines.extend([
        "",
        "## 四、调整量分布",
        "",
    ])

    adjustments = [r["total_adjustment"] for r in results]
    trend_adj = [r["trend_adjustment"] for r in results]
    med_adj = [r["medication_adjustment"] for r in results]
    lines.extend([
        f"- 总调整量范围：[{min(adjustments):+.4f}, {max(adjustments):+.4f}]",
        f"- 趋势调整量范围：[{min(trend_adj):+.4f}, {max(trend_adj):+.4f}]",
        f"- 药物调整量范围：[{min(med_adj):+.4f}, {max(med_adj):+.4f}]",
        f"- 平均绝对调整量：{np.mean(np.abs(adjustments)):.4f}",
        "",
    ])

    lines.extend([
        "## 五、风险等级影响统计",
        "",
        f"- 风险等级不变：{level_changes['unchanged']} 次",
        f"- 风险等级上调：{level_changes['upgraded']} 次",
        f"- 风险等级下调：{level_changes['downgraded']} 次",
        f"- 总评价次数：{len(results)} 次",
        "",
    ])

    lines.extend([
        "## 六、结论",
        "",
        "- 趋势融合对**稳定低血压**场景产生向下修正（stable_low_trend），避免了对正常血压用户的过度预警。",
        "- 对**高血压天数 > 0** 的场景，融合向上修正，最大调整幅度受 high_bp_ratio × 0.08 约束。",
        "- **上升趋势**信号（upward_trend）为上升中的血压提供了额外 +0.02 的警示。",
        "- **药物未控制**场景（服药 + 高血压未控制）叠加 +0.02 修正。",
        "- 趋势融合的调整量级别在 [-0.02, +0.12] 区间内，设计意图是**微调而非颠覆** LightGBM 的基础概率判断。",
        "",
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4. Main
# ---------------------------------------------------------------------------

def main():
    print("趋势融合效果评价")
    print("=" * 50)
    print()

    results = run_evaluation()

    print()
    print("生成报告...")
    report = generate_report(results)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"报告已保存至: {REPORT_PATH}")


if __name__ == "__main__":
    main()
