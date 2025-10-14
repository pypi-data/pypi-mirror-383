import pytest

from izifizi.module import function


@pytest.mark.parametrize(("x", "y", "expected_result"), [(2, 3, 6), (4, 5, 20), (0, 10, 0)])
def test_function(x: int, y: int, expected_result: int) -> None:
    assert expected_result == function(x, y)
