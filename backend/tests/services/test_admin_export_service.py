from services.admin_export_service import (
    build_csv_response,
    build_prediction_governance_export_download,
    build_training_export_download,
)


def test_admin_csv_downloads_share_response_contract():
    training = build_training_export_download("age,BMI\n56,27.4\n")
    governance = build_prediction_governance_export_download("prediction_id\n901\n")

    training_response = build_csv_response(training)
    governance_response = build_csv_response(governance)

    assert training.filename == "training_data_export.csv"
    assert governance.filename == "prediction_governance_export.csv"
    assert training_response.get_data(as_text=True) == "age,BMI\n56,27.4\n"
    assert training_response.mimetype == "text/csv"
    assert (
        training_response.headers["Content-Disposition"]
        == "attachment; filename=training_data_export.csv"
    )
    assert (
        governance_response.headers["Content-Disposition"]
        == "attachment; filename=prediction_governance_export.csv"
    )
