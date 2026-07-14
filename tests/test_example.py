import pytest

from lab_orchestration.example import Example


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, -2, -3),
    ],
)
def test_add(a: int, b: int, expected: int) -> None:

    ex = Example()
    result = ex.add(a, b)
    assert result == expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (2, 1, 1),
        (0, 0, 0),
        (-1, -2, 1),
    ],
)
def test_subtract(a: int, b: int, expected: int) -> None:

    ex = Example()
    result = ex.subtract(a, b)
    assert result == expected
