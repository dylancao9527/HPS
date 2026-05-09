from prediction.application.user_prediction_records import UserPredictionRecordActions


class ListPredictionTrendUseCase:
    def __init__(self, *, repository=None, actions=None):
        self.actions = actions or UserPredictionRecordActions(repository=repository)

    def execute(self, *, user_id, limit):
        return self.actions.list_prediction_trend(user_id=user_id, limit=limit)
