from training.ml_schema import normalize_binary_flag


UPDATABLE_PROFILE_FIELDS = [
    "nickname",
    "avatar",
    "diagnosis",
]
UPDATABLE_RISK_FACTOR_FIELDS = [
    "age",
    "male",
    "height",
    "weight",
    "current_smoker",
    "cigs_per_day",
    "bp_meds",
    "diabetes",
    "tot_chol",
    "glucose",
]
NULLABLE_NUMERIC_FIELDS = {
    "age",
    "height",
    "weight",
    "cigs_per_day",
    "tot_chol",
    "glucose",
}
NULLABLE_STRING_FIELDS = {"nickname", "diagnosis"}
BINARY_FIELDS = {"male", "current_smoker", "bp_meds", "diabetes"}

PROFILE_FIELD_ALIASES = {
    "male": ("gender",),
    "current_smoker": ("currentSmoker", "smoking"),
    "cigs_per_day": ("cigsPerDay",),
    "bp_meds": ("BPMeds",),
    "tot_chol": ("totChol", "cholesterol"),
}


def to_optional_float(value, field_name):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name}必须为数字")


def normalize_binary(value, field_name):
    try:
        return normalize_binary_flag(value)
    except ValueError:
        raise ValueError(f"{field_name}取值无效")


def _has_value(data, key):
    return key in data and data[key] is not None


def _normalize_gender_alias(value):
    if value in (None, ""):
        return None
    if value == "Male":
        return 1
    if value == "Female":
        return 0
    raise ValueError("性别取值无效")


def _normalize_smoking_alias(value):
    if value in (None, ""):
        return None
    if value == "Yes":
        return 1
    if value == "No":
        return 0
    return value


def normalize_profile_payload(data):
    normalized = dict(data)
    if "male" not in normalized and _has_value(normalized, "gender"):
        normalized["male"] = _normalize_gender_alias(normalized.get("gender"))

    if "current_smoker" not in normalized and _has_value(normalized, "smoking"):
        normalized["current_smoker"] = _normalize_smoking_alias(
            normalized.get("smoking")
        )

    for canonical, aliases in PROFILE_FIELD_ALIASES.items():
        if canonical in normalized:
            continue
        for alias in aliases:
            if alias in normalized:
                normalized[canonical] = normalized.get(alias)
                break

    normalized.pop("alcohol", None)
    normalized.pop("family_history", None)
    return normalized


def validate_profile_payload(data):
    age = to_optional_float(data.get("age"), "年龄")
    height = to_optional_float(data.get("height"), "身高")
    weight = to_optional_float(data.get("weight"), "体重")
    cigs_per_day = to_optional_float(data.get("cigs_per_day"), "日吸烟支数")
    tot_chol = to_optional_float(data.get("tot_chol"), "总胆固醇")
    glucose = to_optional_float(data.get("glucose"), "血糖")

    checks = [
        (age, 1, 120, "年龄需在 1-120 岁之间"),
        (height, 80, 250, "身高需在 80-250 cm 之间"),
        (weight, 20, 300, "体重需在 20-300 kg 之间"),
        (cigs_per_day, 0, 80, "日吸烟支数需在 0-80 之间"),
        (tot_chol, 50, 500, "总胆固醇需在 50-500 mg/dL 之间"),
        (glucose, 40, 500, "血糖需在 40-500 mg/dL 之间"),
    ]
    for value, lower, upper, message in checks:
        if value is not None and not (lower <= value <= upper):
            raise ValueError(message)

    male = normalize_binary(data.get("male"), "性别")
    current_smoker = normalize_binary(data.get("current_smoker"), "当前是否吸烟")
    bp_meds = normalize_binary(data.get("bp_meds"), "是否服用降压药")
    diabetes = normalize_binary(data.get("diabetes"), "是否患糖尿病")

    diagnosis = data.get("diagnosis")
    if diagnosis not in (None, "", "Yes", "No"):
        raise ValueError("诊断反馈取值无效")

    if current_smoker == 1 and cigs_per_day is not None and cigs_per_day < 0:
        raise ValueError("日吸烟支数需大于等于 0")

    _ = male, bp_meds, diabetes


def coerce_profile_field(field, value):
    if field in NULLABLE_NUMERIC_FIELDS and (value is None or value == ""):
        return None
    if field in NULLABLE_STRING_FIELDS and (value is None or value == ""):
        return None
    if field in BINARY_FIELDS:
        return normalize_binary(value, field)
    if field in NULLABLE_NUMERIC_FIELDS and value is not None:
        return float(value)
    return value


class ProfilePayloadNormalizer:
    def normalize(self, data):
        return normalize_profile_payload(data)

    def validate_ranges(self, data):
        validate_profile_payload(data)
