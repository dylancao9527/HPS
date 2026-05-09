from prediction.domain.governance_policy import (
    build_anomaly_flags,
    build_governance_summary,
)


def test_anomaly_flags_cover_prediction_chain_governance_cases():
    assert build_anomaly_flags(
        {
            "risk_level": "高风险",
            "confidence_level": "low",
            "data_days_used": 2,
            "input_data": {
                "age": 56,
                "BMI": None,
                "currentSmoker": 1,
                "BPMeds": None,
                "diabetes": 0,
                "totChol": None,
                "glucose": None,
            },
            "bp_forecast": [{"systolic": 142, "diastolic": 91}],
            "recommendations": [],
        }
    ) == [
        "high_risk_without_recommendation",
        "high_risk_low_confidence",
        "insufficient_data_prediction",
        "missing_key_profile_fields",
    ]

    assert build_anomaly_flags(
        {
            "risk_level": "低风险",
            "confidence_level": "medium",
            "data_days_used": 8,
            "input_data": {
                "age": 56,
                "BMI": 27.4,
                "currentSmoker": 1,
                "cigsPerDay": 5,
                "BPMeds": 0,
                "diabetes": 0,
                "totChol": 190,
                "glucose": 96,
            },
            "bp_forecast": [{"systolic": 145, "diastolic": 92}],
            "recommendations": [{"summary": "保持观察"}],
        }
    ) == ["elevated_forecast_low_risk"]


def test_optional_missing_risk_factor_inputs_are_governance_signal_only():
    assert build_anomaly_flags(
        {
            "risk_level": "中风险",
            "confidence_level": "medium",
            "data_days_used": 8,
            "input_data": {
                "age": 56,
                "BMI": 27.4,
                "currentSmoker": None,
                "BPMeds": None,
                "diabetes": None,
                "totChol": None,
                "glucose": None,
            },
            "bp_forecast": [{"systolic": 132, "diastolic": 84}],
            "recommendations": [{"summary": "保持观察"}],
        }
    ) == ["missing_key_profile_fields"]

    assert build_anomaly_flags(
        {
            "risk_level": "中风险",
            "confidence_level": "medium",
            "data_days_used": 8,
            "input_data": {
                "age": 56,
                "BMI": 27.4,
                "currentSmoker": 1,
                "cigsPerDay": None,
                "BPMeds": 0,
                "diabetes": 0,
                "totChol": 190,
                "glucose": 96,
            },
            "bp_forecast": [{"systolic": 132, "diastolic": 84}],
            "recommendations": [{"summary": "保持观察"}],
        }
    ) == ["missing_key_profile_fields"]


def test_governance_summary_exposes_core_prediction_chain_metrics():
    summary = build_governance_summary(
        [
            {
                "risk_level": "高风险",
                "confidence_level": "low",
                "data_days_used": 2,
                "cache_mode": "model_reused",
                "anomaly_flags": [
                    "high_risk_low_confidence",
                    "insufficient_data_prediction",
                ],
            },
            {
                "risk_level": "中风险",
                "confidence_level": "medium",
                "data_days_used": 8,
                "cache_mode": "fresh_train",
                "anomaly_flags": [],
            },
            {
                "risk_level": "high",
                "confidence_level": "high",
                "data_days_used": 12,
                "cache_mode": "model_reused",
                "anomaly_flags": ["high_risk_without_recommendation"],
            },
        ]
    )

    assert summary["total_predictions"] == 3
    assert summary["high_risk_predictions"] == 2
    assert summary["low_confidence_predictions"] == 1
    assert summary["low_confidence_rate"] == 0.3333
    assert summary["anomaly_predictions"] == 2
    assert summary["insufficient_data_predictions"] == 1
    assert summary["prophet_model_reuse_count"] == 2
    assert summary["prophet_model_retrain_count"] == 1
