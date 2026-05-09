from dataclasses import dataclass
from datetime import date, datetime


DAILY_BP_HIGH_SYSTOLIC_THRESHOLD = 140
DAILY_BP_HIGH_DIASTOLIC_THRESHOLD = 90
DAILY_BP_ELEVATED_SYSTOLIC_THRESHOLD = 130
DAILY_BP_ELEVATED_DIASTOLIC_THRESHOLD = 85


@dataclass(frozen=True)
class DailyBPSeriesPoint:
    recorded_on: date
    average_systolic: float
    average_diastolic: float
    measurements: int

    @property
    def has_high_bp(self) -> bool:
        return is_high_bp(self.average_systolic, self.average_diastolic)

    @property
    def has_elevated_bp(self) -> bool:
        return is_elevated_bp(self.average_systolic, self.average_diastolic)


def coerce_recorded_on(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    if hasattr(value, "date"):
        return value.date()
    return value


def is_high_bp(systolic, diastolic) -> bool:
    if systolic is not None and systolic >= DAILY_BP_HIGH_SYSTOLIC_THRESHOLD:
        return True
    return diastolic is not None and diastolic >= DAILY_BP_HIGH_DIASTOLIC_THRESHOLD


def is_elevated_bp(systolic, diastolic) -> bool:
    if systolic is not None and systolic >= DAILY_BP_ELEVATED_SYSTOLIC_THRESHOLD:
        return True
    return (
        diastolic is not None
        and diastolic >= DAILY_BP_ELEVATED_DIASTOLIC_THRESHOLD
    )


def count_leading_high_bp_days(points, *, limit=3) -> int:
    leading_days = 0
    for point in list(points or [])[:limit]:
        if has_high_bp_point(point):
            leading_days += 1
            continue
        break
    return leading_days


def has_high_bp_point(point) -> bool:
    if hasattr(point, "has_high_bp"):
        return bool(point.has_high_bp)
    if isinstance(point, dict):
        return is_high_bp(
            point.get("average_systolic") or point.get("systolic"),
            point.get("average_diastolic") or point.get("diastolic"),
        )
    return is_high_bp(
        getattr(point, "average_systolic", None) or getattr(point, "systolic", None),
        getattr(point, "average_diastolic", None) or getattr(point, "diastolic", None),
    )
