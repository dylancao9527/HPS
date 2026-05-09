from datetime import datetime, timedelta
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
backend_root = str(BACKEND_ROOT)
if backend_root in sys.path:
    sys.path.remove(backend_root)
sys.path.insert(0, backend_root)


@pytest.fixture
def fixed_now():
    return datetime(2026, 4, 25, 9, 30, 0)


@pytest.fixture
def fixed_cache_windows():
    return {
        "hot_window": timedelta(hours=1),
        "cache_window": timedelta(hours=24),
    }


@pytest.fixture
def fake_profile():
    return SimpleNamespace(
        age=56,
        male=1,
        bmi=27.4,
        current_smoker=1,
        cigs_per_day=5,
        bp_meds=1,
        diabetes=0,
        tot_chol=190,
        glucose=96,
        profile_complete=True,
    )


@pytest.fixture
def fake_user(fake_profile):
    return SimpleNamespace(
        id=42,
        profile=SimpleNamespace(diagnosis=None),
        risk_factor_profile=fake_profile,
    )


@pytest.fixture
def fake_bp_record(fixed_now):
    return SimpleNamespace(
        id=7,
        systolic_bp=138,
        diastolic_bp=86,
        heart_rate=72,
        recorded_at=fixed_now,
    )


@pytest.fixture
def sample_forecast():
    return [
        {
            "day": 1,
            "systolic": 132,
            "diastolic": 84,
            "systolic_lower": 126,
            "systolic_upper": 139,
            "diastolic_lower": 78,
            "diastolic_upper": 89,
        },
        {
            "day": 2,
            "systolic": 141,
            "diastolic": 91,
            "systolic_lower": 134,
            "systolic_upper": 148,
            "diastolic_lower": 84,
            "diastolic_upper": 96,
        },
    ]


@pytest.fixture
def sample_training_meta():
    return {
        "aggregation_mode": "daily_mean",
        "parameter_profile": "standard",
        "seasonality": {
            "weekly_enabled": True,
            "monthly_enabled": False,
        },
        "avg_measurements_per_day": 2.5,
        "recent_sys_range_mean": 5.2,
        "recent_dia_range_mean": 3.1,
        "confidence_level": "medium",
        "confidence_reasons": ["short_history"],
    }
