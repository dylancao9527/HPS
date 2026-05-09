from prediction.application.batch_delete_predictions import BatchDeletePredictionsUseCase
from prediction.application.delete_prediction import DeletePredictionUseCase
from prediction.application.get_bp_data_status import GetBPDataStatusUseCase
from prediction.application.get_prediction_history import GetPredictionHistoryUseCase
from prediction.application.list_prediction_trend import (
    ListPredictionTrendUseCase,
)
from prediction.application.predict_use_case import PredictUseCase
from prediction.application.user_prediction_records import UserPredictionRecordActions
from prediction.infrastructure.gateways import (
    ProphetGateway,
    RecommendationService,
    RiskGateway,
    RiskLevelService,
)
from prediction.infrastructure.repositories import PredictionRepository
from utils.time_utils import utc_now_naive


class PredictionUseCaseFactory:
    def __init__(
        self,
        *,
        repository_factory=PredictionRepository,
        prophet_gateway_factory=ProphetGateway,
        risk_gateway_factory=RiskGateway,
        recommendation_service_factory=RecommendationService,
        risk_level_service_factory=RiskLevelService,
        now_provider=utc_now_naive,
    ):
        self.repository_factory = repository_factory
        self.prophet_gateway_factory = prophet_gateway_factory
        self.risk_gateway_factory = risk_gateway_factory
        self.recommendation_service_factory = recommendation_service_factory
        self.risk_level_service_factory = risk_level_service_factory
        self.now_provider = now_provider

    def build_predict_use_case(self):
        return PredictUseCase(
            repository=self.repository_factory(),
            prophet_gateway=self.prophet_gateway_factory(),
            risk_gateway=self.risk_gateway_factory(),
            recommendation_service=self.recommendation_service_factory(),
            risk_level_service=self.risk_level_service_factory(),
            now_provider=self.now_provider,
        )

    def build_prediction_history_use_case(self):
        return GetPredictionHistoryUseCase(
            actions=self.build_user_prediction_record_actions()
        )

    def build_delete_prediction_use_case(self):
        return DeletePredictionUseCase(actions=self.build_user_prediction_record_actions())

    def build_bp_data_status_use_case(self):
        return GetBPDataStatusUseCase(repository=self.repository_factory())

    def build_batch_delete_predictions_use_case(self):
        return BatchDeletePredictionsUseCase(
            actions=self.build_user_prediction_record_actions()
        )

    def build_list_prediction_trend_use_case(self):
        return ListPredictionTrendUseCase(
            actions=self.build_user_prediction_record_actions()
        )

    def build_user_prediction_record_actions(self):
        return UserPredictionRecordActions(repository=self.repository_factory().records)
