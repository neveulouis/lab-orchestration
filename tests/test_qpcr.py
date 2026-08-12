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
            [1, 2, 3],
            id="mixed",
        ),
        pytest.param(
            ["denaturation", "denaturation", "denaturation"],
            [],
            id="denaturation_only",
        ),
        pytest.param(
            [
                "initial_denaturation",
                "denaturation",
                "annealing",
                "extension",
            ],
            [1],
            id="one_full_cycle",
        ),
    ],
)
def test_counter_bumps_on_denaturation_and_writes_on_extension(
    operations: list[str], expected: list[int]
) -> None:
    thermocycler = Thermocycler()
    for operation in operations:
        thermocycler.invoke(operation)
    assert list(thermocycler.readings) == expected


def test_midpoint_is_half_the_plateau() -> None:
    thermocycler = Thermocycler()
    for _ in range(CURVE_MIDPOINT_CYCLE):
        thermocycler.invoke("denaturation")
        thermocycler.invoke("extension")
    assert thermocycler.readings[CURVE_MIDPOINT_CYCLE] == CURVE_PLATEAU / 2


def test_readings_increase_with_cycle_number() -> None:
    thermocycler = Thermocycler()
    for _ in range(CURVE_MIDPOINT_CYCLE + 5):
        thermocycler.invoke("denaturation")
        thermocycler.invoke("extension")
    assert (
        thermocycler.readings[CURVE_MIDPOINT_CYCLE - 5]
        < thermocycler.readings[CURVE_MIDPOINT_CYCLE]
        < thermocycler.readings[CURVE_MIDPOINT_CYCLE + 5]
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
