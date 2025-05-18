from pathlib import Path

import pytest

from simpleval.evaluation.judges.judge_utils import get_metrics_dir, get_metrics_models_root


def test_get_metrics_root():
    path = Path(get_metrics_models_root())
    expected_path_suffix = Path('simpleval/evaluation/metrics/models')
    assert path.parts[-len(expected_path_suffix.parts):] == expected_path_suffix.parts
    assert path.exists()
    assert path.is_dir()


def test_get_metrics_dir():
    metric_model = 'test_metric'
    path = Path(get_metrics_dir(metric_model))
    expected_path_suffix = Path('simpleval/evaluation/metrics/models/test_metric')
    assert path.parts[-len(expected_path_suffix.parts):] == expected_path_suffix.parts
    assert path.exists()
    assert path.is_dir()


def test_get_metrics_dir_not_found():
    with pytest.raises(FileNotFoundError):
        get_metrics_dir('non_existent_metric')
