import json
from dataclasses import dataclass
from math import ceil

from sqlalchemy import false, func, or_

from extensions import db
from models import PredictionRecord
from prediction.domain.governance_policy import (
    build_anomaly_flags,
    build_governance_summary,
    is_high_risk,
)
from prediction.domain.trend_policy import summarize_forecast_trend


KNOWN_ANOMALY_TYPES = (
    "high_risk_without_recommendation",
    "high_risk_low_confidence",
    "insufficient_data_prediction",
    "missing_key_profile_fields",
    "elevated_forecast_low_risk",
)


@dataclass(frozen=True)
class GovernanceQuery:
    page: int = 1
    per_page: int = 20
    risk_level: str = ""
    confidence_level: str = ""
    has_anomaly: bool | None = None
    anomaly_type: str = ""

    @classmethod
    def from_filters(
        cls,
        *,
        page=1,
        per_page=20,
        risk_level="",
        confidence_level="",
        has_anomaly=None,
        anomaly_type="",
    ):
        return cls(
            page=page if page > 0 else 1,
            per_page=per_page if per_page > 0 else 20,
            risk_level=(risk_level or "").strip(),
            confidence_level=(confidence_level or "").strip(),
            has_anomaly=has_anomaly,
            anomaly_type=(anomaly_type or "").strip(),
        )

    @property
    def needs_anomaly_projection_filter(self):
        return self.has_anomaly is not None or bool(self.anomaly_type)


class GovernanceProjection:
    def __init__(self, payload_assembler):
        self.payload_assembler = payload_assembler

    def assemble_record(self, item, prophet_record=None):
        payload = self.payload_assembler.assemble_prediction_payload(
            item,
            prophet_record=prophet_record,
        )
        payload["anomaly_flags"] = build_anomaly_flags(payload)
        return payload

    @staticmethod
    def build_list_row(row):
        return {
            "prediction_id": row.get("prediction_id"),
            "risk_level": row.get("risk_level"),
            "risk_probability": row.get("risk_probability"),
            "confidence_level": row.get("confidence_level"),
            "data_days_used": row.get("data_days_used"),
            "input_data": row.get("input_data") or {},
            "anomaly_flags": row.get("anomaly_flags") or [],
            "created_at": row.get("created_at"),
        }

    @staticmethod
    def build_detail(row):
        return {
            "prediction_id": row.get("prediction_id"),
            "risk_level": row.get("risk_level"),
            "risk_probability": row.get("risk_probability"),
            "confidence_level": row.get("confidence_level"),
            "data_days_used": row.get("data_days_used"),
            "input_data": row.get("input_data") or {},
            "fusion_meta": row.get("fusion_meta") or {},
            "forecast_summary": summarize_forecast_trend(row.get("bp_forecast") or [])
            if row.get("bp_forecast")
            else {},
            "confidence_reasons": row.get("confidence_reasons") or [],
            "recommendations": row.get("recommendations") or [],
            "anomaly_flags": row.get("anomaly_flags") or [],
            "created_at": row.get("created_at"),
        }


class PredictionGovernanceReadModel:
    def __init__(self, *, payload_assembler, projection=None):
        self.projection = projection or GovernanceProjection(payload_assembler)

    @staticmethod
    def is_high_risk(risk_level):
        return is_high_risk(risk_level)

    @staticmethod
    def build_anomaly_flags(payload):
        return build_anomaly_flags(payload)

    @staticmethod
    def high_risk_condition():
        return or_(
            PredictionRecord.risk_level == "高风险",
            func.lower(func.trim(PredictionRecord.risk_level)) == "high",
        )

    @staticmethod
    def low_risk_condition():
        return or_(
            PredictionRecord.risk_level == "低风险",
            func.lower(func.trim(PredictionRecord.risk_level)) == "low",
        )

    @staticmethod
    def low_confidence_condition():
        return func.lower(func.trim(PredictionRecord.confidence_level)) == "low"

    @staticmethod
    def without_recommendation_condition():
        return PredictionGovernanceReadModel.anomaly_flag_condition(
            "high_risk_without_recommendation"
        )

    @staticmethod
    def insufficient_data_condition():
        return PredictionGovernanceReadModel.anomaly_flag_condition(
            "insufficient_data_prediction"
        )

    @staticmethod
    def missing_key_profile_fields_condition():
        return PredictionGovernanceReadModel.anomaly_flag_condition(
            "missing_key_profile_fields"
        )

    @staticmethod
    def elevated_forecast_condition():
        return PredictionGovernanceReadModel.anomaly_flag_condition(
            "elevated_forecast_low_risk"
        )

    @staticmethod
    def model_reuse_condition():
        return PredictionRecord.cache_mode == "model_reuse"

    @staticmethod
    def anomaly_flag_condition(anomaly_type):
        anomaly_type = (anomaly_type or "").strip()
        if not anomaly_type:
            return false()
        return (
            func.json_contains(
                PredictionRecord.anomaly_flags,
                json.dumps(anomaly_type),
                "$",
            )
            == 1
        )

    @classmethod
    def anomaly_conditions(cls):
        return {
            anomaly_type: cls.anomaly_flag_condition(anomaly_type)
            for anomaly_type in KNOWN_ANOMALY_TYPES
        }

    @classmethod
    def anomaly_condition_for_type(cls, anomaly_type):
        anomaly_type = (anomaly_type or "").strip()
        if not anomaly_type:
            return None
        return cls.anomaly_conditions().get(anomaly_type, false())

    @classmethod
    def any_anomaly_condition(cls):
        return PredictionRecord.has_anomaly.is_(True)

    def governance_base_query(self):
        return PredictionRecord.query.order_by(PredictionRecord.created_at.desc())

    @staticmethod
    def apply_governance_filters(query, *, risk_level="", confidence_level=""):
        risk_level = (risk_level or "").strip()
        confidence_level = (confidence_level or "").strip()

        if risk_level:
            query = query.filter(PredictionRecord.risk_level == risk_level)
        if confidence_level:
            query = query.filter(PredictionRecord.confidence_level == confidence_level)

        return query

    @classmethod
    def apply_anomaly_filters(
        cls,
        query,
        *,
        has_anomaly=None,
        anomaly_type="",
    ):
        anomaly_type = (anomaly_type or "").strip()
        if anomaly_type:
            query = query.filter(cls.anomaly_condition_for_type(anomaly_type))

        if has_anomaly is True:
            query = query.filter(cls.any_anomaly_condition())
        elif has_anomaly is False:
            query = query.filter(~cls.any_anomaly_condition())

        return query

    @staticmethod
    def filter_by_anomaly_state(rows, *, has_anomaly=None, anomaly_type=""):
        anomaly_type = (anomaly_type or "").strip()
        filtered = []
        for row in rows:
            flags = row.get("anomaly_flags") or []
            if anomaly_type and anomaly_type not in flags:
                continue
            if has_anomaly is True and not flags:
                continue
            if has_anomaly is False and flags:
                continue
            filtered.append(row)
        return filtered

    @staticmethod
    def paginate_rows(rows, *, page, per_page):
        total = len(rows)
        pages = ceil(total / per_page) if total else 0
        start = (page - 1) * per_page
        end = start + per_page
        return rows[start:end], total, pages

    def _filtered_query(self, governance_query):
        return self.apply_governance_filters(
            self.governance_base_query(),
            risk_level=governance_query.risk_level,
            confidence_level=governance_query.confidence_level,
        )

    def _project_records(self, items):
        return [self.projection.assemble_record(item) for item in items]

    @staticmethod
    def _is_in_memory_query(query):
        return hasattr(query, "items")

    @staticmethod
    def _distribution_from_rows(rows):
        distribution = {}
        for key, count in rows:
            distribution[key or "unknown"] = count
        return distribution

    @staticmethod
    def _count_predictions_where(*conditions):
        query = PredictionRecord.query
        for condition in conditions:
            query = query.filter(condition)
        return query.count()

    def _build_summary_from_database(self):
        total_predictions = self._count_predictions_where()
        risk_distribution = self._distribution_from_rows(
            db.session.query(
                PredictionRecord.risk_level,
                func.count(PredictionRecord.id),
            )
            .group_by(PredictionRecord.risk_level)
            .all()
        )
        confidence_distribution = self._distribution_from_rows(
            db.session.query(
                PredictionRecord.confidence_level,
                func.count(PredictionRecord.id),
            )
            .group_by(PredictionRecord.confidence_level)
            .all()
        )
        anomaly_counts = {
            anomaly_type: self._count_predictions_where(
                self.anomaly_condition_for_type(anomaly_type)
            )
            for anomaly_type in KNOWN_ANOMALY_TYPES
        }
        high_risk_predictions = self._count_predictions_where(
            self.high_risk_condition()
        )
        low_confidence_predictions = self._count_predictions_where(
            self.low_confidence_condition()
        )
        insufficient_data_predictions = anomaly_counts[
            "insufficient_data_prediction"
        ]
        anomaly_predictions = self._count_predictions_where(
            self.any_anomaly_condition()
        )
        prophet_model_reuse_count = self._count_predictions_where(
            self.model_reuse_condition()
        )
        return {
            "total_predictions": total_predictions,
            "risk_distribution": risk_distribution,
            "confidence_distribution": confidence_distribution,
            "anomaly_counts": anomaly_counts,
            "high_risk_predictions": high_risk_predictions,
            "low_confidence_predictions": low_confidence_predictions,
            "low_confidence_rate": round(
                low_confidence_predictions / total_predictions,
                4,
            )
            if total_predictions
            else 0,
            "anomaly_predictions": anomaly_predictions,
            "insufficient_data_predictions": insufficient_data_predictions,
            "prophet_model_reuse_count": prophet_model_reuse_count,
            "prophet_model_retrain_count": (
                total_predictions - prophet_model_reuse_count
            ),
        }

    def get_summary(self):
        try:
            return self._build_summary_from_database()
        except RuntimeError as exc:
            if "Working outside of application context" not in str(exc):
                raise
            records = self._project_records(self.governance_base_query().all())
            return build_governance_summary(records)

    def list_predictions(
        self,
        *,
        page,
        per_page,
        risk_level="",
        confidence_level="",
        has_anomaly=None,
        anomaly_type="",
    ):
        governance_query = GovernanceQuery.from_filters(
            page=page,
            per_page=per_page,
            risk_level=risk_level,
            confidence_level=confidence_level,
            has_anomaly=has_anomaly,
            anomaly_type=anomaly_type,
        )
        query = self._filtered_query(governance_query)
        if governance_query.needs_anomaly_projection_filter:
            if self._is_in_memory_query(query):
                assembled = self._project_records(query.all())
                filtered = self.filter_by_anomaly_state(
                    assembled,
                    has_anomaly=governance_query.has_anomaly,
                    anomaly_type=governance_query.anomaly_type,
                )
                page_rows, total, pages = self.paginate_rows(
                    filtered,
                    page=governance_query.page,
                    per_page=governance_query.per_page,
                )
                return {
                    "records": [
                        self.projection.build_list_row(row) for row in page_rows
                    ],
                    "total": total,
                    "page": governance_query.page,
                    "pages": pages,
                }
            query = self.apply_anomaly_filters(
                query,
                has_anomaly=governance_query.has_anomaly,
                anomaly_type=governance_query.anomaly_type,
            )

        pagination = query.paginate(
            page=governance_query.page,
            per_page=governance_query.per_page,
            error_out=False,
        )
        return {
            "records": [
                self.projection.build_list_row(row)
                for row in self._project_records(pagination.items)
            ],
            "total": pagination.total,
            "page": governance_query.page,
            "pages": pagination.pages,
        }

    def list_predictions_for_export(
        self,
        *,
        risk_level="",
        confidence_level="",
        has_anomaly=None,
        anomaly_type="",
    ):
        governance_query = GovernanceQuery.from_filters(
            risk_level=risk_level,
            confidence_level=confidence_level,
            has_anomaly=has_anomaly,
            anomaly_type=anomaly_type,
        )
        query = self._filtered_query(governance_query)
        if governance_query.needs_anomaly_projection_filter:
            if self._is_in_memory_query(query):
                rows = self._project_records(query.all())
                return self.filter_by_anomaly_state(
                    rows,
                    has_anomaly=governance_query.has_anomaly,
                    anomaly_type=governance_query.anomaly_type,
                )
            query = self.apply_anomaly_filters(
                query,
                has_anomaly=governance_query.has_anomaly,
                anomaly_type=governance_query.anomaly_type,
            )
        return self._project_records(query.all())

    def get_prediction_detail(self, prediction_id):
        item = (
            self.governance_base_query()
            .filter(PredictionRecord.id == prediction_id)
            .first()
        )
        if not item:
            return None
        return self.projection.build_detail(self.projection.assemble_record(item))
