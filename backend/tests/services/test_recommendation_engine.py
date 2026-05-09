from services.recommendation import generate_recommendations
from services.recommendation_engine import RecommendationEngine
from services.recommendation_knowledge_base import RecommendationKnowledgeBase


def _flatten_card_text(cards):
    parts = []
    for card in cards:
        parts.extend(
            [
                card.get("summary", ""),
                card.get("reason", ""),
                card.get("source_label", ""),
            ]
        )
        parts.extend(card.get("actions", []))
    return "\n".join(parts)


class StubKnowledgeBase:
    def __init__(self, entries):
        self.entries = entries

    def match(self, signal):
        return self.entries


def test_recommendation_engine_groups_by_topic_priority_and_merges_confidence_notice():
    engine = RecommendationEngine(
        knowledge_base=StubKnowledgeBase(
            [
                {
                    "id": "lifestyle-low",
                    "topic": "lifestyle",
                    "priority": "low",
                    "summary_template": "低优先级生活方式建议",
                    "explanation_template": "低优先级原因",
                    "action_templates": ["低优先级行动"],
                    "safety_boundary": {"avoid_diagnosis": True},
                },
                {
                    "id": "lifestyle-high",
                    "topic": "lifestyle",
                    "priority": "high",
                    "summary_template": "高优先级生活方式建议",
                    "explanation_template": "高优先级原因",
                    "action_templates": ["高优先级行动"],
                    "safety_boundary": {"avoid_diagnosis": True},
                },
                {
                    "id": "confidence-low",
                    "topic": "confidence_notice",
                    "priority": "medium",
                    "summary_template": "记录较少",
                    "explanation_template": "记录天数较少，建议继续补充记录。",
                    "action_templates": ["继续记录"],
                    "safety_boundary": {"avoid_diagnosis": True},
                },
                {
                    "id": "follow-up",
                    "topic": "follow_up",
                    "priority": "medium",
                    "summary_template": "随访建议",
                    "explanation_template": "随访原因",
                    "action_templates": ["保持记录"],
                    "safety_boundary": {"avoid_diagnosis": True},
                },
            ]
        )
    )

    cards = engine.build({"risk_level": "medium"})

    assert [card["topic"] for card in cards] == ["follow_up", "lifestyle"]
    assert cards[1]["summary"] == "高优先级生活方式建议"
    assert "低优先级" not in _flatten_card_text(cards)
    assert "记录天数较少，建议继续补充记录。" in cards[0]["reason"]


def test_guideline_knowledge_base_entries_declare_avoid_diagnosis_boundary():
    entries = RecommendationKnowledgeBase().list_entries()

    assert entries
    assert all(
        entry.get("safety_boundary", {}).get("avoid_diagnosis") is True
        for entry in entries
    )


def test_guideline_recommendations_keep_frontend_payload_and_safety_boundary():
    signals = [
        {
            "risk_level": "high",
            "high_bp_days": 0,
            "trend_direction": "upward",
            "record_days": 1,
            "confidence_level": "medium",
            "bp_grade": "grade2",
        },
        {
            "risk_level": "high",
            "high_bp_days": 0,
            "trend_direction": "stable",
            "record_days": 5,
            "confidence_level": "high",
            "bp_grade": "grade3",
        },
    ]
    cards = [
        card
        for signal in signals
        for card in generate_recommendations(
            guideline_signal=signal,
            risk_probability=0.72,
        )
    ]

    assert cards
    assert all(
        {"topic", "summary", "reason", "actions", "source_label"}.issubset(card)
        for card in cards
    )
    text = _flatten_card_text(cards)
    forbidden_phrases = [
        "确诊",
        "诊断",
        "处方",
        "药物干预",
        "调整治疗方案",
        "调整用药",
        "自行用药",
        "属于重度高血压",
        "属于高血压前期",
        "医疗干预",
        "治疗方案",
    ]
    assert not any(phrase in text for phrase in forbidden_phrases)
