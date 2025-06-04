import builtins
from simpleval.commands.reporting.utils import print_table

class DummyLogger:
    def __init__(self):
        self.debug_calls = []
    def debug(self, msg):
        self.debug_calls.append(msg)

class DummyTabulate:
    def __init__(self, raise_unicode=False):
        self.raise_unicode = raise_unicode
        self.calls = []
    def __call__(self, table, headers=None, tablefmt=None):
        self.calls.append((table, headers, tablefmt))
        if self.raise_unicode and tablefmt == 'heavy_grid':
            raise UnicodeError('dummy')
        return 'formatted-table'

def test_print_table_normal(monkeypatch):
    output = []
    monkeypatch.setattr(builtins, 'print', output.append)
    dummy_tabulate = DummyTabulate()
    monkeypatch.setattr('simpleval.commands.reporting.utils.tabulate', dummy_tabulate)
    print_table([[1, 2]], headers=['a', 'b'])
    assert output == ['formatted-table']
    assert dummy_tabulate.calls[0] == ([[1, 2]], ['a', 'b'], 'heavy_grid')


def test_print_table_unicodeerror(monkeypatch):
    # Patch tabulate to raise UnicodeError on heavy_grid, else return a string
    def fake_tabulate(table, headers=None, tablefmt=None):
        if tablefmt == 'heavy_grid':
            raise UnicodeError("fake unicode error")
        return "fallback-table"
    monkeypatch.setattr('simpleval.commands.reporting.utils.tabulate', fake_tabulate)
    output = []
    monkeypatch.setattr(builtins, 'print', output.append)
    print_table([[1, 2]], headers=['a', 'b'])
    # Should print fallback-table after catching the error
    assert output == ["fallback-table"]
