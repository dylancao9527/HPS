"""Prophet 训练数据 DataFrame 构建器。

将不同来源的血压记录转换为 Prophet 所需的日级聚合 DataFrame，
包含 date / systolic / diastolic / measurements 列。
"""

import pandas as pd


def build_daily_training_frame(records) -> pd.DataFrame:
    """从原始血压记录（ORM 对象）构建日均 DataFrame。"""
    df = pd.DataFrame(
        [
            {
                "ds": record.recorded_at,
                "systolic": record.systolic_bp,
                "diastolic": record.diastolic_bp,
            }
            for record in records
        ]
    )
    df["date"] = pd.to_datetime(df["ds"]).dt.date

    daily = (
        df.groupby("date")
        .agg(
            systolic=("systolic", "mean"),
            diastolic=("diastolic", "mean"),
            measurements=("ds", "count"),
        )
        .reset_index()
    )
    daily["date"] = pd.to_datetime(daily["date"])
    return daily.sort_values("date").reset_index(drop=True)


def build_daily_training_frame_from_aggregates(rows) -> pd.DataFrame:
    """从预聚合行构建日均 DataFrame。"""
    daily = pd.DataFrame(
        [
            {
                "date": row.recorded_day,
                "systolic": float(row.systolic),
                "diastolic": float(row.diastolic),
                "measurements": int(row.measurements),
            }
            for row in rows
        ]
    )
    daily["date"] = pd.to_datetime(daily["date"])
    return daily.sort_values("date").reset_index(drop=True)


def build_daily_training_frame_from_series(points) -> pd.DataFrame:
    """从 DailyBPSeries 点构建日均 DataFrame。"""
    daily = pd.DataFrame(
        [
            {
                "date": point.recorded_on,
                "systolic": float(point.average_systolic),
                "diastolic": float(point.average_diastolic),
                "measurements": int(point.measurements),
            }
            for point in points
        ]
    )
    daily["date"] = pd.to_datetime(daily["date"])
    return daily.sort_values("date").reset_index(drop=True)
