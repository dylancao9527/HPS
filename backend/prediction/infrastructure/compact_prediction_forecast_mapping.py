def build_forecast_points(points):
    return [
        {
            "day": point.get("day", index + 1),
            "systolic": point.get("systolic"),
            "diastolic": point.get("diastolic"),
            "systolic_lower": point.get("systolic_lower"),
            "systolic_upper": point.get("systolic_upper"),
            "diastolic_lower": point.get("diastolic_lower"),
            "diastolic_upper": point.get("diastolic_upper"),
        }
        for index, point in enumerate(points or [])
    ]


def assemble_forecast(prophet_record, item):
    if item is not None and isinstance(getattr(item, "bp_forecast", None), list):
        return item.bp_forecast
    if not prophet_record or not prophet_record.forecast_points:
        return []
    return [
        {
            "day": point.forecast_day,
            "systolic": point.systolic,
            "diastolic": point.diastolic,
            "systolic_lower": point.systolic_lower,
            "systolic_upper": point.systolic_upper,
            "diastolic_lower": point.diastolic_lower,
            "diastolic_upper": point.diastolic_upper,
        }
        for point in prophet_record.forecast_points
    ]
