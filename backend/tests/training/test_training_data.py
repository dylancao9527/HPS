from training.ml_schema import BASE_TRAINING_DATASET, EXPORT_DATASET
from training import data


def test_prepare_lgbm_data_allows_missing_export_dataset(monkeypatch, tmp_path, capsys):
    base_path = tmp_path / BASE_TRAINING_DATASET
    base_path.write_text(
        "\n".join(
            [
                "male,age,currentSmoker,cigsPerDay,BPMeds,diabetes,totChol,sysBP,diaBP,BMI,heartRate,glucose,Risk",
                "1,56,0,0,0,0,210,142,91,27.3,78,105,1",
                "0,43,0,0,0,0,188,118,76,22.5,72,92,0",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(data, "DATASETS_DIR", tmp_path)

    X, y, _, _, dataset_summary = data.prepare_lgbm_data(random_seed=7)

    assert not (tmp_path / EXPORT_DATASET).exists()
    assert len(X) == 2
    assert len(y) == 2
    assert dataset_summary["export_rows"] == 0
    assert dataset_summary["label_source_summary"] == {"base_dataset": 2}
    output = capsys.readouterr().out
    assert f"{EXPORT_DATASET} 不存在，仅使用基础数据集训练" in output


def test_prepare_lgbm_data_uses_runtime_label_and_bp_meds_policy(monkeypatch, tmp_path):
    (tmp_path / BASE_TRAINING_DATASET).write_text(
        "\n".join(
            [
                "male,age,currentSmoker,cigsPerDay,BPMeds,diabetes,totChol,sysBP,diaBP,BMI,heartRate,glucose,Risk",
                "1,56,0,0,1,0,210,142,91,27.3,78,105,1",
                "0,43,0,0,0,0,188,118,76,22.5,72,92,0",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / EXPORT_DATASET).write_text(
        "\n".join(
            [
                "male,age,currentSmoker,cigsPerDay,BPMeds,diabetes,totChol,sysBP,diaBP,BMI,heartRate,glucose,labelSource,Risk",
                "1,66,1,5,1,0,220,150,95,28.1,80,110,diagnosis,1",
                "0,48,0,0,0,0,190,120,78,23.0,70,90,rule,0",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(data, "DATASETS_DIR", tmp_path)

    X, _, _, _, dataset_summary = data.prepare_lgbm_data(
        random_seed=7,
        bp_meds_policy="observed",
        label_mode="diagnosis_only",
    )

    assert dataset_summary["export_rows"] == 1
    assert dataset_summary["bp_meds_policy"] == "observed"
    assert dataset_summary["label_mode"] == "diagnosis_only"
    assert dataset_summary["label_source_summary"] == {
        "base_dataset": 2,
        "diagnosis": 1,
    }
    assert 1 in set(X["BPMeds"].astype("Int64").dropna().astype(int))
