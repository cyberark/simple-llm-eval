from simpleval.evaluation.judges import judge_utils
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


def test_verify_env_var_set(monkeypatch):
    monkeypatch.setenv('TEST_ENV_VAR', '1')
    # Should not raise
    judge_utils.verify_env_var('TEST_ENV_VAR')


def test_verify_env_var_not_set(monkeypatch):
    monkeypatch.delenv('TEST_ENV_VAR', raising=False)
    with pytest.raises(ValueError):
        judge_utils.verify_env_var('TEST_ENV_VAR')


def test_bedrock_preliminary_checks_success(mocker):
    mock_sts = mocker.Mock()
    mock_sts.get_caller_identity.return_value = {'UserId': 'test'}
    mocker.patch('boto3.client', return_value=mock_sts)
    mock_session = mocker.Mock()
    mock_session.region_name = 'us-east-1'
    mocker.patch('boto3.session.Session', return_value=mock_session)
    judge_utils.bedrock_preliminary_checks()


def test_bedrock_preliminary_checks_sts_failure(mocker):
    mock_sts = mocker.Mock()
    mock_sts.get_caller_identity.side_effect = Exception('fail')
    mocker.patch('boto3.client', return_value=mock_sts)
    mock_session = mocker.Mock()
    mock_session.region_name = 'us-east-1'
    mocker.patch('boto3.session.Session', return_value=mock_session)
    with pytest.raises(RuntimeError, match='Failed to validate sts credentials.'):
        judge_utils.bedrock_preliminary_checks()


def test_bedrock_preliminary_checks_region_failure(mocker):
    mock_sts = mocker.Mock()
    mock_sts.get_caller_identity.return_value = {'UserId': 'test'}
    mocker.patch('boto3.client', return_value=mock_sts)
    mock_session = mocker.Mock()
    mock_session.region_name = None
    mocker.patch('boto3.session.Session', return_value=mock_session)
    with pytest.raises(RuntimeError, match='Failed to retrieve AWS region.'):
        judge_utils.bedrock_preliminary_checks()
