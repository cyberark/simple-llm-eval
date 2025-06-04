import builtins
import pytest
from unittest.mock import patch
from simpleval.commands.reporting.utils import print_table


@pytest.fixture
def capture_print(monkeypatch):
    """Fixture to capture printed output."""
    output = []
    monkeypatch.setattr(builtins, 'print', output.append)
    return output


def test_print_table_normal(capture_print):
    """Test normal table printing with heavy_grid format."""
    class DummyTabulate:
        def __init__(self):
            self.calls = []
        def __call__(self, table, headers=None, tablefmt=None):
            self.calls.append((table, headers, tablefmt))
            return 'formatted-table'
    dummy_tabulate = DummyTabulate()
    with patch('simpleval.commands.reporting.utils.tabulate', dummy_tabulate):
        print_table([[1, 2]], headers=['a', 'b'])
        assert capture_print == ['formatted-table']
        assert dummy_tabulate.calls[0] == ([[1, 2]], ['a', 'b'], 'heavy_grid')


def test_print_table_unicodeerror(capture_print):
    """Test fallback when tabulate raises UnicodeError."""
    def fake_tabulate(table, headers=None, tablefmt=None):
        if tablefmt == 'heavy_grid':
            raise UnicodeError('fake unicode error')
        return 'fallback-table'
    with patch('simpleval.commands.reporting.utils.tabulate', fake_tabulate):
        print_table([[1, 2]], headers=['a', 'b'])
        assert capture_print == ['fallback-table']
