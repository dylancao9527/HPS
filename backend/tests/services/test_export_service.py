import csv
import io
from types import SimpleNamespace

from services import export_service
from training import export_samples


class FakeUserQuery:
    def __init__(self, users):
        self.users = users

    def all(self):
        return self.users


class ExplodingUserQuery:
    def all(self):
        raise AssertionError("training export should use batch projections, not User.query.all()")


class FakeField:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return ("eq", self.name, other)

    def __ge__(self, other):
        return ("ge", self.name, other)


class FakeBPQuery:
    def __init__(self, total_counts, high_counts, user_id=None, high_only=False):
        self.total_counts = total_counts
        self.high_counts = high_counts
        self.user_id = user_id
        self.high_only = high_only

    def filter_by(self, **kwargs):
        return FakeBPQuery(
            self.total_counts,
            self.high_counts,
            user_id=kwargs.get("user_id", self.user_id),
            high_only=self.high_only,
        )

    def filter(self, *conditions):
        user_id = self.user_id
        high_only = self.high_only
        for condition in conditions:
            if isinstance(condition, tuple) and condition[:2] == ("eq", "user_id"):
                user_id = condition[2]
            if isinstance(condition, tuple) and condition[0] == "or":
                high_only = True
        return FakeBPQuery(
            self.total_counts,
            self.high_counts,
            user_id=user_id,
            high_only=high_only,
        )

    def count(self):
        if self.high_only:
            return self.high_counts.get(self.user_id, 0)
        return self.total_counts.get(self.user_id, 0)


class FakeBPRecord:
    user_id = FakeField("user_id")
    systolic_bp = FakeField("systolic_bp")
    diastolic_bp = FakeField("diastolic_bp")
    query = None


def _profile(*, diagnosis=None, smoker=0, complete=True):
    return SimpleNamespace(
        profile_complete=complete,
        diagnosis=diagnosis,
        age=56,
        male=1,
        bmi=24.2,
        current_smoker=smoker,
        cigs_per_day=8,
        bp_meds=1,
        diabetes=0,
        tot_chol=190,
        glucose=96,
    )


def _user(user_id, profile):
    return SimpleNamespace(id=user_id, profile=profile)


def _install_export_fakes(monkeypatch):
    users = [
        _user(1, _profile(diagnosis="Yes")),
        _user(2, _profile(diagnosis="No")),
        _user(3, _profile(diagnosis=None)),
        _user(4, _profile(diagnosis=None)),
    ]
    monkeypatch.setattr(
        export_service,
        "User",
        SimpleNamespace(query=FakeUserQuery(users)),
        raising=False,
    )
    FakeBPRecord.query = FakeBPQuery(
        total_counts={1: 5, 2: 5, 3: 5, 4: 2},
        high_counts={1: 0, 2: 0, 3: 3, 4: 0},
    )
    monkeypatch.setattr(export_samples, "BPRecord", FakeBPRecord)
    monkeypatch.setattr(export_samples, "or_", lambda *args: ("or", args))
    monkeypatch.setattr(
        export_samples,
        "calculate_recent_bp_averages",
        lambda user_id, recent_count, **kwargs: {
            "systolic": 132 + user_id,
            "diastolic": 82 + user_id,
            "heart_rate": 70 + user_id,
            "count_used": recent_count,
        },
    )

    def load_fake_batch(recent_count):
        samples = [
            sample
            for sample in export_samples.iter_exportable_training_samples(
                users,
                recent_count,
                bp_record_model=FakeBPRecord,
            )
            if sample is not None
        ]
        return export_samples.TrainingExportBatch(
            total_users=len(users),
            samples=samples,
        )

    monkeypatch.setattr(export_service, "load_training_export_batch", load_fake_batch)


def test_export_training_csv_preserves_label_sources(monkeypatch):
    _install_export_fakes(monkeypatch)

    csv_text = export_service.export_training_csv()
    rows = list(csv.DictReader(io.StringIO(csv_text)))

    assert len(rows) == 3
    assert rows[0]["Risk"] == "1"
    assert rows[0]["labelSource"] == "diagnosis"
    assert rows[1]["Risk"] == "0"
    assert rows[1]["labelSource"] == "diagnosis"
    assert rows[2]["Risk"] == "1"
    assert rows[2]["labelSource"] == "rule"
    assert rows[0]["sysBP"] == "133"
    assert rows[2]["heartRate"] == "73"


def test_training_export_stats_match_csv_sample_counts(monkeypatch):
    _install_export_fakes(monkeypatch)

    csv_rows = list(csv.DictReader(io.StringIO(export_service.export_training_csv())))
    stats = export_service.get_training_export_stats()

    assert len(csv_rows) == stats["exportable_samples"]
    assert stats == {
        "recent_bp_avg_count": 5,
        "exportable_samples": 3,
        "skipped_users": 1,
        "positive_samples": 2,
        "negative_samples": 1,
        "positive_ratio": 0.6667,
        "diagnosis_labeled_samples": 2,
        "rule_labeled_samples": 1,
    }


def test_training_export_service_uses_batch_projection_source(monkeypatch):
    batch = export_samples.TrainingExportBatch(
        total_users=2,
        samples=[
            export_samples.TrainingExportSample(
                row={
                    "male": 1,
                    "age": 56,
                    "currentSmoker": 0,
                    "cigsPerDay": 0,
                    "BPMeds": 1,
                    "diabetes": 0,
                    "totChol": 190,
                    "sysBP": 133,
                    "diaBP": 83,
                    "BMI": 24.2,
                    "heartRate": 71,
                    "glucose": 96,
                    "Risk": 1,
                    "labelSource": "rule",
                },
                label=1,
                label_source="rule",
            )
        ],
    )
    monkeypatch.setattr(
        export_service,
        "User",
        SimpleNamespace(query=ExplodingUserQuery()),
        raising=False,
    )
    monkeypatch.setattr(export_service, "load_training_export_batch", lambda _: batch)

    rows = list(csv.DictReader(io.StringIO(export_service.export_training_csv())))
    stats = export_service.get_training_export_stats()

    assert rows[0]["Risk"] == "1"
    assert stats["exportable_samples"] == 1
    assert stats["skipped_users"] == 1
