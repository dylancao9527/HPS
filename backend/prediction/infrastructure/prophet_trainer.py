"""Prophet 模型训练器。

封装 Prophet 模型构建、参数配置和训练逻辑。
从 prophet_gateway 提取，使训练逻辑可独立测试和复用。
"""

from typing import Any

from prediction.infrastructure.prophet_training_context import (
    HIGH_CONFIDENCE_DAYS,
    SHORT_HISTORY_DAYS,
)


def build_prophet_model(
    forecast_days: int,
    data_days_used: int,
    parameter_profile: str,
):
    """构建未拟合的 Prophet 模型实例及其季节性配置。

    返回 (model, seasonality_dict)。
    """
    changepoint_prior_scale = 0.05
    if parameter_profile == "short":
        changepoint_prior_scale = 0.02
    elif parameter_profile == "volatile":
        changepoint_prior_scale = 0.1

    seasonality = build_prophet_seasonality(
        forecast_days,
        data_days_used,
        parameter_profile,
    )

    from prophet import Prophet

    prophet_kwargs: dict[str, Any] = {
        "changepoint_prior_scale": changepoint_prior_scale,
        "seasonality_mode": "additive",
        "daily_seasonality": False,
        "weekly_seasonality": seasonality["weekly_enabled"],
        "yearly_seasonality": False,
    }
    model = Prophet(**prophet_kwargs)

    if seasonality["monthly_enabled"]:
        model.add_seasonality(name="monthly", period=30.5, fourier_order=3)

    return model, seasonality


def build_prophet_seasonality(
    forecast_days: int,
    data_days_used: int,
    parameter_profile: str,
) -> dict[str, bool]:
    weekly_enabled = False
    monthly_enabled = False

    if parameter_profile != "short":
        if forecast_days == 7:
            weekly_enabled = data_days_used >= 14
        elif forecast_days == 14:
            weekly_enabled = data_days_used >= SHORT_HISTORY_DAYS
            monthly_enabled = data_days_used >= HIGH_CONFIDENCE_DAYS

    return {
        "weekly_enabled": weekly_enabled,
        "monthly_enabled": monthly_enabled,
    }


def train_models_for_context(forecast_days, context):
    """训练收缩压和舒张压两个 Prophet 模型。

    返回 (sys_model, dia_model, seasonality)。
    """
    sys_df = context["daily"][["date", "systolic"]].rename(
        columns={"date": "ds", "systolic": "y"}
    )
    sys_model, seasonality = build_prophet_model(
        forecast_days, context["data_days_used"], context["parameter_profile"]
    )
    sys_model.fit(sys_df)

    dia_df = context["daily"][["date", "diastolic"]].rename(
        columns={"date": "ds", "diastolic": "y"}
    )
    dia_model, _ = build_prophet_model(
        forecast_days, context["data_days_used"], context["parameter_profile"]
    )
    dia_model.fit(dia_df)

    return sys_model, dia_model, seasonality


def predict_from_models(sys_model, dia_model, forecast_days):
    """用已训练的 Prophet 模型生成 N 天预测。"""
    future_sys = sys_model.make_future_dataframe(periods=forecast_days)
    future_dia = dia_model.make_future_dataframe(periods=forecast_days)

    forecast_sys = sys_model.predict(future_sys)
    forecast_dia = dia_model.predict(future_dia)

    sys_pred = forecast_sys["yhat"].tail(forecast_days).to_numpy(dtype=float)
    dia_pred = forecast_dia["yhat"].tail(forecast_days).to_numpy(dtype=float)

    return [
        {
            "day": i + 1,
            "systolic": round(float(sys_pred[i]), 1),
            "diastolic": round(float(dia_pred[i]), 1),
        }
        for i in range(forecast_days)
    ]
