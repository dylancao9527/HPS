from services.recommendation_engine import RecommendationEngine


_ENGINE = RecommendationEngine()


def get_risk_level(probability):
    if probability < 0.3:
        return ("低风险", "low", "#22c55e")
    if probability < 0.6:
        return ("中风险", "medium", "#f59e0b")
    return ("高风险", "high", "#ef4444")


def generate_recommendations(*, guideline_signal, risk_probability):
    signal = dict(guideline_signal or {})
    signal.setdefault("risk_level", get_risk_level(risk_probability)[1])
    return _ENGINE.build(signal)
