from prediction.application.user_prediction_records import UserPredictionRecordActions


class BatchDeletePredictionsUseCase:
    def __init__(self, *, repository=None, actions=None):
        self.actions = actions or UserPredictionRecordActions(repository=repository)

    def execute(self, *, user_id, prediction_ids):
        return self.actions.batch_delete_predictions(
            user_id=user_id,
            prediction_ids=prediction_ids,
        )
