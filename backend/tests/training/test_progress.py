from io import StringIO

import pytest

from training.progress import TrainingProgress


def test_training_progress_outputs_stage_status_and_key_metrics():
    stream = StringIO()
    progress = TrainingProgress(total_steps=2, stream=stream)

    progress.start_step("数据准备", detail="seed=7")
    progress.finish_step(rows=123, pos="38.2%")
    progress.start_step("官方调优", detail="LightGBMTunerCV")
    progress.metric(cv_auc=0.93841)
    progress.finish_step(best_iteration=312)

    output = stream.getvalue()
    assert "1/2 数据准备  running  seed=7" in output
    assert "1/2 数据准备  done  rows=123 pos=38.2%" in output
    assert "2/2 官方调优  running  LightGBMTunerCV" in output
    assert "2/2 官方调优  info  cv_auc=0.9384" in output
    assert "2/2 官方调优  done  best_iteration=312" in output
    assert "lambda_l1" not in output
    assert "[1]" not in output


def test_training_progress_rejects_finish_without_active_step():
    progress = TrainingProgress(total_steps=1, stream=StringIO())

    with pytest.raises(RuntimeError, match="finish_step called before start_step"):
        progress.finish_step()
