from dataclasses import dataclass

from models import PredictionRecord


@dataclass
class CompactPredictionRows:
    prediction_record: PredictionRecord
    prophet_prediction: object | None = None
