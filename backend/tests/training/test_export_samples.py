from types import SimpleNamespace

from training import export_samples


class FakeField:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return ("eq", self.name, other)

    def __ge__(self, other):
        return ("ge", self.name, other)

    def desc(self):
        return ("desc", self.name)


class FakeBPQuery:
    def __init__(self, records_by_user, *, user_id=None, high_only=False, limit_count=None):
        self.records_by_user = records_by_user
        self.user_id = user_id
        self.high_only = high_only
        self.limit_count = limit_count

    def filter_by(self, **kwargs):
        return FakeBPQuery(
            self.records_by_user,
            user_id=kwargs.get("user_id", self.user_id),
            high_only=self.high_only,
            limit_count=self.limit_count,
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
            self.records_by_user,
            user_id=user_id,
            high_only=high_only,
            limit_count=self.limit_count,
        )

    def order_by(self, *args):
        return self

    def limit(self, count):
        return FakeBPQuery(
            self.records_by_user,
            user_id=self.user_id,
            high_only=self.high_only,
            limit_count=count,
        )

    def all(self):
        records = list(self.records_by_user.get(self.user_id, []))
        if self.limit_count is not None:
            return records[: self.limit_count]
        return records

    def count(self):
        records = self.records_by_user.get(self.user_id, [])
        if self.high_only:
            return sum(
                1 for record in records if record.systolic_bp >= 140 or record.diastolic_bp >= 90
            )
        return len(records)


class FakeBPRecord:
    user_id = FakeField("user_id")
    systolic_bp = FakeField("systolic_bp")
    diastolic_bp = FakeField("diastolic_bp")
    recorded_at = FakeField("recorded_at")
    query = FakeBPQuery({})


def _install_bp_records(monkeypatch, records_by_user):
    FakeBPRecord.query = FakeBPQuery(records_by_user)
    monkeypatch.setattr(export_samples, "or_", lambda *args: ("or", args))
    return FakeBPRecord


def _bp(sys, dia, heart_rate=72):
    return SimpleNamespace(systolic_bp=sys, diastolic_bp=dia, heart_rate=heart_rate)


def _profile(
    *,
    diagnosis=None,
    complete=True,
    current_smoker=0,
    cigs_per_day=8,
    bp_meds=1,
    diabetes=0,
    tot_chol=190,
    glucose=96,
):
    return SimpleNamespace(
        profile_complete=complete,
        diagnosis=diagnosis,
        age=56,
        male=1,
        bmi=24.2,
        current_smoker=current_smoker,
        cigs_per_day=cigs_per_day,
        bp_meds=bp_meds,
        diabetes=diabetes,
        tot_chol=tot_chol,
        glucose=glucose,
    )


def _user(user_id, profile):
    return SimpleNamespace(id=user_id, profile=profile)


def test_recent_bp_averages_use_recent_window_and_available_heart_rates(monkeypatch):
    bp_record_model = _install_bp_records(
        monkeypatch,
        {
            1: [
                _bp(150, 95, 80),
                _bp(130, 85, None),
                _bp(120, 78, 70),
            ]
        },
    )

    result = export_samples.calculate_recent_bp_averages(
        1,
        2,
        bp_record_model=bp_record_model,
    )

    assert result == {
        "systolic": 140.0,
        "diastolic": 90.0,
        "heart_rate": 80.0,
        "count_used": 2,
    }


def test_export_sample_uses_diagnosis_label_and_zeroes_non_smoker_cigs(monkeypatch):
    bp_record_model = _install_bp_records(
        monkeypatch,
        {1: [_bp(132, 82), _bp(134, 84), _bp(136, 86)]},
    )

    sample = export_samples.build_training_export_sample(
        _user(1, _profile(diagnosis="No", current_smoker=0, cigs_per_day=8)),
        3,
        bp_record_model=bp_record_model,
    )

    assert sample.label == 0
    assert sample.label_source == "diagnosis"
    assert sample.row["labelSource"] == "diagnosis"
    assert sample.row["Risk"] == 0
    assert sample.row["cigsPerDay"] == 0
    assert sample.row["sysBP"] == 134.0


def test_export_sample_uses_rule_label_and_preserves_missing_fields(monkeypatch):
    bp_record_model = _install_bp_records(
        monkeypatch,
        {2: [_bp(145, 91), _bp(142, 88), _bp(139, 92), _bp(128, 80)]},
    )

    sample = export_samples.build_training_export_sample(
        _user(
            2,
            _profile(
                diagnosis=None,
                current_smoker=1,
                cigs_per_day="",
                tot_chol=None,
                glucose=None,
            ),
        ),
        4,
        bp_record_model=bp_record_model,
    )

    assert sample.label == 1
    assert sample.label_source == "rule"
    assert sample.row["labelSource"] == "rule"
    assert sample.row["cigsPerDay"] is None
    assert sample.row["totChol"] is None
    assert sample.row["glucose"] is None


def test_export_sample_keeps_optional_risk_factors_missing_when_minimum_profile_is_complete(monkeypatch):
    bp_record_model = _install_bp_records(
        monkeypatch,
        {5: [_bp(132, 82), _bp(134, 84), _bp(136, 86)]},
    )

    sample = export_samples.build_training_export_sample(
        _user(
            5,
            _profile(
                diagnosis="No",
                current_smoker=None,
                cigs_per_day=None,
                bp_meds=None,
                diabetes=None,
                tot_chol=None,
                glucose=None,
            ),
        ),
        3,
        bp_record_model=bp_record_model,
    )

    assert sample.label == 0
    assert sample.label_source == "diagnosis"
    assert sample.row["currentSmoker"] is None
    assert sample.row["cigsPerDay"] is None
    assert sample.row["BPMeds"] is None
    assert sample.row["diabetes"] is None
    assert sample.row["totChol"] is None
    assert sample.row["glucose"] is None


def test_export_sample_skips_incomplete_missing_bp_and_insufficient_rule_label(monkeypatch):
    bp_record_model = _install_bp_records(
        monkeypatch,
        {
            3: [],
            4: [_bp(125, 80), _bp(126, 82)],
        },
    )

    incomplete = export_samples.build_training_export_sample(
        _user(1, _profile(complete=False)),
        3,
        bp_record_model=bp_record_model,
    )
    missing_bp = export_samples.build_training_export_sample(
        _user(3, _profile(diagnosis=None)),
        3,
        bp_record_model=bp_record_model,
    )
    insufficient_rule = export_samples.build_training_export_sample(
        _user(4, _profile(diagnosis=None)),
        3,
        bp_record_model=bp_record_model,
    )

    assert incomplete is None
    assert missing_bp is None
    assert insufficient_rule is None


def test_export_batch_uses_precomputed_bp_projection_without_per_user_queries(monkeypatch):
    class ExplodingQuery:
        def filter_by(self, **kwargs):
            raise AssertionError("batch export should not query BP per user")

        def filter(self, *conditions):
            raise AssertionError("batch export should not query BP per user")

    class ExplodingBPRecord:
        query = ExplodingQuery()

    projections = [
        export_samples.TrainingExportProjection(
            user_id=1,
            profile=SimpleNamespace(diagnosis="No"),
            risk_factor_profile=_profile(current_smoker=0, cigs_per_day=8),
            recent_bp={
                "systolic": 132,
                "diastolic": 82,
                "heart_rate": 71,
                "count_used": 5,
            },
            total_bp_count=5,
            high_bp_count=0,
        ),
        export_samples.TrainingExportProjection(
            user_id=2,
            profile=SimpleNamespace(diagnosis=None),
            risk_factor_profile=_profile(),
            recent_bp={
                "systolic": 145,
                "diastolic": 91,
                "heart_rate": None,
                "count_used": 5,
            },
            total_bp_count=5,
            high_bp_count=3,
        ),
    ]

    batch = export_samples.build_training_export_batch(
        projections,
        total_users=3,
        bp_record_model=ExplodingBPRecord,
    )

    assert batch.total_users == 3
    assert [sample.label for sample in batch.samples] == [0, 1]
    assert [sample.label_source for sample in batch.samples] == ["diagnosis", "rule"]
    assert batch.samples[0].row["cigsPerDay"] == 0


def test_export_batch_keeps_optional_risk_factor_projection_fields_missing():
    projections = [
        export_samples.TrainingExportProjection(
            user_id=6,
            profile=SimpleNamespace(diagnosis="No"),
            risk_factor_profile=_profile(
                current_smoker=None,
                cigs_per_day=None,
                bp_meds=None,
                diabetes=None,
                tot_chol=None,
                glucose=None,
            ),
            recent_bp={
                "systolic": 132,
                "diastolic": 82,
                "heart_rate": 71,
                "count_used": 5,
            },
            total_bp_count=5,
            high_bp_count=0,
        )
    ]

    batch = export_samples.build_training_export_batch(
        projections,
        total_users=1,
    )

    assert len(batch.samples) == 1
    assert batch.samples[0].row["currentSmoker"] is None
    assert batch.samples[0].row["BPMeds"] is None
    assert batch.samples[0].row["diabetes"] is None
    assert batch.samples[0].row["totChol"] is None
    assert batch.samples[0].row["glucose"] is None
