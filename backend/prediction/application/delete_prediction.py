from prediction.application.user_prediction_records import UserPredictionRecordActions


class DeletePredictionUseCase:
    def __init__(self, *, repository=None, actions=None):
        self.actions = actions or UserPredictionRecordActions(repository=repository)

    def execute(self, command):
        return self.actions.delete_prediction(command)
