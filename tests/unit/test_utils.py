from simpleval.utilities.files import is_subpath

def test_is_subpath_child():
    path = '/parent/child'
    parent = '/parent'

    assert is_subpath(path, parent) is True

def test_is_subpath_not_child():
    path = '/some-dir/child'
    parent = '/parent'

    assert is_subpath(path, parent) is False

def test_is_subpath_same_path():
    path = '/parent'
    parent = '/parent'

    assert is_subpath(path, parent) is False
