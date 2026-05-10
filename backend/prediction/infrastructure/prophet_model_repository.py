from datetime import timedelta

from extensions import db
from sqlalchemy import inspect, text
from utils.time_utils import utc_now_naive

from models import UserProphetModel


class ProphetModelRepository:
    def get_active_prophet_model(self, user_id, forecast_days=None):
        return (
            UserProphetModel.query.filter_by(
                user_id=user_id,
                is_active=True,
            )
            .order_by(UserProphetModel.trained_at.desc(), UserProphetModel.id.desc())
            .first()
        )

    def save_user_prophet_model(self, payload):
        UserProphetModel.query.filter_by(
            user_id=payload["user_id"],
            is_active=True,
        ).update({"is_active": False}, synchronize_session=False)

        row = UserProphetModel(
            user_id=payload["user_id"],
            model_version=payload["model_version"],
            data_signature=payload["data_signature"],
            aggregation_mode=payload["aggregation_mode"],
            trained_at=payload["trained_at"],
            trained_until=payload["trained_until"],
            data_days_used=payload["data_days_used"],
            total_history_days=payload["total_history_days"],
            history_window_capped=payload["history_window_capped"],
            parameter_profile=payload["parameter_profile"],
            weekly_enabled=payload["weekly_enabled"],
            monthly_enabled=payload["monthly_enabled"],
            storage_key=payload["storage_key"],
            is_active=True,
        )
        db.session.add(row)
        db.session.commit()
        return row

    def list_prophet_models_with_legacy_blobs(self, *, limit: int):
        columns = {
            column["name"]
            for column in inspect(db.engine).get_columns("user_prophet_models")
        }
        if "sys_model_blob" not in columns or "dia_model_blob" not in columns:
            return []
        return db.session.execute(
            text(
                """
                SELECT
                    id,
                    user_id,
                    model_version,
                    data_signature,
                    sys_model_blob,
                    dia_model_blob
                FROM user_prophet_models
                WHERE storage_key IS NULL
                  AND sys_model_blob IS NOT NULL
                  AND dia_model_blob IS NOT NULL
                ORDER BY id ASC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()

    def update_prophet_storage_key(self, *, row_id: int, storage_key: str):
        db.session.execute(
            text(
                "UPDATE user_prophet_models SET storage_key = :storage_key WHERE id = :row_id"
            ),
            {"storage_key": storage_key, "row_id": row_id},
        )

    def list_prophet_storage_keys(self) -> list[str]:
        rows = UserProphetModel.query.filter(
            UserProphetModel.storage_key.isnot(None)
        ).all()
        return [row.storage_key for row in rows if row.storage_key]

    def commit(self):
        db.session.commit()

    def prune_inactive_prophet_models(
        self, *, keep_inactive_per_slot: int, max_inactive_age_hours: int
    ):
        cutoff = utc_now_naive() - timedelta(hours=max_inactive_age_hours)
        rows = (
            UserProphetModel.query.filter_by(is_active=False)
            .order_by(
                UserProphetModel.user_id.asc(),
                UserProphetModel.trained_at.desc(),
                UserProphetModel.id.desc(),
            )
            .all()
        )
        kept: dict[int, int] = {}
        deleted = []
        for row in rows:
            slot = row.user_id
            slot_kept = kept.get(slot, 0)
            if slot_kept < keep_inactive_per_slot and row.trained_at >= cutoff:
                kept[slot] = slot_kept + 1
                continue
            deleted.append(row)
        deleted_storage_keys = [row.storage_key for row in deleted if row.storage_key]
        for row in deleted:
            db.session.delete(row)
        db.session.commit()
        return deleted_storage_keys
