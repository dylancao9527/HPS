from datetime import timedelta

from extensions import db
from utils.time_utils import utc_now_naive

from models import UserProphetModel


class ProphetModelRepository:
    def get_active_prophet_model(self, user_id):
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
            trained_at=payload["trained_at"],
            trained_until=payload["trained_until"],
            storage_key=payload["storage_key"],
            is_active=True,
        )
        db.session.add(row)
        db.session.commit()
        return row

    def list_prophet_storage_keys(self) -> list[str]:
        rows = UserProphetModel.query.filter(
            UserProphetModel.storage_key.isnot(None)
        ).all()
        return [row.storage_key for row in rows if row.storage_key]

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
