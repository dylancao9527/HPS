from services.recommendation_knowledge_base import RecommendationKnowledgeBase


DEFAULT_SOURCE_LABEL = (
    "建议依据：中国高血压防治指南（2024年修订版）相关健康管理建议"
)

TOPIC_PRIORITY_ORDER = ["urgent", "follow_up", "lifestyle", "prevention", "maintenance", "confidence_notice"]
SAFETY_REWRITES = {
    "确诊": "确认",
    "诊断": "评估",
    "处方": "线下医疗建议",
    "属于重度高血压": "提示血压处于较高范围",
    "属于高血压前期": "提示血压处于正常高值范围",
    "需要及时医疗干预": "建议及时就医评估",
    "必要时考虑药物干预": "由医生评估后续管理方案",
    "药物干预": "后续管理方案",
    "调整治疗方案": "评估后续管理方案",
    "治疗方案": "管理方案",
    "调整用药": "咨询医生",
    "自行用药": "自行处理",
}


class RecommendationEngine:
    def __init__(self, knowledge_base=None):
        self.knowledge_base = knowledge_base or RecommendationKnowledgeBase()

    def build(self, signal):
        matched = self.knowledge_base.match(signal)
        if not matched:
            return self._build_no_match_payload(signal)

        # 按 topic 分组，每组取 priority 最高的一条
        priority_order = {"high": 0, "medium": 1, "low": 2}
        groups = {}
        confidence_notice = None
        for entry in matched:
            topic = entry.get("topic", "follow_up")
            if topic == "confidence_notice":
                if confidence_notice is None or priority_order.get(entry.get("priority"), 99) < priority_order.get(confidence_notice.get("priority"), 99):
                    confidence_notice = entry
                continue
            if topic not in groups or priority_order.get(entry.get("priority"), 99) < priority_order.get(groups[topic].get("priority"), 99):
                groups[topic] = entry

        if not groups:
            return self._build_no_match_payload(signal)

        # 按 topic 顺序排列卡片
        ordered = sorted(groups.values(), key=lambda e: (
            TOPIC_PRIORITY_ORDER.index(e.get("topic")) if e.get("topic") in TOPIC_PRIORITY_ORDER else 99,
            e.get("id", ""),
        ))

        cards = []
        for i, entry in enumerate(ordered):
            reason = self._apply_safety_boundary(
                entry["explanation_template"],
                entry,
            )
            if i == 0 and confidence_notice:
                notice = self._apply_safety_boundary(
                    confidence_notice["explanation_template"],
                    confidence_notice,
                )
                if notice not in reason:
                    reason = f"{reason} {notice}"
            cards.append({
                "topic": entry.get("topic", "follow_up"),
                "summary": self._apply_safety_boundary(
                    entry["summary_template"],
                    entry,
                ),
                "reason": reason,
                "actions": [
                    self._apply_safety_boundary(action, entry)
                    for action in entry["action_templates"][:3]
                ],
                "source_label": DEFAULT_SOURCE_LABEL,
            })
        return cards

    def _apply_safety_boundary(self, text, entry):
        safety_boundary = entry.get("safety_boundary") or {}
        if not (
            safety_boundary.get("avoid_diagnosis")
            or safety_boundary.get("avoid_medication_adjustment")
        ):
            return text

        safe_text = text
        for unsafe, replacement in SAFETY_REWRITES.items():
            safe_text = safe_text.replace(unsafe, replacement)
        return safe_text

    def _build_no_match_payload(self, signal):
        if self._has_elevated_signal(signal):
            return [{
                "topic": "follow_up",
                "summary": "从目前记录看，血压情况仍建议继续观察。",
                "reason": "现有规则暂未命中特定提醒，但记录中仍有偏高风险或偏高天数信号。",
                "actions": [
                    "建议继续保持近几天的血压记录，便于观察后续变化。",
                    "尽量保持规律作息并减少高盐饮食。",
                    "如果后续仍持续偏高，可考虑线下咨询医生。",
                ],
                "source_label": DEFAULT_SOURCE_LABEL,
            }]
        return [{
            "topic": "maintenance",
            "summary": "从目前情况看，你的血压整体较为平稳。",
            "reason": "最近记录中没有出现需要特别提醒的变化。",
            "actions": ["建议继续保持当前记录习惯。"],
            "source_label": DEFAULT_SOURCE_LABEL,
        }]

    def _has_elevated_signal(self, signal):
        risk_level = signal.get("risk_level")
        high_bp_days = signal.get("high_bp_days") or 0
        return risk_level == "high" or high_bp_days >= 2

