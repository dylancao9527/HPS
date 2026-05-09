from models.prediction import PredictionRecord


def test_prediction_record_uses_json_payloads_for_optional_governance_signals():
    columns = PredictionRecord.__table__.c

    assert columns.input_snapshot.nullable is True
    assert columns.fusion_meta.nullable is True
    assert columns.bp_forecast.nullable is True
    assert columns.recommendations.nullable is True

