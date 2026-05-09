"""
==============================================================================
普通用户档案模型
==============================================================================
UserProfile 保存展示资料与诊断反馈；UserRiskFactorProfile 保存进入预测
和训练导出的风险因素档案。管理员账号不关联这些表。
==============================================================================
"""

from extensions import db
from training.ml_schema import binary_flag_to_gender, binary_flag_to_yes_no
from utils.time_utils import utc_now_naive


class UserProfile(db.Model):
    """普通用户个人档案主表"""

    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False, unique=True, index=True)

    # ---- 展示信息（不参与模型训练）----
    nickname = db.Column(db.String(50), nullable=True)   # 昵称/真实姓名
    avatar = db.Column(db.Text, nullable=True)           # 头像 Base64（前端压缩 ≤30KB）

    # ---- 诊断反馈（用于 LightGBM 再训练标签来源）----
    # 'Yes' -> 已有高血压诊断反馈 -> 导出 Risk=1
    # 'No'  -> 暂无高血压诊断反馈 -> 导出 Risk=0
    # null  -> 不确定 -> 尝试血压自动标注，否则跳过
    diagnosis = db.Column(db.String(20), nullable=True)

    # ---- 时间戳 ----
    updated_at = db.Column(
        db.DateTime,
        default=utc_now_naive,
        onupdate=utc_now_naive,
    )

    def to_dict(self):
        return {
            'nickname': self.nickname,
            'avatar': self.avatar,
            'diagnosis': self.diagnosis,
        }


class UserRiskFactorProfile(db.Model):
    """普通用户风险因素档案表"""

    __tablename__ = 'user_risk_factor_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False, unique=True, index=True)

    # ---- 基本信息 ----
    age = db.Column(db.Float, nullable=True)            # 年龄
    male = db.Column(db.Integer, nullable=True)         # 1=Male, 0=Female

    # ---- 身体指标 ----
    height = db.Column(db.Float, nullable=True)         # 身高 cm
    weight = db.Column(db.Float, nullable=True)         # 体重 kg

    # ---- 风险特征 ----
    current_smoker = db.Column(db.Integer, nullable=True)   # 1=Yes, 0=No
    cigs_per_day = db.Column(db.Float, nullable=True)       # 日吸烟支数
    bp_meds = db.Column(db.Integer, nullable=True)          # 是否服用降压药
    diabetes = db.Column(db.Integer, nullable=True)         # 是否糖尿病

    # ---- 化验指标（选填）----
    tot_chol = db.Column(db.Float, nullable=True)       # 总胆固醇 mg/dL
    glucose = db.Column(db.Float, nullable=True)        # 血糖 mg/dL

    # ---- 时间戳 ----
    updated_at = db.Column(
        db.DateTime,
        default=utc_now_naive,
        onupdate=utc_now_naive,
    )

    @property
    def bmi(self):
        """BMI = 体重(kg) / 身高(m)²"""
        if self.height and self.weight and self.height > 0:
            return round(self.weight / (self.height / 100) ** 2, 1)
        return None

    @property
    def profile_complete(self):
        """基本信息是否填写完毕（预测所需最低要求）"""
        return all([
            self.age is not None,
            self.male is not None,
            self.height is not None,
            self.weight is not None,
        ])

    def to_dict(self):
        gender = binary_flag_to_gender(self.male)
        smoking = binary_flag_to_yes_no(self.current_smoker)
        return {
            'age': self.age,
            'male': self.male,
            'gender': gender,
            'height': self.height,
            'weight': self.weight,
            'bmi': self.bmi,
            'current_smoker': self.current_smoker,
            'cigs_per_day': self.cigs_per_day,
            'bp_meds': self.bp_meds,
            'diabetes': self.diabetes,
            'smoking': smoking,
            'tot_chol': self.tot_chol,
            'cholesterol': self.tot_chol,
            'glucose': self.glucose,
            'profile_complete': self.profile_complete,
        }
