DEFAULT_FORECAST_DAYS = 7
FORECAST_PERIOD_ERROR_MESSAGE = "预测周期已统一为未来7天"


class UnsupportedForecastPeriodError(ValueError):
    pass


def require_supported_forecast_days(forecast_days):
    if forecast_days is None:
        return DEFAULT_FORECAST_DAYS

    if isinstance(forecast_days, bool):
        raise UnsupportedForecastPeriodError(FORECAST_PERIOD_ERROR_MESSAGE)

    try:
        normalized = int(forecast_days)
    except (TypeError, ValueError) as exc:
        raise UnsupportedForecastPeriodError(FORECAST_PERIOD_ERROR_MESSAGE) from exc

    if normalized != DEFAULT_FORECAST_DAYS:
        raise UnsupportedForecastPeriodError(FORECAST_PERIOD_ERROR_MESSAGE)

    return DEFAULT_FORECAST_DAYS
