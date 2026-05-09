class PredictionGuidelineMapping:
    GUIDELINE_CATEGORY = "guideline_payload"
    GUIDELINE_TITLE_SUMMARY = "summary"
    GUIDELINE_TITLE_REASON = "reason"
    GUIDELINE_TITLE_ACTION = "action"
    GUIDELINE_TITLE_MATCHED_KNOWLEDGE_ID = "matched_knowledge_id"
    GUIDELINE_TITLE_SOURCE_LABEL = "source_label"


def build_recommendations(items):
    rows = []
    for card in items or []:
        rows.append(
            {
                "topic": card.get("topic", "follow_up"),
                "summary": card.get("summary", ""),
                "reason": card.get("reason", ""),
                "actions": list(card.get("actions") or []),
                "source_label": card.get("source_label", ""),
            }
        )
    return rows


def assemble_recommendations(item):
    if isinstance(getattr(item, "recommendations", None), list):
        return item.recommendations

    if not item.recommendation_items:
        return []

    if all(
        rec.category == PredictionGuidelineMapping.GUIDELINE_CATEGORY
        for rec in item.recommendation_items
    ):
        card = {
            "topic": "follow_up",
            "summary": "",
            "reason": "",
            "actions": [],
            "source_label": "",
        }
        for rec in item.recommendation_items:
            if rec.title == PredictionGuidelineMapping.GUIDELINE_TITLE_SUMMARY:
                card["summary"] = rec.content
            elif rec.title == PredictionGuidelineMapping.GUIDELINE_TITLE_REASON:
                card["reason"] = rec.content
            elif rec.title == PredictionGuidelineMapping.GUIDELINE_TITLE_ACTION:
                card["actions"].append(rec.content)
            elif rec.title == PredictionGuidelineMapping.GUIDELINE_TITLE_SOURCE_LABEL:
                card["source_label"] = rec.content
        return [card]

    cards = {}
    order = []
    for rec in item.recommendation_items:
        topic = rec.category
        if topic not in cards:
            cards[topic] = {
                "topic": topic,
                "summary": "",
                "reason": "",
                "actions": [],
                "source_label": "",
            }
            order.append(topic)
        if rec.title == PredictionGuidelineMapping.GUIDELINE_TITLE_SUMMARY:
            cards[topic]["summary"] = rec.content
        elif rec.title == PredictionGuidelineMapping.GUIDELINE_TITLE_REASON:
            cards[topic]["reason"] = rec.content
        elif rec.title == PredictionGuidelineMapping.GUIDELINE_TITLE_ACTION:
            cards[topic]["actions"].append(rec.content)
        elif rec.title == PredictionGuidelineMapping.GUIDELINE_TITLE_SOURCE_LABEL:
            cards[topic]["source_label"] = rec.content
    return [cards[t] for t in order]
