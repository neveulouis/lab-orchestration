import pytest

from lab_orchestration.qpcr import (
    CURVE_MIDPOINT_CYCLE,
    CURVE_PLATEAU,
    Thermocycler,
)


@pytest.mark.parametrize(
    ("operations", "expected"),
    [
        pytest.param(
            [
                "denaturation",
                "extension",
                "denaturation",
                "extension",
                "denaturation",
                "extension",
            ],
            [False, True, False, True, False, True],
            id="mixed",
        ),
        pytest.param(
            ["denaturation", "denaturation", "denaturation"],
            [False, False, False],
            id="denaturation_only",
        ),
        pytest.param(
            [
                "initial_denaturation",
                "denaturation",
                "annealing",
                "extension",
            ],
            [False, False, False, True],
            id="one_full_cycle",
        ),
    ],
)
def test_readings_return_on_extension(
    operations: list[str], expected: list[bool]
) -> None:
    thermocycler = Thermocycler()
    readings = [thermocycler.invoke(operation) is not None for operation in operations]
    assert readings == expected


def test_midpoint_is_half_the_plateau() -> None:
    thermocycler = Thermocycler()
    for _ in range(CURVE_MIDPOINT_CYCLE):
        thermocycler.invoke("denaturation")
        reading = thermocycler.invoke("extension")
    assert reading == CURVE_PLATEAU / 2


def test_readings_increase_with_cycle_number() -> None:
    thermocycler = Thermocycler()
    readings = []
    midpoint_index = CURVE_MIDPOINT_CYCLE - 1  # cycle n is at index n-1
    for _ in range(CURVE_MIDPOINT_CYCLE + 5):
        thermocycler.invoke("denaturation")
        data = thermocycler.invoke("extension")
        if data is not None:
            readings.append(data)
    assert (
        readings[midpoint_index - 5]
        < readings[midpoint_index]
        < readings[midpoint_index + 5]
    )


def test_unrecognised_operation_raises_error() -> None:
    thermocycler = Thermocycler()
    with pytest.raises(ValueError, match="acquire"):
        thermocycler.invoke("acquire")


def test_substring_of_recognised_operation_raises_error() -> None:
    thermocycler = Thermocycler()
    with pytest.raises(ValueError, match="nat"):
        thermocycler.invoke("nat")


def test_extension_at_cycle_0_raises_error() -> None:
    thermocycler = Thermocycler()
    with pytest.raises(RuntimeError, match="before any denaturation"):
        thermocycler.invoke("extension")
