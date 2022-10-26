
def test_func():
    import os
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    assert 1 == 2