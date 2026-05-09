from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from .ml_schema import LABEL_SOURCE_COLUMN, profile_to_model_feature_row
from extensions import db
from models import BPRecord, User, UserProfile, UserRiskFactorProfile
from sqlalchemy import case, func, or_


@dataclass(frozen=True)
class TrainingExportSample:
    row: dict
    label: int
    label_source: str


@dataclass(frozen=True)
class TrainingExportProjection:
    user_id: int
    profile: object | None
    risk_factor_profile: object | None
    recent_bp: dict | None
    total_bp_count: int
    high_bp_count: int


@dataclass(frozen=True)
class TrainingExportBatch:
    total_users: int
    samples: list[TrainingExportSample]


def calculate_recent_bp_averages(user_id, recent_count, *, bp_record_model=None):
    bp_record_model = bp_record_model or BPRecord
    recent_records = (
        bp_record_model.query.filter_by(user_id=user_id)
        .order_by(bp_record_model.recorded_at.desc())
        .limit(recent_count)
        .all()
    )

    if not recent_records:
        return None

    avg_sys = sum(r.systolic_bp for r in recent_records) / len(recent_records)
    avg_dia = sum(r.diastolic_bp for r in recent_records) / len(recent_records)

    heart_rates = [r.heart_rate for r in recent_records if r.heart_rate is not None]
    avg_hr = sum(heart_rates) / len(heart_rates) if heart_rates else None

    return {
        "systolic": round(avg_sys, 2),
        "diastolic": round(avg_dia, 2),
        "heart_rate": round(avg_hr, 2) if avg_hr is not None else None,
        "count_used": len(recent_records),
    }


def determine_training_label(user_id, profile, *, bp_record_model=None):
    bp_record_model = bp_record_model or BPRecord
    if profile.diagnosis == "Yes":
        return 1, "diagnosis"
    if profile.diagnosis == "No":
        return 0, "diagnosis"

    high_bp_count = (
        bp_record_model.query.filter(
            bp_record_model.user_id == user_id,
        )
        .filter(
            or_(
                bp_record_model.systolic_bp >= 140,
                bp_record_model.diastolic_bp >= 90,
            )
        )
        .count()
    )
    total_bp = bp_record_model.query.filter_by(user_id=user_id).count()

    if high_bp_count >= 3:
        return 1, "rule"
    if total_bp >= 3:
        return 0, "rule"
    return None


def determine_training_label_from_counts(profile, *, total_bp_count, high_bp_count):
    diagnosis = getattr(profile, "diagnosis", None)
    if diagnosis == "Yes":
        return 1, "diagnosis"
    if diagnosis == "No":
        return 0, "diagnosis"

    if high_bp_count >= 3:
        return 1, "rule"
    if total_bp_count >= 3:
        return 0, "rule"
    return None


def build_training_export_sample_from_projection(projection):
    profile = projection.profile
    risk_profile = projection.risk_factor_profile
    if not risk_profile or not risk_profile.profile_complete:
        return None

    bp_avg = projection.recent_bp
    if not bp_avg:
        return None

    label_result = determine_training_label_from_counts(
        profile,
        total_bp_count=projection.total_bp_count,
        high_bp_count=projection.high_bp_count,
    )
    if label_result is None:
        return None

    label, label_source = label_result
    cigs_per_day = risk_profile.cigs_per_day
    if risk_profile.current_smoker == 0:
        cigs_per_day = 0
    elif cigs_per_day == "":
        cigs_per_day = None

    row = profile_to_model_feature_row(
        age=risk_profile.age,
        male=risk_profile.male,
        bmi=risk_profile.bmi,
        current_smoker=risk_profile.current_smoker,
        cigs_per_day=cigs_per_day,
        bp_meds=risk_profile.bp_meds,
        diabetes=risk_profile.diabetes,
        tot_chol=risk_profile.tot_chol,
        sys_bp=bp_avg["systolic"],
        dia_bp=bp_avg["diastolic"],
        heart_rate=bp_avg["heart_rate"],
        glucose=risk_profile.glucose,
    )
    row[LABEL_SOURCE_COLUMN] = label_source
    row["Risk"] = label
    return TrainingExportSample(
        row=row,
        label=label,
        label_source=label_source,
    )


def build_training_export_sample(user, recent_bp_avg_count, *, bp_record_model=None):
    profile = user.profile
    risk_profile = getattr(user, "risk_factor_profile", None) or profile
    if not risk_profile or not risk_profile.profile_complete:
        return None

    bp_avg = calculate_recent_bp_averages(
        user.id,
        recent_bp_avg_count,
        bp_record_model=bp_record_model,
    )
    if not bp_avg:
        return None

    label_result = determine_training_label(
        user.id,
        profile,
        bp_record_model=bp_record_model,
    )
    if label_result is None:
        return None

    label, label_source = label_result
    cigs_per_day = risk_profile.cigs_per_day
    if risk_profile.current_smoker == 0:
        cigs_per_day = 0
    elif cigs_per_day == "":
        cigs_per_day = None

    row = profile_to_model_feature_row(
        age=risk_profile.age,
        male=risk_profile.male,
        bmi=risk_profile.bmi,
        current_smoker=risk_profile.current_smoker,
        cigs_per_day=cigs_per_day,
        bp_meds=risk_profile.bp_meds,
        diabetes=risk_profile.diabetes,
        tot_chol=risk_profile.tot_chol,
        sys_bp=bp_avg["systolic"],
        dia_bp=bp_avg["diastolic"],
        heart_rate=bp_avg["heart_rate"],
        glucose=risk_profile.glucose,
    )
    row[LABEL_SOURCE_COLUMN] = label_source
    row["Risk"] = label
    return TrainingExportSample(
        row=row,
        label=label,
        label_source=label_source,
    )


def iter_exportable_training_samples(users, recent_bp_avg_count, *, bp_record_model=None):
    for user in users:
        yield build_training_export_sample(
            user,
            recent_bp_avg_count,
            bp_record_model=bp_record_model,
        )


def _calculate_bmi(height, weight):
    if height and weight and height > 0:
        return round(weight / (height / 100) ** 2, 1)
    return None


def _build_profile_projection(row):
    if row.profile_user_id is None:
        return None

    return SimpleNamespace(
        diagnosis=row.diagnosis,
    )


def _build_risk_factor_projection(row):
    if row.risk_profile_user_id is None:
        return None

    profile_complete = all(
        value is not None for value in (row.age, row.male, row.height, row.weight)
    )
    return SimpleNamespace(
        profile_complete=profile_complete,
        age=row.age,
        male=row.male,
        bmi=_calculate_bmi(row.height, row.weight),
        current_smoker=row.current_smoker,
        cigs_per_day=row.cigs_per_day,
        bp_meds=row.bp_meds,
        diabetes=row.diabetes,
        tot_chol=row.tot_chol,
        glucose=row.glucose,
    )


def _build_recent_bp_projection(row):
    if row.recent_count_used is None:
        return None
    return {
        "systolic": round(float(row.recent_systolic), 2),
        "diastolic": round(float(row.recent_diastolic), 2),
        "heart_rate": round(float(row.recent_heart_rate), 2)
        if row.recent_heart_rate is not None
        else None,
        "count_used": int(row.recent_count_used),
    }


def _recent_bp_average_subquery(bp_record_model, recent_count):
    ranked = db.session.query(
        bp_record_model.user_id.label("user_id"),
        bp_record_model.systolic_bp.label("systolic_bp"),
        bp_record_model.diastolic_bp.label("diastolic_bp"),
        bp_record_model.heart_rate.label("heart_rate"),
        func.row_number()
        .over(
            partition_by=bp_record_model.user_id,
            order_by=bp_record_model.recorded_at.desc(),
        )
        .label("row_number"),
    ).subquery()

    return (
        db.session.query(
            ranked.c.user_id.label("user_id"),
            func.avg(ranked.c.systolic_bp).label("recent_systolic"),
            func.avg(ranked.c.diastolic_bp).label("recent_diastolic"),
            func.avg(ranked.c.heart_rate).label("recent_heart_rate"),
            func.count().label("recent_count_used"),
        )
        .filter(ranked.c.row_number <= recent_count)
        .group_by(ranked.c.user_id)
        .subquery()
    )


def _bp_count_subquery(bp_record_model):
    high_bp_value = case(
        (
            or_(
                bp_record_model.systolic_bp >= 140,
                bp_record_model.diastolic_bp >= 90,
            ),
            1,
        ),
        else_=0,
    )
    return (
        db.session.query(
            bp_record_model.user_id.label("user_id"),
            func.count(bp_record_model.id).label("total_bp_count"),
            func.sum(high_bp_value).label("high_bp_count"),
        )
        .group_by(bp_record_model.user_id)
        .subquery()
    )


def load_training_export_projections(
    recent_bp_avg_count,
    *,
    user_model=None,
    user_profile_model=None,
    risk_factor_profile_model=None,
    bp_record_model=None,
):
    user_model = user_model or User
    user_profile_model = user_profile_model or UserProfile
    risk_factor_profile_model = risk_factor_profile_model or UserRiskFactorProfile
    bp_record_model = bp_record_model or BPRecord

    total_users = user_model.query.count()
    recent_bp = _recent_bp_average_subquery(bp_record_model, recent_bp_avg_count)
    bp_counts = _bp_count_subquery(bp_record_model)
    rows = (
        db.session.query(
            user_model.id.label("user_id"),
            user_profile_model.user_id.label("profile_user_id"),
            user_profile_model.diagnosis.label("diagnosis"),
            risk_factor_profile_model.user_id.label("risk_profile_user_id"),
            risk_factor_profile_model.age.label("age"),
            risk_factor_profile_model.male.label("male"),
            risk_factor_profile_model.height.label("height"),
            risk_factor_profile_model.weight.label("weight"),
            risk_factor_profile_model.current_smoker.label("current_smoker"),
            risk_factor_profile_model.cigs_per_day.label("cigs_per_day"),
            risk_factor_profile_model.bp_meds.label("bp_meds"),
            risk_factor_profile_model.diabetes.label("diabetes"),
            risk_factor_profile_model.tot_chol.label("tot_chol"),
            risk_factor_profile_model.glucose.label("glucose"),
            recent_bp.c.recent_systolic,
            recent_bp.c.recent_diastolic,
            recent_bp.c.recent_heart_rate,
            recent_bp.c.recent_count_used,
            bp_counts.c.total_bp_count,
            bp_counts.c.high_bp_count,
        )
        .select_from(user_model)
        .outerjoin(user_profile_model, user_profile_model.user_id == user_model.id)
        .outerjoin(
            risk_factor_profile_model,
            risk_factor_profile_model.user_id == user_model.id,
        )
        .outerjoin(recent_bp, recent_bp.c.user_id == user_model.id)
        .outerjoin(bp_counts, bp_counts.c.user_id == user_model.id)
        .all()
    )

    projections = [
        TrainingExportProjection(
            user_id=row.user_id,
            profile=_build_profile_projection(row),
            risk_factor_profile=_build_risk_factor_projection(row),
            recent_bp=_build_recent_bp_projection(row),
            total_bp_count=int(row.total_bp_count or 0),
            high_bp_count=int(row.high_bp_count or 0),
        )
        for row in rows
    ]
    return projections, total_users


def build_training_export_batch(
    projections,
    *,
    total_users,
    bp_record_model=None,
):
    _ = bp_record_model
    samples = [
        sample
        for projection in projections
        if (sample := build_training_export_sample_from_projection(projection))
        is not None
    ]
    return TrainingExportBatch(total_users=total_users, samples=samples)


def load_training_export_batch(recent_bp_avg_count):
    projections, total_users = load_training_export_projections(recent_bp_avg_count)
    return build_training_export_batch(
        projections,
        total_users=total_users,
    )
