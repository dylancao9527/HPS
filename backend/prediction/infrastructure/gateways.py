from prediction.infrastructure.prophet_gateway import predict_bp_trend_for_user
from prediction.infrastructure.risk_model_gateway import score_risk_probability
from services.recommendation import generate_recommendations, get_risk_level


class RecommendationService:
    def generate(self, *, guideline_signal, risk_probability):
        return generate_recommendations(
            guideline_signal=guideline_signal,
            risk_probability=risk_probability,
        )


class RiskLevelService:
    def get_level(self, probability):
        return get_risk_level(probability)


class ProphetGateway:
    def predict(self, user_id, forecast_days):
        return predict_bp_trend_for_user(user_id, forecast_days)


class RiskGateway:
    def score(self, user_data, bp_forecast):
        return score_risk_probability(user_data, bp_forecast)
