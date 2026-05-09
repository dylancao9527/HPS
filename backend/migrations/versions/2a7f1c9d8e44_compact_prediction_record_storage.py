"""compact prediction record storage

Revision ID: 2a7f1c9d8e44
Revises: 9c1d2e3f4a5b
Create Date: 2026-05-08 14:05:00.000000

"""
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


# revision identifiers, used by Alembic.
revision = "2a7f1c9d8e44"
down_revision = "9c1d2e3f4a5b"
branch_labels = None
depends_on = None


OLD_DETAIL_TABLES = (
    "prediction_recommendations",
    "prediction_input_snapshots",
    "prediction_fusion_meta",
    "prediction_confidence_reasons",
    "prophet_forecast_points",
    "prediction_training_meta",
    "prophet_predictions",
)


def upgrade():
    with op.batch_alter_table("prediction_records", schema=None) as batch_op:
        batch_op.add_column(sa.Column("data_days_used", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("confidence_level", sa.String(length=16), nullable=True))
        batch_op.add_column(
            sa.Column(
                "cache_mode",
                sa.String(length=32),
                nullable=False,
                server_default="fresh_train",
            )
        )
        batch_op.add_column(
            sa.Column("has_anomaly", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(sa.Column("input_snapshot", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("fusion_meta", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("bp_forecast", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("training_meta", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("recommendations", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("anomaly_flags", sa.JSON(), nullable=True))
        batch_op.create_index(
            "ix_prediction_records_confidence_created_at",
            ["confidence_level", "created_at"],
            unique=False,
        )
        batch_op.create_index(
            "ix_prediction_records_anomaly_created_at",
            ["has_anomaly", "created_at"],
            unique=False,
        )

    bind = op.get_bind()
    if _has_table(bind, "prophet_predictions"):
        _backfill_compact_prediction_records(bind)

    with op.batch_alter_table("prediction_records", schema=None) as batch_op:
        if _has_column(bind, "prediction_records", "prophet_prediction_id"):
            _drop_fk_if_exists(
                batch_op,
                bind,
                "prediction_records",
                "fk_prediction_records_prophet_prediction_id_prophet_predictions",
            )
            _drop_index_if_exists(
                batch_op,
                bind,
                "prediction_records",
                "fk_prediction_records_prophet_prediction_id_prophet_predictions",
            )
            batch_op.drop_column("prophet_prediction_id")

    for table_name in OLD_DETAIL_TABLES:
        if _has_table(bind, table_name):
            op.drop_table(table_name)


def downgrade():
    op.create_table(
        "prophet_predictions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("forecast_days", sa.Integer(), nullable=False),
        sa.Column("data_days_used", sa.Integer(), nullable=False),
        sa.Column("total_history_days", sa.Integer(), nullable=False),
        sa.Column("history_window_capped", sa.Boolean(), nullable=False),
        sa.Column("data_range", sa.String(length=100), nullable=True),
        sa.Column("cache_key", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_prophet_predictions_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_prophet_predictions")),
        sa.CheckConstraint("forecast_days = 7", name=op.f("ck_prophet_predictions_forecast_days_7")),
    )
    with op.batch_alter_table("prophet_predictions", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_prophet_predictions_user_id"), ["user_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_prophet_predictions_cache_key"), ["cache_key"], unique=False)
        batch_op.create_index("ix_prophet_predictions_user_created_at", ["user_id", "created_at"], unique=False)

    op.create_table(
        "prediction_training_meta",
        sa.Column("prophet_prediction_id", sa.Integer(), nullable=False),
        sa.Column("aggregation_mode", sa.String(length=32), nullable=False),
        sa.Column("parameter_profile", sa.String(length=32), nullable=False),
        sa.Column("weekly_enabled", sa.Boolean(), nullable=False),
        sa.Column("monthly_enabled", sa.Boolean(), nullable=False),
        sa.Column("avg_measurements_per_day", sa.Float(), nullable=True),
        sa.Column("recent_sys_range_mean", sa.Float(), nullable=True),
        sa.Column("recent_dia_range_mean", sa.Float(), nullable=True),
        sa.Column("confidence_level", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["prophet_prediction_id"], ["prophet_predictions.id"], name=op.f("fk_prediction_training_meta_prophet_prediction_id_prophet_predictions"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("prophet_prediction_id", name=op.f("pk_prediction_training_meta")),
    )
    with op.batch_alter_table("prediction_training_meta", schema=None) as batch_op:
        batch_op.create_index("ix_prediction_training_meta_confidence_prophet", ["confidence_level", "prophet_prediction_id"], unique=False)

    op.create_table(
        "prophet_forecast_points",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("prophet_prediction_id", sa.Integer(), nullable=False),
        sa.Column("forecast_day", sa.Integer(), nullable=False),
        sa.Column("systolic", sa.Float(), nullable=False),
        sa.Column("diastolic", sa.Float(), nullable=False),
        sa.Column("systolic_lower", sa.Float(), nullable=True),
        sa.Column("systolic_upper", sa.Float(), nullable=True),
        sa.Column("diastolic_lower", sa.Float(), nullable=True),
        sa.Column("diastolic_upper", sa.Float(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["prophet_prediction_id"], ["prophet_predictions.id"], name=op.f("fk_prophet_forecast_points_prophet_prediction_id_prophet_predictions"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_prophet_forecast_points")),
        sa.UniqueConstraint("prophet_prediction_id", "forecast_day", name="uq_prophet_forecast_points_prediction_day"),
    )
    with op.batch_alter_table("prophet_forecast_points", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_prophet_forecast_points_prophet_prediction_id"), ["prophet_prediction_id"], unique=False)

    op.create_table(
        "prediction_confidence_reasons",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("prediction_record_id", sa.Integer(), nullable=False),
        sa.Column("reason_type", sa.String(length=32), nullable=False),
        sa.Column("reason_code", sa.String(length=64), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["prediction_record_id"], ["prediction_records.id"], name=op.f("fk_prediction_confidence_reasons_prediction_record_id_prediction_records"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_prediction_confidence_reasons")),
    )

    op.create_table(
        "prediction_fusion_meta",
        sa.Column("prediction_record_id", sa.Integer(), nullable=False),
        sa.Column("raw_probability", sa.Float(), nullable=False),
        sa.Column("fused_probability", sa.Float(), nullable=False),
        sa.Column("bp_meds_input", sa.Integer(), nullable=True),
        sa.Column("bp_meds_model_value", sa.Integer(), nullable=False),
        sa.Column("bp_meds_policy", sa.String(length=64), nullable=False),
        sa.Column("medication_adjustment", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["prediction_record_id"], ["prediction_records.id"], name=op.f("fk_prediction_fusion_meta_prediction_record_id_prediction_records"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("prediction_record_id", name=op.f("pk_prediction_fusion_meta")),
    )

    op.create_table(
        "prediction_input_snapshots",
        sa.Column("prediction_record_id", sa.Integer(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("male", sa.Integer(), nullable=False),
        sa.Column("current_smoker", sa.Integer(), nullable=True),
        sa.Column("cigs_per_day", sa.Float(), nullable=True),
        sa.Column("bp_meds", sa.Integer(), nullable=True),
        sa.Column("diabetes", sa.Integer(), nullable=True),
        sa.Column("tot_chol", sa.Float(), nullable=True),
        sa.Column("sys_bp", sa.Float(), nullable=False),
        sa.Column("dia_bp", sa.Float(), nullable=False),
        sa.Column("bmi", sa.Float(), nullable=False),
        sa.Column("heart_rate", sa.Float(), nullable=True),
        sa.Column("glucose", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["prediction_record_id"], ["prediction_records.id"], name=op.f("fk_prediction_input_snapshots_prediction_record_id_prediction_records"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("prediction_record_id", name=op.f("pk_prediction_input_snapshots")),
    )

    op.create_table(
        "prediction_recommendations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("prediction_record_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["prediction_record_id"], ["prediction_records.id"], name=op.f("fk_prediction_recommendations_prediction_record_id_prediction_records"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_prediction_recommendations")),
    )

    with op.batch_alter_table("prediction_records", schema=None) as batch_op:
        batch_op.add_column(sa.Column("prophet_prediction_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            op.f("fk_prediction_records_prophet_prediction_id_prophet_predictions"),
            "prophet_predictions",
            ["prophet_prediction_id"],
            ["id"],
        )
        batch_op.drop_index("ix_prediction_records_anomaly_created_at")
        batch_op.drop_index("ix_prediction_records_confidence_created_at")
        for column in (
            "anomaly_flags",
            "recommendations",
            "training_meta",
            "bp_forecast",
            "fusion_meta",
            "input_snapshot",
            "has_anomaly",
            "cache_mode",
            "confidence_level",
            "data_days_used",
        ):
            batch_op.drop_column(column)


def _backfill_compact_prediction_records(bind):
    for record in bind.execute(text("SELECT * FROM prediction_records ORDER BY id ASC")).mappings():
        prophet = _fetch_one(
            bind,
            "SELECT * FROM prophet_predictions WHERE id = :id",
            {"id": record.get("prophet_prediction_id")},
        )
        input_snapshot = _build_input_snapshot(
            _fetch_one(
                bind,
                "SELECT * FROM prediction_input_snapshots WHERE prediction_record_id = :id",
                {"id": record["id"]},
            ),
            prophet,
        )
        confidence_rows = _fetch_all(
            bind,
            "SELECT * FROM prediction_confidence_reasons WHERE prediction_record_id = :id ORDER BY sort_order ASC, id ASC",
            {"id": record["id"]},
        )
        training_reasons = [
            row["reason_code"] for row in confidence_rows if row["reason_type"] == "training_meta"
        ]
        fusion_reasons = [
            row["reason_code"] for row in confidence_rows if row["reason_type"] == "fusion_meta"
        ]
        model_strategy = next(
            (
                row["reason_code"]
                for row in confidence_rows
                if row["reason_type"] == "model_strategy"
            ),
            None,
        )
        forecast = _build_forecast(
            _fetch_all(
                bind,
                "SELECT * FROM prophet_forecast_points WHERE prophet_prediction_id = :id ORDER BY sort_order ASC, forecast_day ASC, id ASC",
                {"id": prophet["id"] if prophet else None},
            )
        )
        training_meta = _build_training_meta(
            _fetch_one(
                bind,
                "SELECT * FROM prediction_training_meta WHERE prophet_prediction_id = :id",
                {"id": prophet["id"] if prophet else None},
            ),
            prophet,
            training_reasons,
            model_strategy,
        )
        fusion_meta = _build_fusion_meta(
            _fetch_one(
                bind,
                "SELECT * FROM prediction_fusion_meta WHERE prediction_record_id = :id",
                {"id": record["id"]},
            ),
            fusion_reasons,
        )
        recommendations = _build_recommendations(
            _fetch_all(
                bind,
                "SELECT * FROM prediction_recommendations WHERE prediction_record_id = :id ORDER BY sort_order ASC, id ASC",
                {"id": record["id"]},
            )
        )
        cache_mode = "model_reuse" if model_strategy == "reuse_existing_model" else "fresh_train"
        data_days_used = prophet["data_days_used"] if prophet else None
        confidence_level = training_meta.get("confidence_level")
        anomaly_flags = _build_anomaly_flags(
            risk_level=record["risk_level"],
            confidence_level=confidence_level,
            data_days_used=data_days_used,
            input_data=input_snapshot,
            bp_forecast=forecast,
            recommendations=recommendations,
        )
        bind.execute(
            text(
                """
                UPDATE prediction_records
                SET
                    data_days_used = :data_days_used,
                    confidence_level = :confidence_level,
                    cache_mode = :cache_mode,
                    has_anomaly = :has_anomaly,
                    input_snapshot = :input_snapshot,
                    fusion_meta = :fusion_meta,
                    bp_forecast = :bp_forecast,
                    training_meta = :training_meta,
                    recommendations = :recommendations,
                    anomaly_flags = :anomaly_flags
                WHERE id = :id
                """
            ),
            {
                "id": record["id"],
                "data_days_used": data_days_used,
                "confidence_level": confidence_level,
                "cache_mode": cache_mode,
                "has_anomaly": bool(anomaly_flags),
                "input_snapshot": _json(input_snapshot),
                "fusion_meta": _json(fusion_meta),
                "bp_forecast": _json(forecast),
                "training_meta": _json(training_meta),
                "recommendations": _json(recommendations),
                "anomaly_flags": _json(anomaly_flags),
            },
        )


def _build_input_snapshot(row, prophet):
    if not row:
        return None
    cache_key = prophet["cache_key"] if prophet else None
    return {
        "age": row["age"],
        "male": row["male"],
        "currentSmoker": row["current_smoker"],
        "cigsPerDay": row["cigs_per_day"],
        "BPMeds": row["bp_meds"],
        "diabetes": row["diabetes"],
        "totChol": row["tot_chol"],
        "sysBP": row["sys_bp"],
        "diaBP": row["dia_bp"],
        "BMI": row["bmi"],
        "heartRate": row["heart_rate"],
        "glucose": row["glucose"],
        "_tot_chol_filled": row["tot_chol"] is not None,
        "_glucose_filled": row["glucose"] is not None,
        "_model_state_snapshot": None,
        "_cache_snapshot": None,
        "_prediction_run_key": cache_key,
        "_prophet_cache_key": cache_key,
    }


def _build_forecast(rows):
    return [
        {
            "day": row["forecast_day"],
            "systolic": row["systolic"],
            "diastolic": row["diastolic"],
            "systolic_lower": row["systolic_lower"],
            "systolic_upper": row["systolic_upper"],
            "diastolic_lower": row["diastolic_lower"],
            "diastolic_upper": row["diastolic_upper"],
        }
        for row in rows
    ]


def _build_training_meta(row, prophet, confidence_reasons, model_strategy):
    meta = {
        "aggregation_mode": "daily_mean",
        "parameter_profile": "standard",
        "seasonality": {"weekly_enabled": False, "monthly_enabled": False},
        "avg_measurements_per_day": None,
        "recent_sys_range_mean": None,
        "recent_dia_range_mean": None,
        "confidence_level": None,
        "confidence_reasons": confidence_reasons,
        "forecast_days": prophet["forecast_days"] if prophet else 7,
        "total_history_days": prophet["total_history_days"] if prophet else None,
        "history_window_capped": prophet["history_window_capped"] if prophet else None,
        "data_range": prophet["data_range"] if prophet else None,
    }
    if row:
        meta.update(
            {
                "aggregation_mode": row["aggregation_mode"],
                "parameter_profile": row["parameter_profile"],
                "seasonality": {
                    "weekly_enabled": bool(row["weekly_enabled"]),
                    "monthly_enabled": bool(row["monthly_enabled"]),
                },
                "avg_measurements_per_day": row["avg_measurements_per_day"],
                "recent_sys_range_mean": row["recent_sys_range_mean"],
                "recent_dia_range_mean": row["recent_dia_range_mean"],
                "confidence_level": row["confidence_level"],
            }
        )
    if model_strategy:
        meta["model_strategy"] = model_strategy
    return meta


def _build_fusion_meta(row, fusion_reasons):
    if not row:
        return {"reasons": fusion_reasons}
    raw_probability = row["raw_probability"]
    fused_probability = row["fused_probability"]
    medication_adjustment = row["medication_adjustment"]
    adjustment = round(fused_probability - raw_probability, 4)
    return {
        "raw_probability": raw_probability,
        "fused_probability": fused_probability,
        "bp_meds_input": row["bp_meds_input"],
        "bp_meds_model_value": row["bp_meds_model_value"],
        "bp_meds_policy": row["bp_meds_policy"],
        "medication_adjustment": medication_adjustment,
        "trend_adjustment": round(adjustment - medication_adjustment, 4),
        "adjustment": adjustment,
        "reasons": fusion_reasons,
    }


def _build_recommendations(rows):
    cards = {}
    order = []
    for row in rows:
        topic = "follow_up" if row["category"] == "guideline_payload" else row["category"]
        if topic not in cards:
            cards[topic] = {
                "topic": topic,
                "summary": "",
                "reason": "",
                "actions": [],
                "source_label": "",
            }
            order.append(topic)
        if row["title"] == "summary":
            cards[topic]["summary"] = row["content"]
        elif row["title"] == "reason":
            cards[topic]["reason"] = row["content"]
        elif row["title"] == "action":
            cards[topic]["actions"].append(row["content"])
        elif row["title"] == "source_label":
            cards[topic]["source_label"] = row["content"]
    return [cards[topic] for topic in order]


def _build_anomaly_flags(
    *,
    risk_level,
    confidence_level,
    data_days_used,
    input_data,
    bp_forecast,
    recommendations,
):
    flags = []
    high_risk = str(risk_level or "").strip().lower() in {"高风险", "high"}
    low_risk = str(risk_level or "").strip().lower() in {"低风险", "low"}
    if high_risk and not recommendations:
        flags.append("high_risk_without_recommendation")
    if high_risk and str(confidence_level or "").strip().lower() == "low":
        flags.append("high_risk_low_confidence")
    if data_days_used is not None and data_days_used < 3:
        flags.append("insufficient_data_prediction")
    if _has_missing_key_profile_fields(input_data):
        flags.append("missing_key_profile_fields")
    if low_risk and _has_elevated_forecast(bp_forecast):
        flags.append("elevated_forecast_low_risk")
    return flags


def _has_missing_key_profile_fields(input_data):
    if not input_data:
        return False
    key_fields = ("age", "BMI", "currentSmoker", "BPMeds", "diabetes", "totChol", "glucose")
    if any(input_data.get(field) is None for field in key_fields):
        return True
    return input_data.get("currentSmoker") in (1, "1", True) and input_data.get("cigsPerDay") is None


def _has_elevated_forecast(bp_forecast):
    for point in bp_forecast or []:
        if point.get("systolic") is not None and point["systolic"] >= 140:
            return True
        if point.get("diastolic") is not None and point["diastolic"] >= 90:
            return True
    return False


def _fetch_one(bind, query, params):
    return bind.execute(text(query), params).mappings().first()


def _fetch_all(bind, query, params):
    return bind.execute(text(query), params).mappings().all()


def _json(value):
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def _has_table(bind, table_name):
    return inspect(bind).has_table(table_name)


def _has_column(bind, table_name, column_name):
    return column_name in {column["name"] for column in inspect(bind).get_columns(table_name)}


def _drop_fk_if_exists(batch_op, bind, table_name, fk_name):
    names = {fk["name"] for fk in inspect(bind).get_foreign_keys(table_name)}
    if fk_name in names:
        batch_op.drop_constraint(fk_name, type_="foreignkey")


def _drop_index_if_exists(batch_op, bind, table_name, index_name):
    names = {index["name"] for index in inspect(bind).get_indexes(table_name)}
    if index_name in names:
        batch_op.drop_index(index_name)
