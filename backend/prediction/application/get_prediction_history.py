from prediction.schemas.commands import GetPredictionHistoryQuery
from prediction.application.user_prediction_records import UserPredictionRecordActions


class GetPredictionHistoryUseCase:
    def __init__(self, *, repository=None, actions=None):
        self.actions = actions or UserPredictionRecordActions(repository=repository)

    def execute(self, query: GetPredictionHistoryQuery):
        return self.actions.get_history(query)
