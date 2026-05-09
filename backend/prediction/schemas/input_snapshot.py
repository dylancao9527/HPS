from dataclasses import dataclass


MODEL_STATE_SNAPSHOT_KEY = "_model_state_snapshot"
PREDICTION_RUN_KEY = "_prediction_run_key"
LEGACY_CACHE_SNAPSHOT_KEY = "_cache_snapshot"
LEGACY_PROPHET_CACHE_KEY = "_prophet_cache_key"


class IncompleteRiskFactorProfileError(ValueError):
    """Raised when a user tries to predict without required risk factors."""


@dataclass(frozen=True)
class PredictionInputSnapshot:
    age: int | None
    male: int | None
    bmi: float | None
    current_smoker: int | None
    cigs_per_day: int | None
    bp_meds: int | None
    diabetes: int | None
    sys_bp: float
    dia_bp: float
    heart_rate: int | None
    tot_chol: float | None
    glucose: float | None

    @classmethod
    def from_user_and_latest_bp(cls, *, user, latest_bp):
        risk_profile = user.risk_factor_profile
        if risk_profile is None or not risk_profile.profile_complete:
            raise IncompleteRiskFactorProfileError("请先完善风险因素档案")
        current_smoker = risk_profile.current_smoker
        return cls(
            age=risk_profile.age,
            male=risk_profile.male,
            bmi=risk_profile.bmi,
            current_smoker=current_smoker,
            cigs_per_day=0 if current_smoker == 0 else risk_profile.cigs_per_day,
            bp_meds=risk_profile.bp_meds,
            diabetes=risk_profile.diabetes,
            sys_bp=latest_bp.systolic_bp if latest_bp else 120,
            dia_bp=latest_bp.diastolic_bp if latest_bp else 80,
            heart_rate=latest_bp.heart_rate if latest_bp else None,
            tot_chol=risk_profile.tot_chol,
            glucose=risk_profile.glucose,
        )

    def to_model_input(self):
        return {
            "age": self.age,
            "male": self.male,
            "BMI": self.bmi,
            "currentSmoker": self.current_smoker,
            "cigsPerDay": self.cigs_per_day,
            "BPMeds": self.bp_meds,
            "diabetes": self.diabetes,
            "sysBP": self.sys_bp,
            "diaBP": self.dia_bp,
            "heartRate": self.heart_rate,
            "totChol": self.tot_chol,
            "glucose": self.glucose,
        }

    def to_persistence_payload(self, *, model_state, prediction_run_key):
        return {
            **self.to_model_input(),
            "_tot_chol_filled": self.tot_chol is not None,
            "_glucose_filled": self.glucose is not None,
            MODEL_STATE_SNAPSHOT_KEY: model_state,
            PREDICTION_RUN_KEY: prediction_run_key,
        }
