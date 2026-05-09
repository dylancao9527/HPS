from extensions import db
from models import UserProfile, UserRiskFactorProfile
from services.profile_contract import (
    UPDATABLE_RISK_FACTOR_FIELDS,
    UPDATABLE_PROFILE_FIELDS,
    ProfilePayloadNormalizer,
    coerce_profile_field,
)


class ProfileService:
    def __init__(self, normalizer=None):
        self.normalizer = normalizer or ProfilePayloadNormalizer()

    def update_profile(self, user, data):
        if not data:
            return {"error": "无数据"}, 400

        try:
            data = self.normalizer.normalize(data)
            self.normalizer.validate_ranges(data)
        except ValueError as exc:
            return {"error": str(exc)}, 400

        avatar_val = data.get("avatar")
        if avatar_val and len(avatar_val) > 100 * 1024:
            return {"error": "头像文件过大（上限 100KB）"}, 400

        profile = self._ensure_profile(user, data)
        risk_factor_profile = self._ensure_risk_factor_profile(user, data)

        if profile:
            self._apply_fields(profile, data, UPDATABLE_PROFILE_FIELDS)

        if risk_factor_profile:
            self._apply_fields(
                risk_factor_profile,
                data,
                UPDATABLE_RISK_FACTOR_FIELDS,
            )
            if risk_factor_profile.current_smoker == 0:
                risk_factor_profile.cigs_per_day = 0.0
            elif (
                risk_factor_profile.current_smoker is None
                and risk_factor_profile.cigs_per_day in ("", None)
            ):
                risk_factor_profile.cigs_per_day = None

        try:
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            return {"error": f"保存失败: {str(exc)}"}, 500

        return {
            "message": "档案已更新",
            "profile": user.to_dict(),
        }

    def _ensure_profile(self, user, data):
        if not any(field in data for field in UPDATABLE_PROFILE_FIELDS):
            return None
        profile = user.profile
        if not profile:
            profile = UserProfile(user_id=user.id)
            user.profile = profile
            db.session.add(profile)
        return profile

    def _ensure_risk_factor_profile(self, user, data):
        if not any(field in data for field in UPDATABLE_RISK_FACTOR_FIELDS):
            return None
        risk_factor_profile = getattr(user, "risk_factor_profile", None)
        if not risk_factor_profile:
            risk_factor_profile = UserRiskFactorProfile(user_id=user.id)
            user.risk_factor_profile = risk_factor_profile
            db.session.add(risk_factor_profile)
        return risk_factor_profile

    def _apply_fields(self, target, data, fields):
        for field in fields:
            if field in data:
                setattr(target, field, coerce_profile_field(field, data[field]))
