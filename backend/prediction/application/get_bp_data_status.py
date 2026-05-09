class GetBPDataStatusUseCase:
    def __init__(self, *, repository):
        self.repository = repository

    def execute(self, query):
        return self.repository.get_bp_data_status(
            user_id=query.user_id,
            forecast_days=query.forecast_days,
        )
