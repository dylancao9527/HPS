import argparse
import os
import secrets
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
    {
        "username": "shit",
        "email": "shit@example.com",
        "label": "固定登录样例",
        "note": "使用固定密码 A1111111，适合快速登录验证基础流程",
        "password": "A1111111",
        "bp_days": 14,
        "systolic": 122,
        "diastolic": 78,
        "heart_rate": 72,
        "bp_pattern": [0, 1, -1, 2, -2, 0, 1],
        "profile": {
            "age": 39,
            "male": 1,
            "height": 175,
            "weight": 72,
            "current_smoker": 0,
            "cigs_per_day": 0,
            "bp_meds": 0,
            "diabetes": 0,
            "tot_chol": 186,
            "glucose": 91,
            "diagnosis": None,
        },
    },
]


def _demo_user_filter():
    filters = [User.username.like(f"{prefix}%") for prefix in LEGACY_DEMO_PREFIXES]
    filters.extend(User.username == spec["username"] for spec in DEMO_USERS)
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


def _create_demo_user(spec, now, password):
    user = User()
    user.username = spec["username"]
    user.email = spec["email"]
    user.set_password(spec.get("password", password))
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
    created = {
        "username": user.username,
        "label": spec["label"],
        "bp_record_days": spec["bp_days"],
        "note": spec["note"],
        "diagnosis": _diagnosis_label(profile.diagnosis),
    }
    if "password" in spec:
        created["password"] = spec["password"]
    return created


def _summarize_existing_user(user, specs_by_username):
    profile = user.profile
    item = {
        "username": user.username,
        "label": profile.nickname if profile else user.username,
        "bp_record_days": user.bp_records.count(),
        "diagnosis": _diagnosis_label(profile.diagnosis if profile else None),
        "note": "已存在的展示用户",
    }
    spec_password = specs_by_username.get(user.username, {}).get("password")
    if spec_password:
        item["password"] = spec_password
    return item


def seed_demo_users(*, reset_existing=False, password):
    existing = User.query.filter(_demo_user_filter()).all()
    deleted_existing = len(existing) if reset_existing else 0
    if reset_existing and existing:
        for user in existing:
            db.session.delete(user)
        db.session.flush()
        existing = []

    specs_by_username = {spec["username"]: spec for spec in DEMO_USERS}
    existing_usernames = {user.username for user in existing}
    now = utc_now_naive()
    created = []
    for spec in DEMO_USERS:
        if spec["username"] in existing_usernames:
            continue
        created.append(_create_demo_user(spec, now, password))
    if created:
        db.session.commit()
    return {
        "deleted_existing": deleted_existing,
        "created_count": len(created),
        "users": [
            *[
                _summarize_existing_user(user, specs_by_username)
                for user in existing
            ],
            *created,
        ],
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="生成本地演示用户和血压样本")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="实际写入数据库；不传时只输出预览提示",
    )
    parser.add_argument(
        "--reset-existing",
        action="store_true",
        help="删除已有 demo_showcase_/demo_compare_ 前缀用户和脚本中定义的展示用户后重新生成",
    )
    parser.add_argument(
        "--yes-i-understand",
        action="store_true",
        help="确认允许执行删除已有 demo 用户的操作",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("DEMO_USER_PASSWORD"),
        help="显式指定本次生成的 demo 用户密码；也可使用 DEMO_USER_PASSWORD",
    )
    args = parser.parse_args(argv)
    if args.reset_existing and not args.yes_i_understand:
        raise SystemExit("--reset-existing must also pass --yes-i-understand")
    return args


def _generate_demo_password():
    return f"{secrets.token_urlsafe(12)}A1!"


def main(argv=None):
    args = parse_args(argv)
    if not args.apply:
        print("预览模式：不会连接应用或写入数据库。添加 --apply 才会生成 demo 用户。")
        if args.reset_existing:
            print(
                "预览模式：执行时会删除已有 demo_showcase_/demo_compare_ "
                "前缀用户和脚本中定义的展示用户。"
            )
        return

    password = args.password or _generate_demo_password()
    app = create_app({"INIT_ADMIN_ON_STARTUP": False})
    with app.app_context():
        result = seed_demo_users(
            reset_existing=args.reset_existing,
            password=password,
        )

    print("展示用户生成完成：")
    print(f"  删除旧 demo 用户数: {result['deleted_existing']}")
    print(f"  新增 demo 用户数: {result['created_count']}")
    print(f"  本次 demo 用户密码: {password}")
    for item in result["users"]:
        print(
            f"  - {item['username']} ({item['label']}) "
            f"[{item['bp_record_days']} 天记录, 诊断反馈: {item['diagnosis']}] "
            f"{item['note']}"
        )
        if item.get("password"):
            print(f"    固定密码: {item['password']}")


if __name__ == "__main__":
    main()
