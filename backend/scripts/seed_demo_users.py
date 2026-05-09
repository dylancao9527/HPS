from datetime import timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from extensions import db
from models import BPRecord, User, UserProfile, UserRiskFactorProfile
from utils.time_utils import utc_now_naive


DEMO_PASSWORD = "Demo@123456"
DEMO_USER_PREFIX = "demo_showcase_"
LEGACY_DEMO_PREFIXES = ("demo_compare_", DEMO_USER_PREFIX)

DEMO_USERS = [
    {
        "username": "demo_showcase_low",
        "email": "demo_showcase_low@example.com",
        "label": "低风险样例",
        "note": "血压长期平稳，适合演示低风险预测和良好记录习惯",
        "bp_days": 21,
        "systolic": 116,
        "diastolic": 74,
        "heart_rate": 68,
        "bp_pattern": [0, 1, -1, 0, 2, -1, 1],
        "profile": {
            "age": 32,
            "male": 0,
            "height": 162,
            "weight": 56,
            "current_smoker": 0,
            "cigs_per_day": 0,
            "bp_meds": 0,
            "diabetes": 0,
            "tot_chol": 168,
            "glucose": 88,
            "diagnosis": "No",
        },
    },
    {
        "username": "demo_showcase_rising",
        "email": "demo_showcase_rising@example.com",
        "label": "近期上升样例",
        "note": "最近一周血压抬升，适合演示周健康报告中的趋势变化",
        "bp_days": 21,
        "systolic": 126,
        "diastolic": 80,
        "heart_rate": 74,
        "bp_pattern": [-4, -3, -2, -1, 0, 2, 4],
        "weekly_shift": 8,
        "profile": {
            "age": 48,
            "male": 1,
            "height": 172,
            "weight": 78,
            "current_smoker": 0,
            "cigs_per_day": 0,
            "bp_meds": 0,
            "diabetes": 0,
            "tot_chol": 205,
            "glucose": 96,
            "diagnosis": None,
        },
    },
    {
        "username": "demo_showcase_high",
        "email": "demo_showcase_high@example.com",
        "label": "高风险样例",
        "note": "血压持续偏高，适合演示高风险预测、建议和治理信号",
        "bp_days": 30,
        "systolic": 151,
        "diastolic": 96,
        "heart_rate": 82,
        "bp_pattern": [1, -1, 2, 0, 3, -2, 1],
        "profile": {
            "age": 61,
            "male": 1,
            "height": 170,
            "weight": 86,
            "current_smoker": 1,
            "cigs_per_day": 12,
            "bp_meds": 0,
            "diabetes": 1,
            "tot_chol": 236,
            "glucose": 126,
            "diagnosis": "Yes",
        },
    },
    {
        "username": "demo_showcase_meds",
        "email": "demo_showcase_meds@example.com",
        "label": "用药控制样例",
        "note": "已长期用药且血压控制一般，适合演示风险因素档案中的用药字段",
        "bp_days": 21,
        "systolic": 138,
        "diastolic": 88,
        "heart_rate": 76,
        "bp_pattern": [0, -2, 1, 0, 2, -1, 1],
        "profile": {
            "age": 57,
            "male": 0,
            "height": 158,
            "weight": 66,
            "current_smoker": 0,
            "cigs_per_day": 0,
            "bp_meds": 1,
            "diabetes": 0,
            "tot_chol": 212,
            "glucose": 101,
            "diagnosis": "Yes",
        },
    },
    {
        "username": "demo_showcase_smoker",
        "email": "demo_showcase_smoker@example.com",
        "label": "吸烟风险样例",
        "note": "血压中度偏高且存在吸烟风险因素，适合演示风险因素编辑",
        "bp_days": 14,
        "systolic": 136,
        "diastolic": 86,
        "heart_rate": 80,
        "bp_pattern": [-1, 1, 0, 2, -2, 1, 0],
        "profile": {
            "age": 42,
            "male": 1,
            "height": 176,
            "weight": 82,
            "current_smoker": 1,
            "cigs_per_day": 8,
            "bp_meds": 0,
            "diabetes": 0,
            "tot_chol": 218,
            "glucose": 94,
            "diagnosis": None,
        },
    },
    {
        "username": "demo_showcase_sparse",
        "email": "demo_showcase_sparse@example.com",
        "label": "记录不足样例",
        "note": "血压记录较少，适合演示数据不足提示和补充记录路径",
        "bp_days": 4,
        "systolic": 129,
        "diastolic": 82,
        "heart_rate": 73,
        "bp_pattern": [0, 2, -1, 1],
        "profile": {
            "age": 36,
            "male": 0,
            "height": 165,
            "weight": 62,
            "current_smoker": 0,
            "cigs_per_day": 0,
            "bp_meds": 0,
            "diabetes": 0,
            "tot_chol": None,
            "glucose": None,
            "diagnosis": None,
        },
    },
]


def _demo_user_filter():
    filters = [User.username.like(f"{prefix}%") for prefix in LEGACY_DEMO_PREFIXES]
    query_filter = filters[0]
    for item in filters[1:]:
        query_filter = query_filter | item
    return query_filter


def _bp_offsets(spec, day):
    pattern = spec.get("bp_pattern", [0])
    offset = pattern[day % len(pattern)]
    weekly_shift = spec.get("weekly_shift", 0)
    if weekly_shift and day >= spec["bp_days"] - 7:
        offset += weekly_shift
    return offset


def _diagnosis_label(value):
    return value or "不确定"


def _create_demo_user(spec, now):
    user = User()
    user.username = spec["username"]
    user.email = spec["email"]
    user.set_password(DEMO_PASSWORD)
    db.session.add(user)
    db.session.flush()

    profile_spec = spec["profile"]
    profile = UserProfile(user_id=user.id)
    profile.nickname = spec["label"]
    profile.diagnosis = profile_spec["diagnosis"]
    db.session.add(profile)

    risk_profile = UserRiskFactorProfile(user_id=user.id)
    risk_profile.age = profile_spec["age"]
    risk_profile.male = profile_spec["male"]
    risk_profile.height = profile_spec["height"]
    risk_profile.weight = profile_spec["weight"]
    risk_profile.current_smoker = profile_spec["current_smoker"]
    risk_profile.cigs_per_day = profile_spec["cigs_per_day"]
    risk_profile.bp_meds = profile_spec["bp_meds"]
    risk_profile.diabetes = profile_spec["diabetes"]
    risk_profile.tot_chol = profile_spec["tot_chol"]
    risk_profile.glucose = profile_spec["glucose"]
    db.session.add(risk_profile)

    for day in range(spec["bp_days"]):
        offset = _bp_offsets(spec, day)
        db.session.add(
            BPRecord(
                user_id=user.id,
                systolic_bp=spec["systolic"] + offset,
                diastolic_bp=spec["diastolic"] + round(offset * 0.55, 1),
                heart_rate=spec["heart_rate"] + (day % 3),
                recorded_at=now - timedelta(days=spec["bp_days"] - day - 1),
            )
        )
    return {
        "username": user.username,
        "label": spec["label"],
        "bp_record_days": spec["bp_days"],
        "note": spec["note"],
        "diagnosis": _diagnosis_label(profile.diagnosis),
    }


def seed_demo_users(*, reset_existing=False):
    existing = User.query.filter(_demo_user_filter()).all()
    deleted_existing = len(existing) if reset_existing else 0
    if reset_existing and existing:
        for user in existing:
            db.session.delete(user)
        db.session.flush()

    if existing and not reset_existing:
        return {
            "deleted_existing": 0,
            "created_count": 0,
            "users": [
                {
                    "username": user.username,
                    "label": user.profile.nickname if user.profile else user.username,
                    "bp_record_days": user.bp_records.count(),
                    "diagnosis": _diagnosis_label(
                        user.profile.diagnosis if user.profile else None
                    ),
                    "note": "已存在的展示用户",
                }
                for user in existing
            ],
        }

    now = utc_now_naive()
    created = []
    for spec in DEMO_USERS:
        created.append(_create_demo_user(spec, now))
    db.session.commit()
    return {
        "deleted_existing": deleted_existing,
        "created_count": len(created),
        "users": created,
    }


def main():
    app = create_app({"INIT_ADMIN_ON_STARTUP": False})
    with app.app_context():
        result = seed_demo_users(reset_existing=True)

    print("展示用户生成完成：")
    print(f"  删除旧 demo 用户数: {result['deleted_existing']}")
    print(f"  新增 demo 用户数: {result['created_count']}")
    print(f"  统一密码: {DEMO_PASSWORD}")
    for item in result["users"]:
        print(
            f"  - {item['username']} ({item['label']}) "
            f"[{item['bp_record_days']} 天记录, 诊断反馈: {item['diagnosis']}] "
            f"{item['note']}"
        )


if __name__ == "__main__":
    main()
