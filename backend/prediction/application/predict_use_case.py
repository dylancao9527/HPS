from prediction.application.prediction_run import PredictionRun


class PredictUseCase:
    def __init__(
        self,
        *,
        repository,
        prophet_gateway,
        risk_gateway,
        recommendation_service,
        risk_level_service,
        now_provider,
    ):
        self.repository = repository
        self.prophet_gateway = prophet_gateway
        self.risk_gateway = risk_gateway
        self.recommendation_service = recommendation_service
        self.risk_level_service = risk_level_service
        self.now_provider = now_provider

    def execute(self, command):
        return PredictionRun(
            repository=self.repository,
            prophet_gateway=self.prophet_gateway,
            risk_gateway=self.risk_gateway,
            recommendation_service=self.recommendation_service,
            risk_level_service=self.risk_level_service,
            now_provider=self.now_provider,
        ).execute(command)
