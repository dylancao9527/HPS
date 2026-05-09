class ProphetModelLifecycle:
    def __init__(
        self,
        *,
        inspect_model_state,
        load_or_train_models=None,
        predict_from_models=None,
        build_training_meta=None,
        model_version=None,
    ):
        self.inspect_model_state = inspect_model_state
        self.load_or_train_models = load_or_train_models
        self.predict_from_models = predict_from_models
        self.build_training_meta = build_training_meta
        self.model_version = model_version

    def predict(self, user_id, forecast_days=7, repository=None):
        model_state = self.inspect_model_state(
            user_id,
            forecast_days,
            repository=repository,
        )
        return self.predict_from_model_state(
            user_id,
            forecast_days,
            repository=repository,
            model_state=model_state,
        )

    def predict_from_model_state(
        self,
        user_id,
        forecast_days=7,
        *,
        repository=None,
        model_state,
    ):
        repository = model_state.get("repository", repository)
        context = model_state["context"]
        model_context = self.load_or_train_models(
            user_id,
            forecast_days,
            repository,
            context,
            model_state,
        )
        forecast = self.predict_from_models(
            model_context.sys_model,
            model_context.dia_model,
            forecast_days,
        )
        training_meta = self.build_training_meta(
            context,
            model_context.seasonality,
        )
        training_meta.update(
            {
                "model_strategy": model_context.model_strategy,
                "new_data_days_since_training": model_state.get(
                    "new_data_days_since_training", 0
                ),
                "retrain_threshold_days": model_state.get("retrain_threshold_days"),
            }
        )

        return {
            "forecast": forecast,
            "data_days_used": context["data_days_used"],
            "total_history_days": context["total_history_days"],
            "data_range": context["data_range"],
            "history_window_capped": context["history_window_capped"],
            "seasonality": model_context.seasonality,
            "training_meta": training_meta,
            "confidence_level": context["confidence_level"],
            "confidence_reasons": context["confidence_reasons"],
            "model_version": self.model_version,
            "data_signature": model_context.model_data_signature,
            "current_data_signature": context["data_signature"],
            "model_cache_hit": model_context.model_cache_hit,
            "model_asset_id": model_context.model_asset_id,
            "model_strategy": model_context.model_strategy,
        }
