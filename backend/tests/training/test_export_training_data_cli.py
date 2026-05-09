from contextlib import contextmanager
from pathlib import Path

import scripts.export_training_data as export_training_data
from training.ml_schema import EXPORT_DATASET
from training.config import DATASETS_DIR


class FakeApp:
    def __init__(self):
        self.context_entries = 0

    @contextmanager
    def app_context(self):
        self.context_entries += 1
        yield


def test_parse_args_defaults_to_training_dataset_export_path():
    args = export_training_data.parse_args([])

    assert args.output == DATASETS_DIR / EXPORT_DATASET
    assert args.recent_bp_count is None


def test_local_export_writes_csv_with_app_context_and_recent_count(tmp_path):
    app = FakeApp()
    overrides = []

    def fake_app_factory(config_override):
        overrides.append(config_override)
        return app

    def fake_exporter():
        return "age,Risk\n56,0\n"

    output_path = tmp_path / "nested" / "training_data_export.csv"
    result = export_training_data.run_local_training_export(
        output_path=output_path,
        recent_bp_count=7,
        app_factory=fake_app_factory,
        exporter=fake_exporter,
    )

    assert result == output_path.resolve()
    assert output_path.read_text(encoding="utf-8") == "age,Risk\n56,0\n"
    assert app.context_entries == 1
    assert overrides == [
        {
            "INIT_ADMIN_ON_STARTUP": False,
            "EXPORT_RECENT_BP_COUNT": 7,
        }
    ]


def test_main_reports_output_path(monkeypatch, tmp_path, capsys):
    output_path = tmp_path / "training.csv"
    calls = []

    def fake_run_local_training_export(*, output_path, recent_bp_count):
        calls.append((output_path, recent_bp_count))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("age,Risk\n", encoding="utf-8")
        return output_path.resolve()

    monkeypatch.setattr(
        export_training_data,
        "run_local_training_export",
        fake_run_local_training_export,
    )

    export_training_data.main(
        ["--output", str(output_path), "--recent-bp-count", "9"]
    )

    assert calls == [(output_path, 9)]
    assert str(output_path.resolve()) in capsys.readouterr().out

