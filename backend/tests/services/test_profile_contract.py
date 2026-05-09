import pytest

from services.profile_contract import (
    coerce_profile_field,
    normalize_profile_payload,
    validate_profile_payload,
)


def test_profile_payload_normalizes_aliases_and_drops_legacy_unused_fields():
    payload = normalize_profile_payload(
        {
            "gender": "Female",
            "smoking": "Yes",
            "cigsPerDay": "8",
            "BPMeds": "0",
            "cholesterol": "180",
            "alcohol": "legacy",
            "family_history": "legacy",
        }
    )

    assert payload["male"] == 0
    assert payload["current_smoker"] == 1
    assert payload["cigs_per_day"] == "8"
    assert payload["bp_meds"] == "0"
    assert payload["tot_chol"] == "180"
    assert "alcohol" not in payload
    assert "family_history" not in payload


def test_profile_payload_normalizes_camel_case_without_overriding_canonical_values():
    payload = normalize_profile_payload(
        {
            "current_smoker": 0,
            "currentSmoker": 1,
            "tot_chol": 190,
            "totChol": 210,
        }
    )

    assert payload["current_smoker"] == 0
    assert payload["tot_chol"] == 190


def test_profile_contract_validates_ranges_binary_fields_and_diagnosis_feedback():
    validate_profile_payload(
        {
            "age": "56",
            "height": "170",
            "weight": "70",
            "male": "1",
            "current_smoker": "0",
            "bp_meds": "1",
            "diabetes": False,
            "diagnosis": "No",
        }
    )

    with pytest.raises(ValueError, match="诊断反馈取值无效"):
        validate_profile_payload(
            {
                "male": "1",
                "current_smoker": "0",
                "bp_meds": "0",
                "diabetes": "0",
                "diagnosis": "Confirmed",
            }
        )


def test_profile_contract_coerces_nullable_numeric_string_and_binary_fields():
    assert coerce_profile_field("nickname", "") is None
    assert coerce_profile_field("diagnosis", "") is None
    assert coerce_profile_field("age", "56") == 56.0
    assert coerce_profile_field("tot_chol", "") is None
    assert coerce_profile_field("bp_meds", "1") == 1
    assert coerce_profile_field("diabetes", False) == 0
