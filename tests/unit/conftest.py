import pytest

@pytest.fixture
def sample_c_struct():
    return """
    struct Point {
        int x;
        int y;
        double z;
    };
    """

@pytest.fixture
def sample_nested_struct():
    return """
    struct Line {
        struct Point start;
        struct Point end;
    };
    """ 