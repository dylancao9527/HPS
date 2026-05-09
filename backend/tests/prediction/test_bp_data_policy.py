import pytest

from prediction.domain.bp_data_policy import (
    InsufficientBPDataForPredictionError,
    MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION,
    build_bp_data_status,
    require_minimum_bp_days_for_prediction,
)
from prediction.domain.governance_policy import has_insufficient_data


def test_bp_data_status_uses_shared_prediction_data_policy():
    insufficient = build_bp_data_status(
        total_records=2,
        total_days=MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION - 1,
        forecast_days=7,
    )
    warning = build_bp_data_status(
        total_records=9,
        total_days=MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION,
        forecast_days=7,
    )
    recommended = build_bp_data_status(
        total_records=63,
        total_days=21,
        forecast_days=7,
    )

    assert insufficient["minimum_days"] == MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION
    assert insufficient["status"] == "insufficient"
    assert insufficient["meets_minimum"] is False
    assert warning["status"] == "warning"
    assert warning["meets_minimum"] is True
    assert warning["meets_recommended"] is False
    assert recommended["status"] == "recommended"
    assert recommended["meets_recommended"] is True


def test_prediction_guard_and_governance_share_minimum_bp_days():
    status = build_bp_data_status(
        total_records=2,
        total_days=MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION - 1,
        forecast_days=7,
    )

    with pytest.raises(InsufficientBPDataForPredictionError) as exc_info:
        require_minimum_bp_days_for_prediction(status)

    assert str(exc_info.value) == (
        f"血压记录不足：请至少记录 {MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION} "
        "个自然日后再进行预测"
    )
    assert has_insufficient_data(
        {"data_days_used": MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION - 1}
    )
    assert not has_insufficient_data(
        {"data_days_used": MINIMUM_BP_NATURAL_DAYS_FOR_PREDICTION}
    )
