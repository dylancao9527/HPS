class UserPredictionRecordActions:
    def __init__(self, *, repository):
        self.repository = repository

    def get_history(self, query):
        return self.repository.get_prediction_history(
            user_id=query.user_id,
            page=query.page,
            per_page=query.per_page,
            start_date=query.start_date,
            end_date=query.end_date,
        )

    def delete_prediction(self, command):
        deleted = self.repository.delete_prediction(
            user_id=command.user_id,
            prediction_id=command.prediction_id,
        )
        if not deleted:
            return {"error": "记录不存在"}, 404
        return {"message": "已删除"}, 200

    def batch_delete_predictions(self, *, user_id, prediction_ids):
        if not prediction_ids:
            return {"error": "请选择要删除的记录"}, 400
        deleted = self.repository.batch_delete_predictions(
            user_id=user_id,
            prediction_ids=prediction_ids,
        )
        return {"message": f"已删除 {deleted} 条记录"}

    def list_prediction_trend(self, *, user_id, limit):
        return {
            "records": self.repository.list_prediction_trend(
                user_id=user_id,
                limit=limit,
            )
        }
