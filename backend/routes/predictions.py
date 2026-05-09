"""
==============================================================================
预测路由 (predictions.py)
==============================================================================
"""

from flask import Blueprint, jsonify, request

from extensions import db
from prediction.api.serializers import serialize_prediction_result
from prediction.application.composition import PredictionUseCaseFactory
from prediction.domain.bp_data_policy import InsufficientBPDataForPredictionError
from prediction.domain.forecast_period_policy import UnsupportedForecastPeriodError
from prediction.schemas.commands import (
    DeletePredictionCommand,
    GetBPDataStatusQuery,
    GetPredictionHistoryQuery,
    PredictCommand,
)
from prediction.schemas.input_snapshot import IncompleteRiskFactorProfileError
from routes.auth import token_required

predictions_bp = Blueprint("predictions", __name__, url_prefix="/api")
prediction_use_cases = PredictionUseCaseFactory()


def build_predict_use_case():
    return prediction_use_cases.build_predict_use_case()


def build_prediction_history_use_case():
    return prediction_use_cases.build_prediction_history_use_case()


def build_delete_prediction_use_case():
    return prediction_use_cases.build_delete_prediction_use_case()


def build_bp_data_status_use_case():
    return prediction_use_cases.build_bp_data_status_use_case()


def build_batch_delete_predictions_use_case():
    return prediction_use_cases.build_batch_delete_predictions_use_case()


def build_user_prediction_record_actions():
    return prediction_use_cases.build_user_prediction_record_actions()


@predictions_bp.route("/predict", methods=["POST"])
@token_required
def predict(current_user):
    try:
        data = request.get_json() or {}
        command = PredictCommand(
            user_id=current_user.id,
            forecast_days=data.get("forecast_days"),
            use_trend_fusion=data.get("use_trend_fusion", True),
        )
        result = build_predict_use_case().execute(command)
        return jsonify(serialize_prediction_result(result))

    except UnsupportedForecastPeriodError as e:
        return jsonify({"error": str(e)}), 400

    except IncompleteRiskFactorProfileError as e:
        return jsonify({"error": str(e)}), 400

    except InsufficientBPDataForPredictionError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        db.session.rollback()
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@predictions_bp.route("/predictions", methods=["GET"])
@token_required
def get_predictions(current_user):
    query = GetPredictionHistoryQuery(
        user_id=current_user.id,
        page=request.args.get("page", 1, type=int),
        per_page=request.args.get("per_page", 10, type=int),
        start_date=request.args.get("start_date", ""),
        end_date=request.args.get("end_date", ""),
    )
    return jsonify(build_prediction_history_use_case().execute(query))


@predictions_bp.route("/predictions/<int:pred_id>", methods=["DELETE"])
@token_required
def delete_prediction(current_user, pred_id):
    result = build_delete_prediction_use_case().execute(
        DeletePredictionCommand(user_id=current_user.id, prediction_id=pred_id)
    )
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result)


@predictions_bp.route("/predictions/batch", methods=["DELETE"])
@token_required
def batch_delete_predictions(current_user):
    data = request.get_json() or {}
    ids = data.get("ids", [])
    result = build_batch_delete_predictions_use_case().execute(
        user_id=current_user.id,
        prediction_ids=ids,
    )
    if isinstance(result, tuple):
        payload, status = result
        return jsonify(payload), status
    return jsonify(result)


@predictions_bp.route("/bp-data-status", methods=["GET"])
@token_required
def bp_data_status(current_user):
    """返回用户血压数据统计 + 按预测天数的历史充分性提示。"""
    try:
        query = GetBPDataStatusQuery(
            user_id=current_user.id,
            forecast_days=request.args.get("forecast_days"),
        )
    except UnsupportedForecastPeriodError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(build_bp_data_status_use_case().execute(query))
