import pandas as pd

from prediction.infrastructure import risk_model_gateway


class FakeRiskModel:
    def __init__(self):
        self.features = None

    def predict(self, features):
        self.features = features.copy()
        return [0.42]


def test_score_risk_probability_builds_stable_feature_frame(monkeypatch):
    feature_columns = [
        "age",
        "male",
        "BMI",
        "currentSmoker",
        "cigsPerDay",
        "BPMeds",
        "diabetes",
        "sysBP",
        "diaBP",
        "heartRate",
        "totChol",
        "glucose",
    ]
    categorical_features = ["male", "currentSmoker", "BPMeds", "diabetes"]
    fake_model = FakeRiskModel()

    monkeypatch.setattr(
        risk_model_gateway.model_registry,
        "get_model_config",
        lambda: {
            "feature_columns": feature_columns,
            "categorical_features": categorical_features,
        },
    )
    monkeypatch.setattr(
        risk_model_gateway.model_registry,
        "get_lgbm_model",
        lambda: fake_model,
    )

    probability, inference_meta = risk_model_gateway.score_risk_probability(
        {
            "age": 66,
            "male": 1,
            "BMI": 27.3,
            "currentSmoker": 1,
            "cigsPerDay": 5,
            "BPMeds": 1,
            "diabetes": 0,
            "heartRate": 72,
            "totChol": 190,
            "glucose": 95,
        },
        [
            {"systolic": 130, "diastolic": 85},
            {"systolic": 140, "diastolic": 90},
        ],
    )

    features = fake_model.features
    assert probability == 0.42
    assert inference_meta == {
        "bp_meds_input": 1,
        "bp_meds_model_value": 0,
        "bp_meds_policy": "neutralized_for_conservative_inference",
    }
    assert list(features.columns) == feature_columns
    assert features.loc[0, "sysBP"] == 135.0
    assert features.loc[0, "diaBP"] == 87.5
    assert features.loc[0, "BPMeds"] == 0
    assert isinstance(features["BPMeds"].dtype, pd.CategoricalDtype)
    assert list(features["BPMeds"].cat.categories) == [0, 1]
    assert pd.api.types.is_float_dtype(features["age"])
    assert pd.api.types.is_float_dtype(features["BMI"])
