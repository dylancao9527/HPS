import numpy as np
import pandas as pd

from training.metrics import _build_threshold_candidates, find_best_threshold


class FakeModel:
    def __init__(self, scores):
        self._scores = np.asarray(scores, dtype=float)

    def predict(self, X):
        return self._scores[: len(X)]


def test_threshold_candidates_include_edges_around_observed_scores():
    candidates = _build_threshold_candidates([0.2, 0.8])

    assert candidates[0] < 0.2
    assert candidates[1] == 0.5
    assert candidates[2] > 0.8


def test_recall_priority_can_select_full_recall_boundary():
    model = FakeModel([0.2, 0.8])
    X = pd.DataFrame({"x": [1, 2]})
    y = pd.Series([1, 0])

    result = find_best_threshold(
        model,
        X,
        y,
        strategy="recall_priority",
        min_recall=1.0,
    )

    assert result["recall"] == 1.0
    assert result["threshold"] < 0.2
    assert result["recall_constraint_satisfied"] is True
