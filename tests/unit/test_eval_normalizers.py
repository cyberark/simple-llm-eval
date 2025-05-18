import pytest

from simpleval.evaluation.metrics.normalizers import get_normalize_score, get_score_interval


def test_normalize_score_valid():
    items = ['low', 'medium', 'high']
    assert get_normalize_score('low', items) == 0.0
    assert get_normalize_score('medium', items) == 0.5
    assert get_normalize_score('high', items) == 1.0


def test_normalize_score_invalid_value():
    items = ['low', 'medium', 'high']
    with pytest.raises(ValueError,
                       match=r'Value `invalid` not found in the list of items for normalization `\[\'low\', \'medium\', \'high\'\]`.'):
        get_normalize_score('invalid', items)


def test_normalize_score_single_item():
    items = ['only']
    assert get_normalize_score('only', items) == 0.0


def test_normalize_score_empty_list():
    items = []
    with pytest.raises(ValueError, match=r'Value `any` not found in the list of items for normalization `\[\]`.'):
        get_normalize_score('any', items)


def test_score_interval_valid():
    assert get_score_interval(2) == 1.0
    assert get_score_interval(3) == 0.5
    assert get_score_interval(6) == 0.2


def test_score_interval_invalid():
    with pytest.raises(ValueError, match=r'Number of items must be greater than 1 to calculate intervals.'):
        get_score_interval(1)
    with pytest.raises(ValueError, match=r'Number of items must be greater than 1 to calculate intervals.'):
        get_score_interval(0)
